## Context

- Host: `10.34.0.192` (`hc-ufpe-vp-sat-uti`), Debian GNU/Linux 13 (trixie).
- Serviços ativos via SSH: `hc-uti.service` (Podman Compose com `hc-uti-backend` FastAPI `:8000` e `hc-uti-nginx` `:80`/`:443`) e `zabbix-agent2.service` (`:10050`, `Hostname=HC-UFPE-VP-SAT-UTI`).
- Payload real observado em `https://10.34.0.192/api/health`: `{"status":"healthy","app_name":"Reserva UTI","version":"1.8.1","active_users":3,"databases":{"app_db":"connected","aghu_postgres":"connected"}}`.

## Goals / Non-Goals

**Goals:**
- Integrar imediatamente o UTI Manager como caso de referência completo (`/api/health` + Zabbix).
- Preservar a contagem real de `active_users` e status separado de `app_db` e `aghu_postgres`.

**Non-Goals:**
- Modificar o código do `hc-uti-backend` em `10.34.0.192`, pois sua rota `/api/health` já atende ao contrato.

## Decisions

- **Sondar via Nginx HTTPS (`https://10.34.0.192/api/health`) em vez de `:8000` direto**: Valida ponta a ponta tanto o proxy reverso Nginx quanto o backend FastAPI e o certificado SSL.

## Risks / Trade-offs

- **[Truncamento de `status_db` em `HealthLog` (`[:50]`)]** → Avaliar ampliação ou serialização resumida caso o JSON de múltiplos bancos ultrapasse 50 caracteres no histórico.
