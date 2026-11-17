"""
Serviço Assíncrono de Sondagem da Rota Health (Health Poller Service)
========================================================================
Realiza sondagens HTTP GET e TCP assíncronas para verificar a saúde das aplicações
cadastradas no Monitora USID, calculando o tempo de resposta, registrando respostas,
bancos de dados dinâmicos, endpoints complementares e usuários ativos.
"""

import asyncio
import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.aplicacao import Aplicacao
from ..models.health_log import HealthLog


def _parse_json_field(raw: Any) -> Any:
    """Converte strings JSON armazenadas no banco para objetos Python com segurança."""
    if raw is None:
        return None
    if isinstance(raw, (dict, list)):
        return raw
    if isinstance(raw, str):
        text_val = raw.strip()
        if not text_val:
            return None
        try:
            return json.loads(text_val)
        except Exception:
            return None
    return None


def _extract_host_port(url_base: str, porta_tcp: Optional[int]) -> Tuple[str, int]:
    """Extrai host e porta TCP a partir de url_base e porta_tcp opcional."""
    raw = (url_base or "").strip()
    if "://" not in raw:
        raw_for_parse = f"tcp://{raw}"
    else:
        raw_for_parse = raw
    parsed = urlparse(raw_for_parse)
    host = parsed.hostname or raw.split(":")[0] or "127.0.0.1"
    port = int(porta_tcp or parsed.port or 80)
    return host, port


