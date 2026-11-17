"""
Roteador API REST do Monitora USID (/api/monitor)
==================================================
Fornece dados em tempo real para o Dashboard (Cards de status, métricas do Zabbix/SSH em GB,
detalhamento genérico de bancos de dados, serviços locais, usuários ativos e incidentes Zabbix).
Protegido por padrão via Default-Private Router Pattern.
"""

import asyncio
import json
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..auth.auth import auth_handler
from ..helpers.audit_helper import registrar_auditoria
from ..models.aplicacao import Aplicacao
from ..models.health_log import HealthLog
from ..models.integracao import Integracao
from ..providers.implementations.metabase_provider import MetabaseProvider
from ..providers.implementations.ssh_metrics_provider import SshMetricsProvider
from ..providers.implementations.zabbix_provider import ZabbixProvider
from ..resources.database import get_app_db_session
from ..services.health_poller import HealthPollerService

router = APIRouter(
    prefix="/api/monitor",
    tags=["Monitoramento USID"],
    dependencies=[Depends(auth_handler.decode_token)],
)

zabbix_provider = ZabbixProvider()
ssh_metrics_provider = SshMetricsProvider()
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
    tipo_checagem: str = "HTTP"
    porta_tcp: int | None = None
    ssh_host: str | None = None
    http_headers: Any | None = None
    servicos_monitorados: Any | None = None


def _serialize_json_field(val: Any) -> str | None:
    if val is None:
        return None
    if isinstance(val, str):
        return val
    return json.dumps(val, ensure_ascii=False)


def _deserialize_json_field(val: Any) -> Any:
    if isinstance(val, str) and val.strip():
        try:
            return json.loads(val)
        except Exception:
            return val
    return val


def _has_ssh_service_checks(servicos_cfg: Any) -> bool:
    if not isinstance(servicos_cfg, dict):
        return False
    return any(bool(servicos_cfg.get(k)) for k in ("systemd", "containers", "processes", "tomcat_app"))


async def _collect_single_app_dashboard(
    app_info: Dict[str, Any],
    integracoes_map: Dict[int, Integracao],
) -> Dict[str, Any]:
    """Executa sondagem HTTP/TCP e enriquece com Zabbix, SSH e Metabase."""
    poll_res = await HealthPollerService.poll_single_app(app_info)

    zabbix_host = (app_info.get("zabbix_host_id") or "").strip()
    ssh_host = (app_info.get("ssh_host") or "").strip()
    servicos_cfg = app_info.get("servicos_monitorados")

    z_metrics = None
    if zabbix_host:
        z_metrics = await zabbix_provider.get_host_metrics(zabbix_host)
        if z_metrics and z_metrics.get("available"):
            poll_res["zabbix"] = z_metrics

    need_ssh = bool(ssh_host) and (
        not poll_res.get("zabbix") or _has_ssh_service_checks(servicos_cfg)
    )
    if need_ssh:
        ssh_metrics = await ssh_metrics_provider.get_host_metrics(ssh_host, servicos_cfg)
        if not poll_res.get("zabbix") and ssh_metrics.get("available"):
            poll_res["zabbix"] = ssh_metrics
        elif not poll_res.get("zabbix") and z_metrics is not None:
            poll_res["zabbix"] = z_metrics

        if ssh_metrics.get("available"):
            service_checks = ssh_metrics.get("service_checks") or {}
            if service_checks:
                poll_res["databases"].update(service_checks)
            if ssh_metrics.get("has_critical_service_failure"):
                poll_res["is_online"] = False

    integ_id = app_info.get("integracao_id")
    integ_obj = integracoes_map.get(integ_id) if integ_id else None
    is_metabase = (
        (integ_obj and integ_obj.provedor == "METABASE")
        or "metabase" in (app_info.get("nome") or "").lower()
        or "metabase" in (app_info.get("url_base") or "").lower()
    )
    if is_metabase:
        url_target = integ_obj.url_base if integ_obj else app_info.get("url_base")
        key_target = integ_obj.api_key if integ_obj else None
        mb_data = await metabase_provider.get_metabase_metrics(url_base=url_target, api_key=key_target)
        if mb_data.get("available"):
            mb_users = mb_data.get("active_users_10m", 0)
            z_conns = poll_res["zabbix"].get("active_connections", 0) if poll_res.get("zabbix") else 0
            if z_conns > mb_users:
                poll_res["active_users"] = z_conns
                poll_res["active_users_origin"] = "tcp_zabbix"
            else:
                poll_res["active_users"] = mb_users
                poll_res["active_users_origin"] = "api_users"

            mb_dbs = mb_data.get("databases", {})
            if mb_dbs:
                for db_name, db_st in mb_dbs.items():
                    poll_res["databases"][db_name] = (
                        "connected" if db_st in ["complete", "connected"] else "disconnected"
                    )

    return poll_res


