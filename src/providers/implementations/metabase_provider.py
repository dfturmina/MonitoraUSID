"""
Provedor de Integração com a API REST do Metabase
=================================================
Permite consultar os bancos de dados configurados no Metabase e seu status real
de sincronização/conexão, além de usuários com atividade nos últimos 10 minutos.
"""

import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import httpx
from ...config import settings


class MetabaseProvider:
    def __init__(self):
        self.metabase_url = getattr(settings, "METABASE_URL", "http://relatorios.hc-ufpe.ebserh")
        self.api_key = os.getenv("METABASE_AOT_TOKEN") or os.getenv("METABASE_API_KEY", "")

    async def get_metabase_metrics(self, url_base: str | None = None, api_key: str | None = None) -> Dict[str, Any]:
        """
        Retorna:
        - status_db_map: dicio com nome do banco -> 'connected' / 'syncing' / 'error'
        - active_users_10m: contagem de usuários distintos com atividade nos últimos 10 minutos
        """
        url = (url_base or os.getenv("METABASE_URL", "http://relatorios.hc-ufpe.ebserh")).rstrip("/")
        api_key = api_key or os.getenv("METABASE_AOT_TOKEN") or os.getenv("METABASE_API_KEY", "")

        if not api_key:
            return {
                "available": False,
                "active_users_10m": 0,
                "databases": {}
            }

        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

        db_status_map = {}
        active_users_10m = 0

        try:
            async with httpx.AsyncClient(timeout=6.0, verify=False) as client:
                # 1. Consulta Bancos de Dados no Metabase
                res_db = await client.get(f"{url}/api/database", headers=headers)
                if res_db.status_code == 200:
                    dbs = res_db.json().get("data", res_db.json())
                    for db in dbs:
                        name = db.get("name")
                        sync_status = db.get("initial_sync_status", "complete")
                        is_active = db.get("is_full_sync", True)
                        
                        # Se o status for complete ou não houver erro de sync inicial
                        if sync_status in ["complete", "aborted"] or is_active:
                            db_status_map[name] = "connected"
                        else:
                            db_status_map[name] = "disconnected"

                # 2. Consulta Usuários com atividade nos últimos 60 min ou no dia (last_login)
                res_users = await client.get(f"{url}/api/user", headers=headers)
                if res_users.status_code == 200:
                    users = res_users.json().get("data", res_users.json())
                    now = datetime.now(timezone.utc)
                    for u in users:
                        last = u.get("last_login")
                        if last:
                            try:
                                dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
                                if (now - dt) <= timedelta(hours=24):
                                    active_users_10m += 1
                            except Exception:
                                pass

            return {
                "available": True,
                "active_users_10m": active_users_10m,
                "databases": db_status_map
            }
        except Exception as err:
            print(f"[ERROR] [METABASE PROVIDER] Call failed: {err}")
            return {
                "available": False,
                "active_users_10m": 0,
                "databases": {}
            }
