## Why

O sistema **Escala de MEWS** (`10.34.0.197`, `hc-ufpe-vp-sat-mews`) roda em Docker Compose (`cinco_hc-nginx-1` `:443`, `cinco_hc-app-1` Next.js `:3000` e `cinco_hc-postgres-1` PostgreSQL 16 interno sem porta exposta no host), além de um runner do GitHub Actions. A VM **não possui Zabbix Agent ativo** e o Next.js não possui rota `/api/health`, exigindo sondagem HTTPS em `/login` e coleta de métricas/containers via SSH (`adm-local@10.34.0.197`).

## What Changes

- Cadastrar a aplicação **Escala de MEWS** apontando para `https://10.34.0.197/login` (`possui_rota_health=false`, `criticidade=ALTA`).
- Integrar o `SshMetricsProvider` (`adm-local@10.34.0.197`) para coletar CPU, RAM (GB/%), disco (GB/%), e inspecionar o status/healthcheck dos containers Docker (`cinco_hc-nginx-1`, `cinco_hc-app-1`, `cinco_hc-postgres-1`).
- Expor no mapa `databases` do card a saúde real do container `cinco_hc-postgres-1` (reportado como `(healthy)` no Docker) obtida via SSH, uma vez que a porta `5432` não está exposta fora da rede Docker.

## Capabilities

### New Capabilities
- `monitorar-escala-mews`: Sondagem HTTPS da interface Next.js e coleta de métricas de host, containers Docker e healthcheck do PostgreSQL interno do MEWS via SSH.

### Modified Capabilities
<!-- Nenhuma capability existente em openspec/specs/ sofreu alteração de contrato base. -->

## Impact

`src/providers/implementations/ssh_metrics_provider.py`, `src/services/health_poller.py`, `src/routers/monitor.py` e `data/app.db`.