@router.get("/dashboard")
async def get_dashboard_summary(session: AsyncSession = Depends(get_app_db_session)) -> Dict[str, Any]:
    """Retorna dados consolidados para o Dashboard em tempo real."""
    stmt = select(Aplicacao).where(Aplicacao.ativo == True)
    res = await session.execute(stmt)
    apps = res.scalars().all()

    registered_host_ids = [
        str(a.zabbix_host_id).strip()
        for a in apps
        if a.zabbix_host_id and str(a.zabbix_host_id).strip()
    ]
    zabbix_problems = await zabbix_provider.get_active_problems(host_ids=registered_host_ids)

    if not apps:
        return {
            "summary": {
                "total_apps": 0,
                "online_apps": 0,
                "offline_apps": 0,
                "avg_latency_ms": 0,
                "active_problems_count": len(zabbix_problems),
            },
            "applications": [],
            "zabbix_problems": zabbix_problems,
        }

    integ_res = await session.execute(select(Integracao).where(Integracao.ativo == True))
    integracoes_map = {item.id: item for item in integ_res.scalars().all()}

    apps_data = [
        {
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
            "bancos_adicionais": _deserialize_json_field(getattr(a, "bancos_adicionais", None)),
            "tipo_checagem": getattr(a, "tipo_checagem", "HTTP") or "HTTP",
            "porta_tcp": getattr(a, "porta_tcp", None),
            "ssh_host": getattr(a, "ssh_host", None),
            "http_headers": _deserialize_json_field(getattr(a, "http_headers", None)),
            "servicos_monitorados": _deserialize_json_field(getattr(a, "servicos_monitorados", None)),
        }
        for a in apps
    ]

    poll_results = list(
        await asyncio.gather(*(_collect_single_app_dashboard(info, integracoes_map) for info in apps_data))
    )

    from ..services.teams_alert_service import TeamsAlertService

    for app_info, poll_res in zip(apps_data, poll_results):
        try:
            await TeamsAlertService.notify_system_status(
                app_id=app_info["id"],
                app_name=app_info["nome"],
                full_url=poll_res["full_url"],
                is_online=poll_res["is_online"],
                status_http=poll_res["status_http"],
                latency_ms=poll_res["latency_ms"],
                criticidade=app_info.get("criticidade", "MEDIA"),
                error_detail=str(poll_res.get("databases", {}).get("Conexão", "")) if not poll_res["is_online"] else None,
            )
        except Exception as alert_err:
            print(f"[TEAMS ALERT] Falha ao avaliar alerta: {alert_err}")

        try:
            session.add(
                HealthLog(
                    aplicacao_id=app_info["id"],
                    status_http=poll_res["status_http"],
                    latency_ms=poll_res["latency_ms"],
                    status_db=str(poll_res["databases"])[:50],
                    versao_semver=poll_res["versao_semver"],
                )
            )
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
            "active_problems_count": len(zabbix_problems),
        },
        "applications": poll_results,
        "zabbix_problems": zabbix_problems,
    }


