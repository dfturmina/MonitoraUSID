"""
Provedor de Telemetria via SSH (SshMetricsProvider)
==================================================
Coleta de forma assíncrona métricas de SO (CPU, RAM em GB/%, Disco em GB/%,
conexões TCP estabelecidas) e estado de serviços systemd, containers
Docker/Podman, processos e webapps Tomcat em hosts sem Zabbix Agent ativo.
"""

import asyncio
import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple

from ..interfaces.host_metrics_provider_interface import HostMetricsProviderInterface

_SAFE_NAME_RE = re.compile(r"^[a-zA-Z0-9_@.\-]+$")
_SAFE_TARGET_RE = re.compile(r"^[a-zA-Z0-9_@.\-]+$")


def _round_commercial_ram_gb(raw_gb: float) -> float:
    """Arredonda RAM total para potências comerciais típicas de VM."""
    for target, low, high in (
        (2.0, 1.7, 2.2),
        (4.0, 3.6, 4.2),
        (8.0, 7.4, 8.2),
        (16.0, 15.2, 16.4),
        (32.0, 31.0, 32.8),
        (64.0, 62.0, 65.5),
    ):
        if low <= raw_gb <= high:
            return target
    return round(raw_gb, 1)


def _offline_metrics(host_id: str, error_msg: str) -> Dict[str, Any]:
    """Retorna estrutura padrão de host inacessível via SSH."""
    return {
        "source": "SSH",
        "available": False,
        "host_id": host_id,
        "name": host_id,
        "status": "OFFLINE",
        "cpu_usage": 0.0,
        "memory_used_gb": 0.0,
        "memory_total_gb": 0.0,
        "memory_usage": 0.0,
        "disk_used_gb": 0.0,
        "disk_total_gb": 0.0,
        "disk_usage": 0.0,
        "active_connections": 0,
        "ping_latency_ms": 0,
        "service_checks": {},
        "has_critical_service_failure": False,
        "error": error_msg,
    }


def _sanitize_names(values: Any) -> List[str]:
    """Filtra nomes seguros de serviços, containers ou processos."""
    if not isinstance(values, list):
        return []
    return [str(v).strip() for v in values if isinstance(v, str) and _SAFE_NAME_RE.match(v.strip())]


def _build_remote_probe_script(servicos_config: Optional[Dict[str, Any]]) -> str:
    """Monta script shell de rodada única para extrair métricas e serviços via SSH."""
    cfg = servicos_config or {}
    systemd_units = _sanitize_names(cfg.get("systemd"))
    containers = _sanitize_names(cfg.get("containers"))
    processes = _sanitize_names(cfg.get("processes"))
    tomcat_app = cfg.get("tomcat_app")
    if not isinstance(tomcat_app, str) or not _SAFE_NAME_RE.match(tomcat_app.strip()):
        tomcat_app = None
    else:
        tomcat_app = tomcat_app.strip()

    lines = [
        'LC_ALL=C',
        'echo "HOSTNAME=$(hostname)"',
        # CPU sample from /proc/stat over 200ms
        r'''read -r _ u1 n1 s1 i1 w1 q1 sq1 st1 _ < /proc/stat
sleep 0.2
read -r _ u2 n2 s2 i2 w2 q2 sq2 st2 _ < /proc/stat
tot1=$((u1+n1+s1+i1+w1+q1+sq1+st1))
tot2=$((u2+n2+s2+i2+w2+q2+sq2+st2))
dt=$((tot2-tot1))
di=$((i2+w2-i1-w1))
awk -v dt="$dt" -v di="$di" 'BEGIN { if (dt > 0) printf "CPU=%.1f\n", (dt - di) * 100.0 / dt; else print "CPU=0.0" }' ''',
        # Memory from /proc/meminfo
        r'''awk '/^MemTotal:/ {t=$2} /^MemAvailable:/ {a=$2} /^MemFree:/ {f=$2} /^Buffers:/ {b=$2} /^Cached:/ {c=$2} END { if (a == 0) a = f + b + c; printf "MEM_TOTAL_KB=%d\nMEM_AVAIL_KB=%d\n", t, a }' /proc/meminfo''',
        # Root disk usage in KB
        r'''df -Pk / | awk 'NR==2 {printf "DISK_TOTAL_KB=%s\nDISK_USED_KB=%s\nDISK_PUSED=%s\n", $2, $3, $5}' ''',
        # Established TCP sockets
        r'''echo "TCP_ESTAB=$(ss -Htan state established 2>/dev/null | wc -l)"''',
    ]

    for unit in systemd_units:
        lines.append(f'echo "SYS:{unit}=$(systemctl is-active {unit} 2>/dev/null || echo inactive)"')

    if containers:
        lines.append(
            'if command -v podman >/dev/null 2>&1 && [ "$(podman ps -aq 2>/dev/null | wc -l)" -gt 0 ]; then '
            'podman ps -a --format "CTR:{{.Names}}={{.Status}}" 2>/dev/null; '
            'elif command -v docker >/dev/null 2>&1; then '
            'docker ps -a --format "CTR:{{.Names}}={{.Status}}" 2>/dev/null; fi'
        )

    for proc in processes:
        lines.append(
            f'if pgrep -f "{proc}" >/dev/null 2>&1; then echo "PROC:{proc}=running"; else echo "PROC:{proc}=stopped"; fi'
        )

    if tomcat_app:
        lines.append(
            f'if [ -d "/usr/share/tomcat8/webapps/{tomcat_app}" ] || [ -d "/usr/share/tomcat/webapps/{tomcat_app}" ]; then '
            f'echo "TOMCAT_DEPLOY:{tomcat_app}=present"; else echo "TOMCAT_DEPLOY:{tomcat_app}=missing"; fi'
        )
        lines.append(
            'LOG_FILE=$(ls -t /var/log/tomcat8/catalina.out /usr/share/tomcat8/logs/catalina.out /var/log/tomcat*/catalina.out 2>/dev/null | head -n 1); '
            'if [ -n "$LOG_FILE" ] && tail -n 100 "$LOG_FILE" 2>/dev/null | grep -qiE "OutOfMemoryError|FATAL|CannotCreateTransactionException"; then '
            'echo "TOMCAT_LOG=error"; else echo "TOMCAT_LOG=ok"; fi'
        )

    return "\n".join(lines)


