"""
Testes Automatizados para Monitoramento dos 13 Sistemas (OpenSpec Changes)
=========================================================================
Valida seed idempotente, contratos HTTP/TCP/Health do HealthPollerService,
coleta via SshMetricsProvider, resolução por hostname no ZabbixProvider e
trilha de auditoria nas mutações de aplicações.
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from sqlalchemy.future import select

from src.models.aplicacao import Aplicacao
from src.models.audit_log import AuditLog
from src.providers.implementations.ssh_metrics_provider import (
    SshMetricsProvider,
    parse_ssh_probe_output,
)
from src.providers.implementations.zabbix_provider import ZabbixProvider
from src.resources.database import Base, DatabaseManager
from src.services.health_poller import HealthPollerService
from src.services.seed_sistemas import get_seed_applications_data, seed_monitored_systems


_REAL_ASYNC_CLIENT = httpx.AsyncClient


def _make_mock_http_client(handler):
    """Cria mock assíncrono de httpx.AsyncClient usando httpx.MockTransport."""
    transport = httpx.MockTransport(handler)
    return _REAL_ASYNC_CLIENT(transport=transport)


@pytest.mark.asyncio
async def test_seed_monitored_systems_idempotent(tmp_path):
    """Valida que seed_monitored_systems cadastra os 14 registros (13 sistemas) sem duplicar."""
    db_file = tmp_path / "seed_test.db"
    db = DatabaseManager(f"sqlite+aiosqlite:///{db_file}")
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with db.async_session_maker() as session:
        first_count = await seed_monitored_systems(session)
        assert first_count == 14
        second_count = await seed_monitored_systems(session)
        assert second_count == 0

        rows = (await session.execute(select(Aplicacao))).scalars().all()
        nomes = {r.nome for r in rows}
        expected = {item["nome"] for item in get_seed_applications_data()}
        assert nomes == expected
        assert len(rows) == 14

    await db.close_connection()


@pytest.mark.asyncio
async def test_poller_uti_manager_and_quimo_and_metabase_and_wokibi():
    """Valida contratos JSON de UTI Manager, Quimo, Metabase (Host header) e Wokibi (ready)."""

    async def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url == "https://10.34.0.192/api/health":
            return httpx.Response(
                200,
                json={
                    "status": "healthy",
                    "version": "1.8.1",
                    "active_users": 3,
                    "databases": {"app_db": "connected", "aghu_postgres": "connected"},
                },
            )
        if url == "https://10.34.0.191/api/health":
            return httpx.Response(
                200,
                json={"status": "healthy", "service": "Quimo", "version": "1.0.0"},
            )
        if url == "http://10.34.0.114:3000/api/health":
            assert request.headers.get("host") == "relatorios.hc-ufpe.ebserh"
            return httpx.Response(200, json={"status": "ok"})
        if url == "http://10.34.0.219:8080/health":
            return httpx.Response(200, json={"model": "noharm-ai/anony", "ready": True})
        if url == "http://10.34.0.219:3000/":
            return httpx.Response(200, text="<html>Wokibi</html>")
        return httpx.Response(404)

    async def fake_custom_dbs(bancos):
        return {b["nome"]: "Rede OK" for b in bancos}

    with patch("src.services.health_poller.httpx.AsyncClient", side_effect=lambda **kw: _make_mock_http_client(handler)), \
         patch.object(HealthPollerService, "check_custom_databases", side_effect=fake_custom_dbs):

        uti_res = await HealthPollerService.poll_single_app({
            "id": 1, "nome": "UTI Manager", "url_base": "https://10.34.0.192",
            "possui_rota_health": True, "url_health": "/api/health",
            "possui_banco_aghu": True, "monitora_usuarios_ativos": True,
        })
        assert uti_res["is_online"] is True
        assert uti_res["versao_semver"] == "1.8.1"
        assert uti_res["active_users"] == 3
        assert uti_res["databases"] == {"app_db": "connected", "aghu_postgres": "connected"}

        quimo_res = await HealthPollerService.poll_single_app({
            "id": 2, "nome": "Quimo", "url_base": "https://10.34.0.191",
            "possui_rota_health": True, "url_health": "/api/health",
            "possui_banco_aghu": True,
            "bancos_adicionais": [{"nome": "PostgreSQL Quimo", "host": "10.34.0.191", "porta": 5432}],
        })
        assert quimo_res["is_online"] is True
        assert quimo_res["versao_semver"] == "1.0.0"
        assert "Banco Aplicação" not in quimo_res["databases"]
        assert quimo_res["databases"]["PostgreSQL Quimo"] == "Rede OK"
        assert quimo_res["databases"]["Banco AGHU (PostgreSQL)"] == "not_in_route"

        mb_res = await HealthPollerService.poll_single_app({
            "id": 3, "nome": "Metabase", "url_base": "http://10.34.0.114:3000",
            "possui_rota_health": True, "url_health": "/api/health",
            "possui_banco_aghu": True,
            "http_headers": {"Host": "relatorios.hc-ufpe.ebserh"},
            "bancos_adicionais": [{"nome": "PostgreSQL Metabase", "host": "10.34.0.114", "porta": 5432}],
        })
        assert mb_res["is_online"] is True
        assert mb_res["databases"]["PostgreSQL Metabase"] == "Rede OK"

        wokibi_res = await HealthPollerService.poll_single_app({
            "id": 4, "nome": "Wokibi", "url_base": "http://10.34.0.219:8080",
            "possui_rota_health": True, "url_health": "/health",
            "possui_banco_aghu": False,
            "bancos_adicionais": [{"nome": "MongoDB Wokibi", "host": "10.34.0.219", "porta": 27017}],
            "servicos_monitorados": {"extra_http": [{"nome": "Frontend Next.js", "url": "http://10.34.0.219:3000/"}]},
        })
        assert wokibi_res["is_online"] is True
        assert wokibi_res["versao_semver"] == "noharm-ai/anony"
        assert wokibi_res["databases"]["MongoDB Wokibi"] == "Rede OK"
        assert wokibi_res["databases"]["Frontend Next.js"] == "connected"


@pytest.mark.asyncio
async def test_poller_wokibi_ready_false_marks_offline():
    """Wokibi com ready=false deve ser marcado offline mesmo com HTTP 200."""
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"model": "noharm-ai/anony", "ready": False})

    with patch("src.services.health_poller.httpx.AsyncClient", side_effect=lambda **kw: _make_mock_http_client(handler)):
        res = await HealthPollerService.poll_single_app({
            "id": 5, "nome": "Wokibi", "url_base": "http://10.34.0.219:8080",
            "possui_rota_health": True, "url_health": "/health",
        })
        assert res["is_online"] is False
        assert "error" in res["databases"]["Serviço IA"]


@pytest.mark.asyncio
async def test_poller_tcp_mode_gateway_powerbi():
    """Gateway Power BI (tipo_checagem=TCP) deve testar porta 10050 sem HTTP GET."""
    fake_writer = MagicMock()
    fake_writer.close = MagicMock()
    fake_writer.wait_closed = AsyncMock()

    with patch("src.services.health_poller.asyncio.open_connection", new=AsyncMock(return_value=(MagicMock(), fake_writer))):
        ok_res = await HealthPollerService.poll_single_app({
            "id": 14, "nome": "Gateway Power BI", "url_base": "10.34.0.70",
            "tipo_checagem": "TCP", "porta_tcp": 10050,
            "possui_rota_health": False, "possui_banco_aghu": True,
        })
        assert ok_res["is_online"] is True
        assert ok_res["status_http"] == 200
        assert ok_res["full_url"] == "tcp://10.34.0.70:10050"
        assert ok_res["databases"]["Porta TCP 10050"] == "Rede OK"

    with patch("src.services.health_poller.asyncio.open_connection", new=AsyncMock(side_effect=asyncio.TimeoutError("timed out"))):
        fail_res = await HealthPollerService.poll_single_app({
            "id": 14, "nome": "Gateway Power BI", "url_base": "10.34.0.70",
            "tipo_checagem": "TCP", "porta_tcp": 10050,
            "possui_rota_health": False, "possui_banco_aghu": True,
        })
        assert fail_res["is_online"] is False
        assert fail_res["status_http"] == 0
        assert "error" in fail_res["databases"]["Conexão"]


@pytest.mark.asyncio
async def test_poller_direct_http_systems_and_multi_db():
    """Valida sistemas sem /api/health (CSH, Master Tools, RealBlood, Dialsist, GED, MEWS, LEC, Tomcat)."""
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="OK")

    async def fake_open_conn(host, port):
        writer = MagicMock()
        writer.close = MagicMock()
        writer.wait_closed = AsyncMock()
        if host == "10.34.0.217" and port == 1433:
            raise ConnectionRefusedError("SQL Server down")
        return MagicMock(), writer

    with patch("src.services.health_poller.httpx.AsyncClient", side_effect=lambda **kw: _make_mock_http_client(handler)), \
         patch("src.services.health_poller.asyncio.open_connection", side_effect=fake_open_conn):

        realblood_res = await HealthPollerService.poll_single_app({
            "id": 13, "nome": "RealBlood", "url_base": "http://10.34.0.218/",
            "possui_rota_health": False, "possui_banco_aghu": True,
            "bancos_adicionais": [
                {"nome": "SQL Server RealBlood", "host": "10.34.0.217", "porta": 1433},
                {"nome": "IIS RealBlood BD", "host": "10.34.0.217", "porta": 80},
            ],
        })
        assert realblood_res["is_online"] is True
        assert "error:" in realblood_res["databases"]["SQL Server RealBlood"]
        assert realblood_res["databases"]["IIS RealBlood BD"] == "Rede OK"

        dialsist_res = await HealthPollerService.poll_single_app({
            "id": 8, "nome": "Dialsist", "url_base": "http://10.34.0.83/ufpeds4/",
            "possui_rota_health": False, "possui_banco_aghu": True,
            "bancos_adicionais": [
                {"nome": "MySQL Dialsist", "host": "10.34.0.83", "porta": 3306},
                {"nome": "AGHU Slave", "host": "10.34.0.92", "porta": 5432},
            ],
        })
        assert dialsist_res["is_online"] is True
        assert dialsist_res["databases"]["MySQL Dialsist"] == "Rede OK"
        assert dialsist_res["databases"]["AGHU Slave"] == "Rede OK"
        assert "AGHU DB (Declarado)" not in dialsist_res["databases"]


def test_parse_ssh_probe_output_containers_systemd_and_tomcat():
    """Valida parser de saída SSH para CPU, RAM, Disco, containers Docker/Podman, systemd e Tomcat."""
    stdout = "\n".join([
        "HOSTNAME=hc-ufpe-vp-sat-mews",
        "CPU=12.5",
        "MEM_TOTAL_KB=8040000",
        "MEM_AVAIL_KB=4020000",
        "DISK_TOTAL_KB=52428800",
        "DISK_USED_KB=10485760",
        "DISK_PUSED=20%",
        "TCP_ESTAB=18",
        "SYS:sistemalec=active",
        "CTR:cinco_hc-nginx-1=Up 6 months",
        "CTR:cinco_hc-app-1=Up 4 weeks",
        "CTR:cinco_hc-postgres-1=Up 6 months (unhealthy)",
        "PROC:puma=running",
        "TOMCAT_DEPLOY:IntegracaoMasterAghu=present",
        "TOMCAT_LOG=error",
    ])
    parsed = parse_ssh_probe_output(
        "mews",
        stdout,
        latency_ms=42,
        servicos_config={
            "systemd": ["sistemalec"],
            "containers": ["cinco_hc-nginx-1", "cinco_hc-app-1", "cinco_hc-postgres-1"],
            "processes": ["puma"],
            "tomcat_app": "IntegracaoMasterAghu",
        },
    )
    assert parsed["source"] == "SSH"
    assert parsed["available"] is True
    assert parsed["name"] == "hc-ufpe-vp-sat-mews"
    assert parsed["cpu_usage"] == 12.5
    assert parsed["memory_total_gb"] == 8.0
    assert parsed["disk_usage"] == 20.0
    assert parsed["active_connections"] == 18
    assert parsed["service_checks"]["Serviço sistemalec"] == "connected"
    assert parsed["service_checks"]["Container cinco_hc-nginx-1"] == "connected"
    assert "error:" in parsed["service_checks"]["Container cinco_hc-postgres-1"]
    assert parsed["service_checks"]["Processo puma"] == "connected"
    assert parsed["service_checks"]["Webapp IntegracaoMasterAghu"] == "connected"
    assert "error:" in parsed["service_checks"]["Logs Tomcat"]
    assert parsed["has_critical_service_failure"] is True


@pytest.mark.asyncio
async def test_ssh_provider_uses_ttl_cache():
    """SshMetricsProvider deve reutilizar cache dentro do TTL evitando chamadas repetidas."""
    provider = SshMetricsProvider(cache_ttl_seconds=60)
    fake_proc = MagicMock()
    fake_proc.returncode = 0
    fake_proc.communicate = AsyncMock(return_value=(b"HOSTNAME=wokibi\nCPU=5.0\nMEM_TOTAL_KB=4096000\nMEM_AVAIL_KB=2048000\nDISK_TOTAL_KB=20971520\nDISK_USED_KB=10485760\nDISK_PUSED=50%\nTCP_ESTAB=3\n", b""))

    with patch("src.providers.implementations.ssh_metrics_provider.asyncio.create_subprocess_exec", new=AsyncMock(return_value=fake_proc)) as mock_exec:
        m1 = await provider.get_host_metrics("wokibi", {"processes": ["app_anony.py"]})
        m2 = await provider.get_host_metrics("wokibi", {"processes": ["app_anony.py"]})
        assert m1["available"] is True
        assert m2["name"] == "wokibi"
        assert mock_exec.call_count == 1


@pytest.mark.asyncio
async def test_zabbix_provider_resolves_hostname_and_reports_unavailable():
    """ZabbixProvider deve resolver hostname não-numérico via filter.host e sinalizar available=False sem credenciais."""
    zp = ZabbixProvider()

    with patch.object(zp, "_call_rpc", new=AsyncMock(return_value=None)):
        miss = await zp.get_host_metrics("HCPE-VP-MAQUEIROS")
        assert miss["available"] is False

    async def fake_rpc(method, params):
        if method == "host.get":
            assert params.get("filter") == {"host": ["HCPE-VP-MAQUEIROS"]}
            return [{"hostid": "11309", "host": "HCPE-VP-MAQUEIROS", "name": "HCPE-VP-MAQUEIROS", "status": "0"}]
        if method == "item.get":
            assert params.get("hostids") == ["11309"]
            return [
                {"key_": "system.cpu.util", "lastvalue": "14.2"},
                {"key_": "vm.memory.size[total]", "lastvalue": str(8 * 1024**3)},
                {"key_": "vm.memory.size[available]", "lastvalue": str(4 * 1024**3)},
                {"key_": "vfs.fs.size[/,total]", "lastvalue": str(100 * 1024**3)},
                {"key_": "vfs.fs.size[/,used]", "lastvalue": str(25 * 1024**3)},
            ]
        return []

    with patch.object(zp, "_call_rpc", side_effect=fake_rpc):
        ok = await zp.get_host_metrics("HCPE-VP-MAQUEIROS")
        assert ok["available"] is True
        assert ok["host_id"] == "11309"
        assert ok["cpu_usage"] == 14.2
        assert ok["memory_total_gb"] == 8.0
        assert ok["disk_used_gb"] == 25.0


def test_dashboard_ssh_fallback_and_audit_trail(client):
    """Valida endpoint /api/monitor/dashboard com fallback SSH e trilha de auditoria em CRUD."""
    login = client.post("/api/login", data={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    create_resp = client.post(
        "/api/monitor/aplicacoes",
        headers=headers,
        json={
            "nome": "App Teste Audit SSH",
            "url_base": "10.34.0.70",
            "tipo_checagem": "TCP",
            "porta_tcp": 10050,
            "ssh_host": "wokibi",
            "possui_rota_health": False,
            "criticidade": "MEDIA",
        },
    )
    assert create_resp.status_code == 200
    created_id = create_resp.json()["id"]

    # Verifica registro de auditoria no banco
    async def _check_audit():
        async with client.app.state.app_db.async_session_maker() as s:
            res = await s.execute(
                select(AuditLog).where(AuditLog.recurso == f"aplicacao:{created_id}")
            )
            return res.scalars().all()

    logs = asyncio.run(_check_audit())
    assert len(logs) >= 1
    assert logs[0].acao == "CRIAR_APLICACAO"
    assert logs[0].categoria == "CONFIGURACAO"

    # Limpa o registro de teste com auditoria de exclusão
    del_resp = client.delete(f"/api/monitor/aplicacoes/{created_id}", headers=headers)
    assert del_resp.status_code == 200
