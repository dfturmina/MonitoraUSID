## Why

O **Quimo** (`10.34.0.191`, `hc-ufpe-vp-sat-quimio`) opera com Nginx (`:443`) fazendo proxy para containers Podman (`quimio_app` FastAPI `:8080` e `quimio_db_app` PostgreSQL 15 `:5432`), além da integração AGHU (`ugen_quimio`). Sua rota `/api/health` retorna apenas `{"status":"healthy","service":...,"version":"1.0.0"}` (sem lista de bancos) e o servidor **não possui Zabbix Agent ativo**, exigindo combinação de `/api/health`, probe TCP `:5432` e coleta SSH.

## What Changes

- Cadastrar a aplicação **Quimo** apontando para `https://10.34.0.191` (`possui_rota_health=true`, `url_health="/api/health"`, `possui_banco_aghu=true`, `criticidade="ALTA"`).
- Configurar `bancos_adicionais` com `[{"nome": "PostgreSQL Quimo", "host": "10.34.0.191", "porta": 5432}]` e ajustando o `HealthPollerService` para não assumir `"Banco Aplicação": "connected"` quando `databases` vier ausente e houver `bancos_adicionais` sondados.
- Coletar CPU, RAM, disco e status dos containers Podman (`quimio_app`, `quimio_db_app`) via `SshMetricsProvider` (`root@10.34.0.191`).

## Capabilities

### New Capabilities
- `monitorar-quimo`: Monitoramento do Quimo via HTTPS /api/health, probe TCP PostgreSQL 5432, e coleta de métricas/containers Podman via SSH.

### Modified Capabilities
<!-- Nenhuma capability existente em openspec/specs/ sofreu alteração de contrato base. -->

## Impact

`src/providers/implementations/ssh_metrics_provider.py`, `src/services/health_poller.py`, `src/routers/monitor.py` e `data/app.db`.
