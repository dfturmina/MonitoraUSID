"""
Roteador API REST do Monitora USID (/api/monitor)
==================================================
Fornece dados em tempo real para o Dashboard (Cards de status, métricas do Zabbix em GB,
detalhamento genérico de bancos de dados, usuários ativos e incidentes Zabbix).
Protegido por padrão via Default-Private Router Pattern.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..auth.auth import auth_handler
from ..resources.database import get_app_db_session
from ..models.aplicacao import Aplicacao
from ..models.health_log import HealthLog
from ..services.health_poller import HealthPollerService
from ..providers.implementations.zabbix_provider import ZabbixProvider
from ..providers.implementations.metabase_provider import MetabaseProvider

router = APIRouter(
    prefix="/api/monitor",
    tags=["Monitoramento USID"],
    dependencies=[Depends(auth_handler.decode_token)]
)

zabbix_provider = ZabbixProvider()
metabase_provider = MetabaseProvider()


class AplicacaoCreate(BaseModel):
    nome: str
    descricao: str | None = None
    url_base: str
    possui_rota_health: bool = True
    url_health: str = "/api/health"
    possui_banco_aghu: bool = False
    monitora_usuarios_ativos: bool = False
    zabbix_host_id: str | None = None
    criticidade: str = "MEDIA"
    integracao_id: int | None = None
    bancos_adicionais: Any | None = None


@router.get("/dashboard")
async def get_dashboard_summary(session: AsyncSession = Depends(get_app_db_session)) -> Dict[str, Any]:
    """Retorna dados consolidados para o Dashboard em tempo real."""
    stmt = select(Aplicacao).where(Aplicacao.ativo == True)
    res = await session.execute(stmt)
    apps = res.scalars().all()

    # Extrai os Host IDs do Zabbix das aplicações cadastradas
    registered_host_ids = [
        str(a.zabbix_host_id).strip() 
        for a in apps 
        if a.zabbix_host_id and str(a.zabbix_host_id).strip()
    ]

    # Busca alertas ativos do Zabbix apenas para os Host IDs cadastrados
    zabbix_problems = await zabbix_provider.get_active_problems(host_ids=registered_host_ids)

    if not apps:
        return {
            "summary": {
                "total_apps": 0,
                "online_apps": 0,
                "offline_apps": 0,
                "avg_latency_ms": 0,
                "active_problems_count": len(zabbix_problems)
            },
            "applications": [],
            "zabbix_problems": zabbix_problems
        }

    import json
    apps_data = []
    for a in apps:
        b_adic = getattr(a, "bancos_adicionais", None)
        if b_adic and isinstance(b_adic, str):
            try:
                b_adic = json.loads(b_adic)
            except Exception:
                pass

        apps_data.append({
            "id": a.id, 
            "nome": a.nome, 
            "url_base": a.url_base, 
            "possui_rota_health": getattr(a, "possui_rota_health", True),
            "url_health": a.url_health or "/api/health", 
            "possui_banco_aghu": getattr(a, "possui_banco_aghu", False),
            "monitora_usuarios_ativos": getattr(a, "monitora_usuarios_ativos", False),
            "zabbix_host_id": a.zabbix_host_id or "",
            "criticidade": a.criticidade,
            "integracao_id": getattr(a, "integracao_id", None),
            "bancos_adicionais": b_adic
        })

    poll_results = []
    for app_info in apps_data:
        poll_res = await HealthPollerService.poll_single_app(app_info)
        
        # Busca métricas em GB e Ping do Zabbix Provider apenas se um Host ID tiver sido configurado (não vazio)
        zabbix_host = (app_info.get("zabbix_host_id") or "").strip()
        if zabbix_host:
            poll_res["zabbix"] = await zabbix_provider.get_host_metrics(zabbix_host)
            # Para aplicações que não possuem rota health própria (ex: Metabase) e se active_users ainda for 0, usa conexões Zabbix se houver
            if poll_res.get("zabbix"):
                zb = poll_res["zabbix"]
        # Se a aplicação tiver uma integração vinculada ou for o Metabase
        integ_id = app_info.get("integracao_id")
        integ_obj = None
        if integ_id:
            from ..models.integracao import Integracao
            stmt_i = select(Integracao).where(Integracao.id == integ_id, Integracao.ativo == True)
            res_i = await session.execute(stmt_i)
            integ_obj = res_i.scalar_one_or_none()

        is_metabase = (integ_obj and integ_obj.provedor == "METABASE") or "metabase" in (app_info.get("nome") or "").lower() or "metabase" in (app_info.get("url_base") or "").lower()
        if is_metabase:
            url_target = integ_obj.url_base if integ_obj else app_info.get("url_base")
            key_target = integ_obj.api_key if integ_obj else None
            mb_data = await metabase_provider.get_metabase_metrics(url_base=url_target, api_key=key_target)
            if mb_data.get("available"):
                mb_users = mb_data.get("active_users_10m", 0)
                z_conns = poll_res["zabbix"].get("active_connections", 0) if poll_res.get("zabbix") else 0
                
                # Escolhe o maior valor entre os logins da API e as conexões de rede do Zabbix
                if z_conns > mb_users:
                    poll_res["active_users"] = z_conns
                    poll_res["active_users_origin"] = "tcp_zabbix"
                else:
                    poll_res["active_users"] = mb_users
                    poll_res["active_users_origin"] = "api_users"

                # Substitui os bancos adicionais estáticos por TODOS os 17 bancos reais cadastrados no Metabase
                mb_dbs = mb_data.get("databases", {})
                if mb_dbs:
                    poll_res["databases"] = {
                        db_name: ("connected" if status in ["complete", "connected"] else "disconnected")
                        for db_name, status in mb_dbs.items()
                    }

        poll_results.append(poll_res)

        # Dispara notificação no Teams caso o status tenha mudado (ONLINE -> OFFLINE ou OFFLINE -> ONLINE)
        try:
            from ..services.teams_alert_service import TeamsAlertService
            await TeamsAlertService.notify_system_status(
                app_id=app_info["id"],
                app_name=app_info["nome"],
                full_url=poll_res["full_url"],
                is_online=poll_res["is_online"],
                status_http=poll_res["status_http"],
                latency_ms=poll_res["latency_ms"],
                criticidade=app_info.get("criticidade", "MEDIA"),
                error_detail=str(poll_res.get("databases", {}).get("Conexão", "")) if not poll_res["is_online"] else None
            )
        except Exception as alert_err:
            print(f"[TEAMS ALERT] Falha ao avaliar alerta: {alert_err}")

        # Salva registro no histórico de logs
        try:
            log_item = HealthLog(
                aplicacao_id=app_info["id"],
                status_http=poll_res["status_http"],
                latency_ms=poll_res["latency_ms"],
                status_db=str(poll_res["databases"])[:50],
                versao_semver=poll_res["versao_semver"]
            )
            session.add(log_item)
        except Exception:
            pass

    await session.commit()

    total_apps = len(poll_results)
    online_apps = sum(1 for p in poll_results if p["is_online"])
    offline_apps = total_apps - online_apps
    avg_latency = int(sum(p["latency_ms"] for p in poll_results) / total_apps) if total_apps > 0 else 0

    return {
        "summary": {
            "total_apps": total_apps,
            "online_apps": online_apps,
            "offline_apps": offline_apps,
            "avg_latency_ms": avg_latency,
            "active_problems_count": len(zabbix_problems)
        },
        "applications": poll_results,
        "zabbix_problems": zabbix_problems
    }


@router.get("/historico")
async def get_health_history(
    limit: int = Query(50, ge=1, le=500),
    session: AsyncSession = Depends(get_app_db_session)
) -> List[Dict[str, Any]]:
    """Retorna o histórico recente de sondagem da rota /api/health."""
    stmt = (
        select(HealthLog)
        .options(selectinload(HealthLog.aplicacao))
        .order_by(HealthLog.checked_at.desc())
        .limit(limit)
    )
    res = await session.execute(stmt)
    logs = res.scalars().all()

    items = []
    for log in logs:
        items.append({
            "id": log.id,
            "aplicacao_nome": log.aplicacao.nome if log.aplicacao else f"App #{log.aplicacao_id}",
            "status_http": log.status_http,
            "latency_ms": log.latency_ms,
            "status_db": log.status_db,
            "versao_semver": log.versao_semver,
            "checked_at": log.checked_at.isoformat() if log.checked_at else None,
            "is_online": log.status_http == 200
        })
    return items


@router.get("/aplicacoes")
async def listar_aplicacoes(session: AsyncSession = Depends(get_app_db_session)):
    """Lista todas as aplicações cadastradas."""
    stmt = select(Aplicacao)
    res = await session.execute(stmt)
    return res.scalars().all()


@router.post("/aplicacoes")
async def cadastrar_aplicacao(
    payload: AplicacaoCreate,
    session: AsyncSession = Depends(get_app_db_session)
):
    """Cadastra uma nova aplicação no monitoramento."""
    import json
    b_json = json.dumps(payload.bancos_adicionais) if payload.bancos_adicionais is not None and not isinstance(payload.bancos_adicionais, str) else payload.bancos_adicionais

    nova_app = Aplicacao(
        nome=payload.nome,
        descricao=payload.descricao,
        url_base=payload.url_base,
        possui_rota_health=payload.possui_rota_health,
        url_health=payload.url_health,
        possui_banco_aghu=payload.possui_banco_aghu,
        monitora_usuarios_ativos=payload.monitora_usuarios_ativos,
        zabbix_host_id=payload.zabbix_host_id,
        criticidade=payload.criticidade,
        integracao_id=payload.integracao_id,
        bancos_adicionais=b_json
    )
    session.add(nova_app)
    await session.commit()
    await session.refresh(nova_app)
    return nova_app


@router.put("/aplicacoes/{app_id}")
async def editar_aplicacao(
    app_id: int,
    payload: AplicacaoCreate,
    session: AsyncSession = Depends(get_app_db_session)
):
    """Atualiza as informações de uma aplicação existente."""
    import json
    stmt = select(Aplicacao).where(Aplicacao.id == app_id)
    res = await session.execute(stmt)
    app = res.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Aplicação não encontrada")

    b_json = json.dumps(payload.bancos_adicionais) if payload.bancos_adicionais is not None and not isinstance(payload.bancos_adicionais, str) else payload.bancos_adicionais

    app.nome = payload.nome
    app.descricao = payload.descricao
    app.url_base = payload.url_base
    app.possui_rota_health = payload.possui_rota_health
    app.url_health = payload.url_health
    app.possui_banco_aghu = payload.possui_banco_aghu
    app.monitora_usuarios_ativos = payload.monitora_usuarios_ativos
    app.zabbix_host_id = payload.zabbix_host_id
    app.criticidade = payload.criticidade
    app.integracao_id = payload.integracao_id
    app.bancos_adicionais = b_json

    await session.commit()
    await session.refresh(app)
    return app


@router.delete("/aplicacoes/{app_id}")
async def excluir_aplicacao(
    app_id: int,
    session: AsyncSession = Depends(get_app_db_session)
):
    """Exclui uma aplicação do monitoramento."""
    stmt = select(Aplicacao).where(Aplicacao.id == app_id)
    res = await session.execute(stmt)
    app = res.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Aplicação não encontrada")

    await session.delete(app)
    await session.commit()
    return {"detail": "Aplicação excluída com sucesso"}


@router.post("/test-teams-alert")
async def test_teams_alert(
    webhook_url: str | None = None
):
    """Dispara uma mensagem de teste para o Webhook do Teams configurado no .env ou fornecido."""
    from ..services.teams_alert_service import TeamsAlertService
    ok = await TeamsAlertService.send_test_message(webhook_url=webhook_url)
    if not ok:
        raise HTTPException(status_code=400, detail="Não foi possível enviar a mensagem de teste para o Teams. Verifique a URL do Webhook.")
    return {"detail": "Mensagem de teste enviada com sucesso para o Teams!"}
