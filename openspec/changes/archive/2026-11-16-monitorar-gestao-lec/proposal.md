## Why

O sistema **Gestão interna da LEC** (`10.34.0.202`, `HC-UFPE-VP-LEC`) roda como serviço systemd nativo (`sistemalec.service` FastAPI/uvicorn `:8000`) atrás de Nginx HTTPS (`:443`, `comunicacaocirurgica.hc-ufpe.ebserh`). A inspeção via SSH comprovou que o projeto **não possui rota `/api/health`** (`src/routers/health.py` inexistente; `GET /api/health` retorna HTTP 405/404) e **não possui Zabbix Agent ativo**, exigindo sondagem HTTP em `/` + `:8000/docs` e coleta de serviço/métricas via SSH.

## What Changes

- Cadastrar a aplicação **Gestão interna da LEC** apontando para `https://10.34.0.202/` (`possui_rota_health=false`, `possui_banco_aghu=true`, `criticidade="ALTA"`).
- Configurar verificação adicional da porta `:8000/docs` (ou `/openapi.json`) para confirmar que o backend `uvicorn` está respondendo além dos arquivos estáticos do Nginx.
- Coletar CPU, RAM, disco e status dos serviços `sistemalec.service` e `nginx.service` via `SshMetricsProvider` (`root@10.34.0.202`).

## Capabilities

### New Capabilities
- `monitorar-gestao-lec`: Monitoramento HTTPS + backend FastAPI e telemetria systemd/host via SSH para o Sistema LEC.

### Modified Capabilities
<!-- Nenhuma capability existente em openspec/specs/ sofreu alteração de contrato base. -->

## Impact

`src/providers/implementations/ssh_metrics_provider.py`, `src/services/health_poller.py`, `src/routers/monitor.py` e `data/app.db`.