def parse_ssh_probe_output(
    host_id: str,
    stdout: str,
    latency_ms: int,
    servicos_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Converte a saída textual do probe SSH no contrato padrão de métricas."""
    cfg = servicos_config or {}
    expected_containers = _sanitize_names(cfg.get("containers"))

    hostname = host_id
    cpu_usage = 0.0
    mem_total_kb = 0
    mem_avail_kb = 0
    disk_total_kb = 0
    disk_used_kb = 0
    disk_pused = None
    tcp_estab = 0

    service_checks: Dict[str, str] = {}
    observed_containers: Dict[str, str] = {}
    has_critical_failure = False

    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        key, val = line.split("=", 1)

        if key == "HOSTNAME" and val:
            hostname = val
        elif key == "CPU":
            try:
                cpu_usage = round(max(0.0, min(100.0, float(val))), 1)
            except ValueError:
                pass
        elif key == "MEM_TOTAL_KB":
            try:
                mem_total_kb = int(val)
            except ValueError:
                pass
        elif key == "MEM_AVAIL_KB":
            try:
                mem_avail_kb = int(val)
            except ValueError:
                pass
        elif key == "DISK_TOTAL_KB":
            try:
                disk_total_kb = int(val)
            except ValueError:
                pass
        elif key == "DISK_USED_KB":
            try:
                disk_used_kb = int(val)
            except ValueError:
                pass
        elif key == "DISK_PUSED":
            try:
                disk_pused = float(val.rstrip("%"))
            except ValueError:
                pass
        elif key == "TCP_ESTAB":
            try:
                tcp_estab = int(val)
            except ValueError:
                pass
        elif key.startswith("SYS:"):
            unit = key.split(":", 1)[1]
            if val == "active":
                service_checks[f"Serviço {unit}"] = "connected"
            else:
                service_checks[f"Serviço {unit}"] = f"error: {val}"
                has_critical_failure = True
        elif key.startswith("CTR:"):
            ctr_name = key.split(":", 1)[1]
            observed_containers[ctr_name] = val
        elif key.startswith("PROC:"):
            proc = key.split(":", 1)[1]
            if val == "running":
                service_checks[f"Processo {proc}"] = "connected"
            else:
                service_checks[f"Processo {proc}"] = "error: stopped"
                has_critical_failure = True
        elif key.startswith("TOMCAT_DEPLOY:"):
            app_name = key.split(":", 1)[1]
            if val == "present":
                service_checks[f"Webapp {app_name}"] = "connected"
            else:
                service_checks[f"Webapp {app_name}"] = "error: missing"
                has_critical_failure = True
        elif key == "TOMCAT_LOG" and val == "error":
            service_checks["Logs Tomcat"] = "error: critical exception in catalina.out"
            has_critical_failure = True

    for ctr in expected_containers:
        status_str = observed_containers.get(ctr)
        if not status_str:
            service_checks[f"Container {ctr}"] = "error: not found"
            has_critical_failure = True
        elif status_str.lower().startswith("up") and "unhealthy" not in status_str.lower():
            service_checks[f"Container {ctr}"] = "connected"
        else:
            service_checks[f"Container {ctr}"] = f"error: {status_str}"
            has_critical_failure = True

    raw_mem_total_gb = mem_total_kb / (1024 * 1024) if mem_total_kb > 0 else 0.0
    mem_total_gb = _round_commercial_ram_gb(raw_mem_total_gb) if raw_mem_total_gb > 0 else 0.0
    mem_used_kb = max(0, mem_total_kb - mem_avail_kb)
    mem_used_gb = round(mem_used_kb / (1024 * 1024), 1) if mem_total_kb > 0 else 0.0
    mem_pct = round((mem_used_kb / mem_total_kb) * 100, 1) if mem_total_kb > 0 else 0.0

    disk_total_gb = round(disk_total_kb / (1024 * 1024), 1) if disk_total_kb > 0 else 0.0
    disk_used_gb = round(disk_used_kb / (1024 * 1024), 1) if disk_used_kb > 0 else 0.0
    if disk_pused is not None:
        disk_pct = round(disk_pused, 1)
    else:
        disk_pct = round((disk_used_kb / disk_total_kb) * 100, 1) if disk_total_kb > 0 else 0.0

    return {
        "source": "SSH",
        "available": True,
        "host_id": host_id,
        "name": hostname,
        "status": "ONLINE",
        "cpu_usage": cpu_usage,
        "memory_used_gb": mem_used_gb,
        "memory_total_gb": mem_total_gb,
        "memory_usage": mem_pct,
        "disk_used_gb": disk_used_gb,
        "disk_total_gb": disk_total_gb,
        "disk_usage": disk_pct,
        "active_connections": tcp_estab,
        "ping_latency_ms": latency_ms,
        "service_checks": service_checks,
        "has_critical_service_failure": has_critical_failure,
        "error": None,
    }


class SshMetricsProvider(HostMetricsProviderInterface):
    """Coleta métricas de SO e serviços via SSH usando chave configurada localmente."""

    def __init__(self, cache_ttl_seconds: int = 15, timeout_seconds: float = 6.0):
        self.cache_ttl_seconds = cache_ttl_seconds
        self.timeout_seconds = timeout_seconds
        self._cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}

    def clear_cache(self) -> None:
        """Limpa o cache em memória (útil em testes unitários)."""
        self._cache.clear()

    async def get_host_metrics(
        self,
        host_identifier: str,
        servicos_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Executa sonda SSH assíncrona com cache TTL curto e retorna métricas padronizadas."""
        target = (host_identifier or "").strip()
        if not target or not _SAFE_TARGET_RE.match(target):
            return _offline_metrics(host_identifier or "ssh", "Host SSH inválido ou não informado")

        cfg = servicos_config
        if isinstance(cfg, str):
            try:
                cfg = json.loads(cfg)
            except Exception:
                cfg = None

        cache_key = f"{target}:{json.dumps(cfg or {}, sort_keys=True)}"
        now = time.monotonic()
        cached = self._cache.get(cache_key)
        if cached and (now - cached[0]) < self.cache_ttl_seconds:
            return cached[1]

        script = _build_remote_probe_script(cfg)
        start = time.perf_counter()
        proc = None
        try:
            proc = await asyncio.create_subprocess_exec(
                "ssh",
                "-o", "BatchMode=yes",
                "-o", "StrictHostKeyChecking=accept-new",
                "-o", "ConnectTimeout=4",
                target,
                script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout_b, stderr_b = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout_seconds,
            )
            latency_ms = max(1, int((time.perf_counter() - start) * 1000))
            if proc.returncode != 0:
                err_txt = stderr_b.decode("utf-8", errors="replace").strip() or f"rc={proc.returncode}"
                return _offline_metrics(target, err_txt[:160])

            stdout_txt = stdout_b.decode("utf-8", errors="replace")
            metrics = parse_ssh_probe_output(target, stdout_txt, latency_ms, cfg)
            self._cache[cache_key] = (time.monotonic(), metrics)
            return metrics

        except asyncio.TimeoutError:
            if proc is not None:
                try:
                    proc.kill()
                    await proc.wait()
                except Exception:
                    pass
            return _offline_metrics(target, f"Timeout SSH ({self.timeout_seconds}s)")
        except Exception as exc:
            return _offline_metrics(target, str(exc)[:160])