@router.get("/historico")
async def get_health_history(
    limit: int = Query(50, ge=1, le=500),
    session: AsyncSession = Depends(get_app_db_session),
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

    return [
        {
            "id": log.id,
            "aplicacao_nome": log.aplicacao.nome if log.aplicacao else f"App #{log.aplicacao_id}",
            "status_http": log.status_http,
            "latency_ms": log.latency_ms,
            "status_db": log.status_db,
            "versao_semver": log.versao_semver,
            "checked_at": log.checked_at.isoformat() if log.checked_at else None,
            "is_online": log.status_http == 200,
        }
        for log in logs
    ]


@router.get("/aplicacoes")
async def listar_aplicacoes(session: AsyncSession = Depends(get_app_db_session)):
    """Lista todas as aplicações cadastradas."""
    stmt = select(Aplicacao)
    res = await session.execute(stmt)
    return res.scalars().all()


@router.post("/aplicacoes")
async def cadastrar_aplicacao(
    payload: AplicacaoCreate,
    request: Request,
    session: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token),
):
    """Cadastra uma nova aplicação no monitoramento com trilha de auditoria."""
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
        bancos_adicionais=_serialize_json_field(payload.bancos_adicionais),
        tipo_checagem=(payload.tipo_checagem or "HTTP").upper(),
        porta_tcp=payload.porta_tcp,
        ssh_host=payload.ssh_host,
        http_headers=_serialize_json_field(payload.http_headers),
        servicos_monitorados=_serialize_json_field(payload.servicos_monitorados),
    )
    session.add(nova_app)
    await session.commit()
    await session.refresh(nova_app)

    await registrar_auditoria(
        db=session,
        usuario=current_user.get("username", "sistema"),
        categoria="CONFIGURACAO",
        acao="CRIAR_APLICACAO",
        recurso=f"aplicacao:{nova_app.id}",
        dados_anteriores=None,
        dados_novos=payload.model_dump(),
        ip_origem=request.client.host if request.client else None,
    )
    return nova_app


@router.put("/aplicacoes/{app_id}")
async def editar_aplicacao(
    app_id: int,
    payload: AplicacaoCreate,
    request: Request,
    session: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token),
):
    """Atualiza as informações de uma aplicação existente com trilha de auditoria."""
    stmt = select(Aplicacao).where(Aplicacao.id == app_id)
    res = await session.execute(stmt)
    app = res.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Aplicação não encontrada")

    estado_anterior = {
        "nome": app.nome,
        "url_base": app.url_base,
        "tipo_checagem": getattr(app, "tipo_checagem", "HTTP"),
        "porta_tcp": getattr(app, "porta_tcp", None),
        "ssh_host": getattr(app, "ssh_host", None),
        "zabbix_host_id": app.zabbix_host_id,
        "criticidade": app.criticidade,
    }

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
    app.bancos_adicionais = _serialize_json_field(payload.bancos_adicionais)
    app.tipo_checagem = (payload.tipo_checagem or "HTTP").upper()
    app.porta_tcp = payload.porta_tcp
    app.ssh_host = payload.ssh_host
    app.http_headers = _serialize_json_field(payload.http_headers)
    app.servicos_monitorados = _serialize_json_field(payload.servicos_monitorados)

    await session.commit()
    await session.refresh(app)

    await registrar_auditoria(
        db=session,
        usuario=current_user.get("username", "sistema"),
        categoria="CONFIGURACAO",
        acao="EDITAR_APLICACAO",
        recurso=f"aplicacao:{app.id}",
        dados_anteriores=estado_anterior,
        dados_novos=payload.model_dump(),
        ip_origem=request.client.host if request.client else None,
    )
    return app


@router.delete("/aplicacoes/{app_id}")
async def excluir_aplicacao(
    app_id: int,
    request: Request,
    session: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token),
):
    """Exclui uma aplicação do monitoramento com trilha de auditoria."""
    stmt = select(Aplicacao).where(Aplicacao.id == app_id)
    res = await session.execute(stmt)
    app = res.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Aplicação não encontrada")

    estado_anterior = {"id": app.id, "nome": app.nome, "url_base": app.url_base}
    await session.delete(app)
    await session.commit()

    await registrar_auditoria(
        db=session,
        usuario=current_user.get("username", "sistema"),
        categoria="CONFIGURACAO",
        acao="EXCLUIR_APLICACAO",
        recurso=f"aplicacao:{app_id}",
        dados_anteriores=estado_anterior,
        dados_novos=None,
        ip_origem=request.client.host if request.client else None,
    )
    return {"detail": "Aplicação excluída com sucesso"}


@router.post("/test-teams-alert")
async def test_teams_alert(webhook_url: str | None = None):
    """Dispara uma mensagem de teste para o Webhook do Teams configurado no .env ou fornecido."""
    from ..services.teams_alert_service import TeamsAlertService

    ok = await TeamsAlertService.send_test_message(webhook_url=webhook_url)
    if not ok:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível enviar a mensagem de teste para o Teams. Verifique a URL do Webhook.",
        )
    return {"detail": "Mensagem de teste enviada com sucesso para o Teams!"}
