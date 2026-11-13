"""
Serviço de Alertas e Notificações para o Microsoft Teams (TeamsAlertService)
=============================================================================
Despacha Adaptive Cards estilizados para Webhooks do Microsoft Teams / Power Automate Workflows
quando sistemas monitorados entram em estado de indisponibilidade (queda) ou restabelecimento (recuperação).
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import httpx

from ..config import settings

logger = logging.getLogger("teams_alert")


class TeamsAlertService:
    """Gerencia e despacha alertas de saúde para o Microsoft Teams."""

    # Dicionário em memória para rastrear o último status conhecido de cada aplicação
    # chave: aplicacao_id -> valor: bool (is_online)
    _last_known_status: Dict[int, bool] = {}

    # Contador de falhas consecutivas para tolerância a micro-oscilações de rede (Anti-Flapping)
    _consecutive_failures: Dict[int, int] = {}

    # Rastreia se o alerta de QUEDA foi realmente entregue com sucesso ao Teams
    # (Evita enviar alerta de 'Recuperado' fantasma se a queda nem foi entregue)
    _down_alert_delivered: Dict[int, bool] = {}

    @classmethod
    def get_webhook_urls(cls) -> List[str]:
        """Retorna lista de URLs de Webhook configuradas no .env (suporta múltiplas separadas por vírgula)."""
        raw = settings.TEAMS_WEBHOOK_URL or ""
        urls = [u.strip().strip('"').strip("'") for u in raw.split(",") if u.strip().strip('"').strip("'")]
        return urls

    @classmethod
    async def send_adaptive_card(cls, card_content: Dict[str, Any], webhook_url: Optional[str] = None) -> bool:
        """Envia um Adaptive Card para o(s) Webhook(s) do Teams via HTTP POST assíncrono."""
        if not settings.TEAMS_ALERT_ENABLED:
            logger.info("Alertas do Microsoft Teams desativados via TEAMS_ALERT_ENABLED=False.")
            return False

        urls = [webhook_url] if webhook_url else cls.get_webhook_urls()
        if not urls:
            logger.warning("Nenhuma URL de Webhook do Teams configurada em TEAMS_WEBHOOK_URL.")
            return False

        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": card_content
                }
            ]
        }

        success_all = True
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            for url in urls:
                try:
                    resp = await client.post(url, json=payload)
                    if resp.status_code in (200, 202):
                        logger.info(f"Notificação entregue com sucesso ao Teams (HTTP {resp.status_code}).")
                    else:
                        logger.error(f"Erro ao enviar para o Teams ({url[:45]}...): HTTP {resp.status_code} - {resp.text}")
                        success_all = False
                except Exception as err:
                    logger.error(f"Falha de conexão ao enviar alerta para o Teams: {err}")
                    success_all = False

        return success_all

    @classmethod
    async def notify_system_status(
        cls,
        app_id: int,
        app_name: str,
        full_url: str,
        is_online: bool,
        status_http: int = 0,
        latency_ms: int = 0,
        criticidade: str = "MEDIA",
        error_detail: Optional[str] = None,
        force_send: bool = False
    ) -> bool:
        """
        Avalia o status de uma aplicação e notifica o Teams se houve transição de estado confirmada:
        - ONLINE -> OFFLINE (🚨 Alerta de Queda após confirmação de falhas consecutivas)
        - OFFLINE -> ONLINE (🟢 Alerta de Recuperação apenas se a queda foi notificada com sucesso)
        """
        now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

        if is_online:
            # Reseta o contador de falhas consecutivas
            cls._consecutive_failures[app_id] = 0

            was_offline = cls._last_known_status.get(app_id) is False
            was_alert_delivered = cls._down_alert_delivered.get(app_id, False)

            # Atualiza o último status conhecido
            cls._last_known_status[app_id] = True

            # Só dispara mensagem de RECUPERADO se o sistema estava offline E o alerta de queda foi entregue
            if (was_offline and was_alert_delivered) or force_send:
                cls._down_alert_delivered[app_id] = False

                card_content = {
                    "type": "AdaptiveCard",
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "Container",
                            "style": "good",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "✅ RECUPERADO: Sistema Voltou a Operar (ONLINE)",
                                    "weight": "Bolder",
                                    "size": "Large",
                                    "color": "Good"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"O sistema **{app_name}** foi restabelecido e está respondendo normalmente.",
                                    "wrap": True,
                                    "spacing": "Small"
                                }
                            ]
                        },
                        {
                            "type": "FactSet",
                            "spacing": "Medium",
                            "facts": [
                                {"title": "Aplicação:", "value": app_name},
                                {"title": "Latência Atual:", "value": f"{latency_ms} ms"},
                                {"title": "Status HTTP:", "value": f"{status_http} OK" if status_http else "OK"},
                                {"title": "Horário de Retorno:", "value": now_str}
                            ]
                        },
                        {
                            "type": "ActionSet",
                            "spacing": "Medium",
                            "actions": [
                                {
                                    "type": "Action.OpenUrl",
                                    "title": "🔗 Acessar Aplicação",
                                    "url": full_url
                                }
                            ]
                        }
                    ]
                }
                logger.info(f"Disparando aviso de recuperação para o Teams: {app_name} ONLINE")
                return await cls.send_adaptive_card(card_content)

            return False

        else:
            # Incrementa o contador de falhas consecutivas
            current_failures = cls._consecutive_failures.get(app_id, 0) + 1
            cls._consecutive_failures[app_id] = current_failures

            # Exige pelo menos 2 falhas consecutivas para confirmar a queda real e descartar oscilação rápida
            REQUIRED_FAILURES = 2
            if current_failures < REQUIRED_FAILURES and not force_send:
                logger.warning(
                    f"Oscilação temporária em '{app_name}' ({current_failures}/{REQUIRED_FAILURES}). "
                    f"Aguardando próxima confirmação para evitar alarme falso."
                )
                return False

            # Se já estávamos cientes de que estava offline e já enviamos o alerta, não repete (Anti-Spam)
            already_offline = cls._last_known_status.get(app_id) is False
            already_alerted = cls._down_alert_delivered.get(app_id, False)

            if already_offline and already_alerted and not force_send:
                return False

            # Marca como offline
            cls._last_known_status[app_id] = False
            err_msg = error_detail or (f"HTTP {status_http}" if status_http > 0 else "Falha de Conexão / Timeout")

            card_content = {
                "type": "AdaptiveCard",
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.4",
                "body": [
                    {
                        "type": "Container",
                        "style": "attention",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "🚨 ALERTA: Sistema Indisponível (OFFLINE)",
                                "weight": "Bolder",
                                "size": "Large",
                                "color": "Attention"
                            },
                            {
                                "type": "TextBlock",
                                "text": f"O sistema **{app_name}** parou de responder às sondagens de saúde.",
                                "wrap": True,
                                "spacing": "Small"
                            }
                        ]
                    },
                    {
                        "type": "FactSet",
                        "spacing": "Medium",
                        "facts": [
                            {"title": "Aplicação:", "value": app_name},
                            {"title": "Criticidade:", "value": criticidade.upper()},
                            {"title": "Diagnóstico:", "value": err_msg},
                            {"title": "URL:", "value": full_url},
                            {"title": "Horário da Queda:", "value": now_str}
                        ]
                    },
                    {
                        "type": "ActionSet",
                        "spacing": "Medium",
                        "actions": [
                            {
                                "type": "Action.OpenUrl",
                                "title": "🔗 Abrir Sistema",
                                "url": full_url
                            }
                        ]
                    }
                ]
            }
            logger.warning(f"Disparando alerta de queda para o Teams: {app_name} OFFLINE")
            sent_ok = await cls.send_adaptive_card(card_content)
            if sent_ok:
                cls._down_alert_delivered[app_id] = True
            return sent_ok

    @classmethod
    async def send_test_message(cls, webhook_url: Optional[str] = None) -> bool:
        """Envia mensagem interativa de teste para validar o Webhook."""
        now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        card_content = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "Container",
                    "style": "emphasis",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "🩺 Monitora USID — HC-UFPE",
                            "weight": "Bolder",
                            "size": "Large",
                            "color": "Accent"
                        },
                        {
                            "type": "TextBlock",
                            "text": "✅ Teste de Integração com o Microsoft Teams concluído com sucesso!",
                            "weight": "Bolder",
                            "size": "Medium",
                            "color": "Good",
                            "spacing": "Small"
                        }
                    ]
                },
                {
                    "type": "FactSet",
                    "spacing": "Medium",
                    "facts": [
                        {"title": "Origem:", "value": "Monitora USID (SETISD)"},
                        {"title": "Destino:", "value": "Chat Pessoal / Grupo Teams"},
                        {"title": "Status:", "value": "🟢 Operacional e Conectado"},
                        {"title": "Horário:", "value": now_str}
                    ]
                },
                {
                    "type": "TextBlock",
                    "text": "Os alertas automáticos de queda e recuperação de sistemas estão ativos e configurados.",
                    "wrap": True,
                    "size": "Small",
                    "spacing": "Medium"
                }
            ]
        }
        return await cls.send_adaptive_card(card_content, webhook_url=webhook_url)
