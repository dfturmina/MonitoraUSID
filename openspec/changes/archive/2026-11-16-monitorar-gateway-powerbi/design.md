## Context

- VM Windows: `10.34.0.70` (`HC-UFPE-VP-ONPREMISSES` / renomeação prevista `HC-UFPE-VP-GATEWAY_BI`).
- Varredura de portas: `[3389, 10050]` abertas; HTTP `:80`/`:443` inacessíveis (timeout); SSH `:22` inacessível (timeout).
- Integração AGHU: `ugen_bi` (porta `6544`).
- No código atual (`src/services/health_poller.py`), `possui_rota_health=False` ainda executa `httpx.AsyncClient().get(url_base)`.

## Goals / Non-Goals

**Goals:**
- Permitir que o MonitoraUSID monitore serviços de infraestrutura/gateway que não possuem interface web HTTP.
- Acompanhar disponibilidade do Gateway Power BI e métricas Windows no mesmo dashboard.

**Non-Goals:**
- Instalar um servidor web artificial ou agente SSH apenas para responder HTTP em `10.34.0.70`.

## Decisions

- **Adicionar campo `tipo_checagem` (`HTTP` default, `TCP`, `ZABBIX`) em `Aplicacao`**: Mantém 100% de retrocompatibilidade com aplicações web existentes (`HTTP` como padrão) e desbloqueia monitoramento de serviços Windows/daemons sem HTTP.

## Risks / Trade-offs

- **[Migração de schema no SQLite `data/app.db` existente]** → Tratar nova coluna com valor default `'HTTP'` via Alembic ou `ALTER TABLE` seguro no startup.
