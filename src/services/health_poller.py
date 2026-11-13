"""
Serviço Assíncrono de Sondagem da Rota Health (Health Poller Service)
========================================================================
Realiza requisições HTTP GET assíncronas para sondar a saúde das aplicações
cadastradas no Monitora USID, calculando o tempo de resposta, registrando respostas,
bancos de dados dinâmicos e usuários ativos.
"""

import os
import time
from typing import Dict, Any, List
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.aplicacao import Aplicacao
from ..models.health_log import HealthLog


class HealthPollerService:
    """Serviço assíncrono para polling de status de aplicações."""

    @staticmethod
    async def poll_single_app(app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sonda uma única aplicação via HTTP GET."""
        possui_rota_health = app_data.get("possui_rota_health", True)
        possui_banco_aghu = app_data.get("possui_banco_aghu", False)
        url_base = app_data.get("url_base", "").rstrip("/")
        url_health = app_data.get("url_health", "/api/health")
        full_url = f"{url_base}{url_health}" if possui_rota_health else url_base

        start_time = time.perf_counter()
        status_http = 0
        databases_dict = {}
        versao_semver = None
        active_users = 0
        is_online = False

        if not possui_rota_health:
            # Caso a aplicação não tenha rota /api/health, testa a URL Base direta
            try:
                async with httpx.AsyncClient(timeout=4.0, verify=False) as client:
                    response = await client.get(url_base)
                    end_time = time.perf_counter()
                    latency_ms = int((end_time - start_time) * 1000)
                    status_http = response.status_code
                    is_online = response.status_code < 500
                    databases_dict = {}
                    if possui_banco_aghu:
                        databases_dict["AGHU DB (Declarado)"] = "monitored_via_zabbix"
            except Exception as err:
                end_time = time.perf_counter()
                latency_ms = int((end_time - start_time) * 1000)
                status_http = 0
                is_online = False
                databases_dict = {"Conexão": f"error: {str(err)}"}
        else:
            try:
                async with httpx.AsyncClient(timeout=4.0, verify=False) as client:
                    response = await client.get(full_url)
                    end_time = time.perf_counter()
                    latency_ms = int((end_time - start_time) * 1000)
                    status_http = response.status_code

                    if response.status_code == 200:
                        is_online = True
                        try:
                            data = response.json()
                            versao_semver = data.get("version", data.get("versao", "v1.0.0"))
                            active_users = data.get("active_users", data.get("active_sessions", 1))
                            
                            raw_dbs = data.get("databases")
                            if isinstance(raw_dbs, dict):
                                databases_dict = raw_dbs
                            elif isinstance(raw_dbs, str):
                                databases_dict = {"Banco": raw_dbs}
                            else:
                                databases_dict = {"Banco Aplicação": "connected"}
                        except Exception:
                            databases_dict = {"Banco Aplicação": "connected"}
                            active_users = 1
                    else:
                        databases_dict = {"Rota Health": f"HTTP {response.status_code}"}

                    if possui_banco_aghu and not any("aghu" in k.lower() for k in databases_dict.keys()):
                        databases_dict["Banco AGHU (PostgreSQL)"] = "not_in_route"
                    elif not possui_banco_aghu:
                        # Se não possui banco AGHU marcado, remove qualquer chave de AGHU que veio da resposta genérica de /api/health
                        databases_dict = {k: v for k, v in databases_dict.items() if "aghu" not in k.lower()}

            except Exception as err:
                end_time = time.perf_counter()
                latency_ms = int((end_time - start_time) * 1000)
                status_http = 0
                databases_dict = {"Conexão": f"error: {str(err)}"}
                is_online = False

        # Sondagem Dinâmica de Bancos de Dados Adicionais Cadastrados
        raw_bancos = app_data.get("bancos_adicionais")
        if raw_bancos:
            try:
                import json
                bancos_list = json.loads(raw_bancos) if isinstance(raw_bancos, str) else raw_bancos
                if isinstance(bancos_list, list) and len(bancos_list) > 0:
                    custom_dbs = await HealthPollerService.check_custom_databases(bancos_list)
                    # Se houverem bancos customizados sondados, remove a tag neutra de HTTP Direct
                    if custom_dbs:
                        databases_dict.pop("Status HTTP Direct", None)
                    for db_name, db_status in custom_dbs.items():
                        databases_dict[db_name] = db_status
            except Exception as e:
                print(f"[WARNING] Erro ao sondar bancos adicionais: {e}")

        # Tenta consulta no banco de aplicação do Metabase para contar usuários ativos se a URL estiver configurada
        metabase_db_url = os.getenv("METABASE_DB_URL", "")
        if metabase_db_url and app_data.get("monitora_usuarios_ativos"):
            try:
                from sqlalchemy.ext.asyncio import create_async_engine
                from sqlalchemy import text
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
            "possui_rota_health": possui_rota_health,
            "possui_banco_aghu": possui_banco_aghu,
            "monitora_usuarios_ativos": app_data.get("monitora_usuarios_ativos", False),
            "zabbix_host_id": app_data.get("zabbix_host_id", ""),
            "criticidade": app_data.get("criticidade", "MEDIA"),
            "bancos_adicionais": raw_bancos,
            "full_url": full_url,
            "status_http": status_http,
            "latency_ms": latency_ms,
            "active_users": active_users,
            "databases": databases_dict,
            "versao_semver": versao_semver,
            "is_online": is_online
        }

    @staticmethod
    async def check_custom_databases(bancos_list: List[Dict[str, Any]]) -> Dict[str, str]:
        """Sonda assincronamente a conectividade TCP de qualquer lista dinâmica de bancos de dados."""
        import asyncio
        results = {}
        for db in bancos_list:
            name = db.get("nome") or db.get("name") or "Banco"
            host = db.get("host") or db.get("ip") or "127.0.0.1"
            port = int(db.get("porta") or db.get("port") or 5432)
            try:
                reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=2.0)
                writer.close()
                await writer.wait_closed()
                results[name] = "Rede OK"
            except Exception as e:
                results[name] = f"error: {str(e)}"
        return results

    @classmethod
    async def poll_all_applications(cls, db_session: AsyncSession) -> List[Dict[str, Any]]:
        """Busca todas as aplicações ativas do banco de dados e executa sondagem em paralelo."""
        stmt = select(Aplicacao).where(Aplicacao.ativo == True)
        result = await db_session.execute(stmt)
        aplicacoes = result.scalars().all()

        results = []
        for app in aplicacoes:
            app_dict = {
                "id": app.id,
                "nome": app.nome,
                "url_base": app.url_base,
                "possui_rota_health": getattr(app, "possui_rota_health", True),
                "url_health": app.url_health,
                "possui_banco_aghu": getattr(app, "possui_banco_aghu", False),
                "monitora_usuarios_ativos": getattr(app, "monitora_usuarios_ativos", False),
                "zabbix_host_id": getattr(app, "zabbix_host_id", ""),
                "criticidade": app.criticidade,
                "bancos_adicionais": getattr(app, "bancos_adicionais", None)
            }
            poll_result = await cls.poll_single_app(app_dict)

            # Persiste o log no banco de dados
            log_entry = HealthLog(
                aplicacao_id=app.id,
                status_http=poll_result["status_http"],
                latency_ms=poll_result["latency_ms"],
                status_db=str(poll_result["databases"])[:50],
                versao_semver=poll_result["versao_semver"]
            )
            db_session.add(log_entry)
            results.append(poll_result)

        await db_session.commit()
        return results