class HealthPollerService:
    """Serviço assíncrono para polling de status de aplicações."""

    @staticmethod
    async def _probe_tcp_endpoint(url_base: str, porta_tcp: Optional[int]) -> Tuple[bool, int, int, Dict[str, str], str]:
        """Sonda conectividade TCP direta para aplicações sem servidor HTTP."""
        host, port = _extract_host_port(url_base, porta_tcp)
        full_url = f"tcp://{host}:{port}"
        start_time = time.perf_counter()
        try:
            _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=4.0)
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            writer.close()
            await writer.wait_closed()
            return True, 200, latency_ms, {f"Porta TCP {port}": "Rede OK"}, full_url
        except Exception as err:
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            return False, 0, latency_ms, {"Conexão": f"error: {str(err) or type(err).__name__}"}, full_url

    @staticmethod
    async def _probe_extra_http(extra_list: List[Dict[str, Any]]) -> Dict[str, str]:
        """Sonda URLs HTTP complementares configuradas em servicos_monitorados.extra_http."""
        async def _check_one(item: Dict[str, Any]) -> Tuple[str, str]:
            name = str(item.get("nome") or item.get("name") or item.get("url") or "Endpoint")
            url = str(item.get("url") or "").strip()
            if not url:
                return name, "error: url vazia"
            try:
                async with httpx.AsyncClient(timeout=3.5, verify=False, follow_redirects=True) as client:
                    resp = await client.get(url)
                    if resp.status_code < 500:
                        return name, "connected"
                    return name, f"error: HTTP {resp.status_code}"
            except Exception as exc:
                return name, f"error: {str(exc) or type(exc).__name__}"

        tasks = [_check_one(it) for it in extra_list if isinstance(it, dict)]
        if not tasks:
            return {}
        pairs = await asyncio.gather(*tasks)
        return dict(pairs)

    @staticmethod
    async def poll_single_app(app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sonda uma única aplicação via HTTP GET ou TCP conforme tipo_checagem."""
        tipo_checagem = str(app_data.get("tipo_checagem") or "HTTP").upper()
        possui_rota_health = app_data.get("possui_rota_health", True)
        possui_banco_aghu = app_data.get("possui_banco_aghu", False)
        url_base = str(app_data.get("url_base") or "").rstrip("/")
        url_health = str(app_data.get("url_health") or "/api/health")
        custom_headers = _parse_json_field(app_data.get("http_headers"))
        if not isinstance(custom_headers, dict):
            custom_headers = None

        full_url = f"{url_base}{url_health}" if possui_rota_health else url_base
        status_http = 0
        latency_ms = 0
        databases_dict: Dict[str, str] = {}
        versao_semver: Optional[str] = None
        active_users = 0
        is_online = False
        has_explicit_dbs = False

        if tipo_checagem == "TCP":
            is_online, status_http, latency_ms, databases_dict, full_url = (
                await HealthPollerService._probe_tcp_endpoint(url_base, app_data.get("porta_tcp"))
            )
        elif not possui_rota_health:
            start_time = time.perf_counter()
            try:
                async with httpx.AsyncClient(timeout=4.0, verify=False, follow_redirects=True) as client:
                    response = await client.get(url_base, headers=custom_headers)
                    latency_ms = int((time.perf_counter() - start_time) * 1000)
                    status_http = response.status_code
                    is_online = response.status_code < 500
                    databases_dict = {}
            except Exception as err:
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                status_http = 0
                is_online = False
                databases_dict = {"Conexão": f"error: {str(err) or type(err).__name__}"}
        else:
            start_time = time.perf_counter()
            try:
                async with httpx.AsyncClient(timeout=4.0, verify=False, follow_redirects=True) as client:
                    response = await client.get(full_url, headers=custom_headers)
                    latency_ms = int((time.perf_counter() - start_time) * 1000)
                    status_http = response.status_code

                    if response.status_code == 200:
                        is_online = True
                        try:
                            data = response.json()
                            if isinstance(data, dict):
                                if "ready" in data and data.get("ready") is not True:
                                    is_online = False
                                    databases_dict = {"Serviço IA": "error: model not ready"}
                                elif str(data.get("status", "")).lower() in ("unhealthy", "error", "down", "failed"):
                                    is_online = False

                                versao_semver = (
                                    data.get("version")
                                    or data.get("versao")
                                    or data.get("model")
                                )
                                active_users = int(data.get("active_users", data.get("active_sessions", 0)) or 0)

                                raw_dbs = data.get("databases")
                                if isinstance(raw_dbs, dict):
                                    databases_dict = dict(raw_dbs)
                                    has_explicit_dbs = True
                                elif isinstance(raw_dbs, str):
                                    databases_dict = {"Banco": raw_dbs}
                                    has_explicit_dbs = True
                                elif is_online:
                                    databases_dict = {"Banco Aplicação": "connected"}
                        except Exception:
                            databases_dict = {"Banco Aplicação": "connected"}
                            active_users = 1
                    else:
                        databases_dict = {"Rota Health": f"HTTP {response.status_code}"}
            except Exception as err:
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                status_http = 0
                databases_dict = {"Conexão": f"error: {str(err) or type(err).__name__}"}
                is_online = False

        # Sondagem Dinâmica de Bancos de Dados Adicionais Cadastrados
        bancos_list = _parse_json_field(app_data.get("bancos_adicionais"))
        if isinstance(bancos_list, list) and len(bancos_list) > 0:
            try:
                custom_dbs = await HealthPollerService.check_custom_databases(bancos_list)
                if custom_dbs:
                    databases_dict.pop("Status HTTP Direct", None)
                    if not has_explicit_dbs:
                        databases_dict.pop("Banco Aplicação", None)
                    for db_name, db_status in custom_dbs.items():
                        databases_dict[db_name] = db_status
            except Exception as e:
                print(f"[WARNING] Erro ao sondar bancos adicionais: {e}")

        # Sondagem de endpoints HTTP complementares configurados em servicos_monitorados
        servicos_cfg = _parse_json_field(app_data.get("servicos_monitorados"))
        if isinstance(servicos_cfg, dict) and isinstance(servicos_cfg.get("extra_http"), list):
            extra_results = await HealthPollerService._probe_extra_http(servicos_cfg["extra_http"])
            for ep_name, ep_status in extra_results.items():
                databases_dict[ep_name] = ep_status

        # Regra consolidada de Banco AGHU
        if possui_banco_aghu:
            if not any("aghu" in k.lower() for k in databases_dict.keys()):
                if tipo_checagem == "HTTP" and possui_rota_health:
                    databases_dict["Banco AGHU (PostgreSQL)"] = "not_in_route"
                else:
                    databases_dict["AGHU DB (Declarado)"] = "monitored_via_zabbix"
        elif tipo_checagem == "HTTP" and possui_rota_health:
            databases_dict = {k: v for k, v in databases_dict.items() if "aghu" not in k.lower()}

        # Tenta consulta no banco de aplicação do Metabase para contar usuários ativos se a URL estiver configurada
        metabase_db_url = os.getenv("METABASE_DB_URL", "")
        if metabase_db_url and app_data.get("monitora_usuarios_ativos"):
            try:
                from sqlalchemy import text
                from sqlalchemy.ext.asyncio import create_async_engine

                mb_engine = create_async_engine(metabase_db_url, echo=False)
                async with mb_engine.connect() as conn:
                    query = text("SELECT COUNT(DISTINCT user_id) FROM core_session WHERE created_at >= NOW() - INTERVAL '30 minutes'")
                    res_mb = await conn.execute(query)
                    count_val = res_mb.scalar()
                    if count_val is not None:
                        active_users = int(count_val)
                await mb_engine.dispose()
            except Exception as mb_err:
                print(f"[WARNING] Erro ao consultar banco de aplicação do Metabase: {mb_err}")

        return {
            "aplicacao_id": app_data.get("id"),
            "id": app_data.get("id"),
            "nome": app_data.get("nome"),
            "url_base": url_base,
            "url_health": url_health,
            "tipo_checagem": tipo_checagem,
            "porta_tcp": app_data.get("porta_tcp"),
            "ssh_host": app_data.get("ssh_host"),
            "http_headers": custom_headers,
            "servicos_monitorados": servicos_cfg,
            "possui_rota_health": possui_rota_health,
            "possui_banco_aghu": possui_banco_aghu,
            "monitora_usuarios_ativos": app_data.get("monitora_usuarios_ativos", False),
            "zabbix_host_id": app_data.get("zabbix_host_id", ""),
            "criticidade": app_data.get("criticidade", "MEDIA"),
            "bancos_adicionais": bancos_list,
            "full_url": full_url,
            "status_http": status_http,
            "latency_ms": latency_ms,
            "active_users": active_users,
            "databases": databases_dict,
            "versao_semver": versao_semver,
            "is_online": is_online,
        }

    @staticmethod
    async def check_custom_databases(bancos_list: List[Dict[str, Any]]) -> Dict[str, str]:
        """Sonda assincronamente em paralelo a conectividade TCP de uma lista de bancos."""
        async def _check_db(db: Dict[str, Any]) -> Tuple[str, str]:
            name = str(db.get("nome") or db.get("name") or "Banco")
            host = str(db.get("host") or db.get("ip") or "127.0.0.1")
            port = int(db.get("porta") or db.get("port") or 5432)
            try:
                _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=2.0)
                writer.close()
                await writer.wait_closed()
                return name, "Rede OK"
            except Exception as exc:
                return name, f"error: {str(exc) or type(exc).__name__}"

        tasks = [_check_db(db) for db in bancos_list if isinstance(db, dict)]
        if not tasks:
            return {}
        pairs = await asyncio.gather(*tasks)
        return dict(pairs)

    @classmethod
    async def poll_all_applications(cls, db_session: AsyncSession) -> List[Dict[str, Any]]:
        """Busca todas as aplicações ativas do banco de dados e executa sondagem em paralelo."""
        stmt = select(Aplicacao).where(Aplicacao.ativo == True)
        result = await db_session.execute(stmt)
        aplicacoes = result.scalars().all()

        app_dicts = [
            {
                "id": app.id,
                "nome": app.nome,
                "url_base": app.url_base,
                "possui_rota_health": getattr(app, "possui_rota_health", True),
                "url_health": app.url_health,
                "possui_banco_aghu": getattr(app, "possui_banco_aghu", False),
                "monitora_usuarios_ativos": getattr(app, "monitora_usuarios_ativos", False),
                "zabbix_host_id": getattr(app, "zabbix_host_id", ""),
                "criticidade": app.criticidade,
                "bancos_adicionais": getattr(app, "bancos_adicionais", None),
                "tipo_checagem": getattr(app, "tipo_checagem", "HTTP"),
                "porta_tcp": getattr(app, "porta_tcp", None),
                "ssh_host": getattr(app, "ssh_host", None),
                "http_headers": getattr(app, "http_headers", None),
                "servicos_monitorados": getattr(app, "servicos_monitorados", None),
            }
            for app in aplicacoes
        ]

        results = list(await asyncio.gather(*(cls.poll_single_app(d) for d in app_dicts)))

        for app, poll_result in zip(aplicacoes, results):
            log_entry = HealthLog(
                aplicacao_id=app.id,
                status_http=poll_result["status_http"],
                latency_ms=poll_result["latency_ms"],
                status_db=str(poll_result["databases"])[:50],
                versao_semver=poll_result["versao_semver"],
            )
            db_session.add(log_entry)

        await db_session.commit()
        return results
