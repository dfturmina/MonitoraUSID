## Context

- Host: `10.34.0.191` (`hc-ufpe-vp-sat-quimio`), Debian GNU/Linux 13 (trixie).
- Containers Podman: `quimio_db_app` (`postgres:15-alpine`, `0.0.0.0:5432->5432/tcp`, status `healthy`), `quimio_app` (`0.0.0.0:8080->8000/tcp`, FastAPI uvicorn).
- Proxy web: `nginx.service` (`:80`/`:443`); `https://10.34.0.191/api/health` retornou HTTP 200 `{"status":"healthy","service":"HC-UFPE | Sistema de Gestão de Quimioterapia","version":"1.0.0"}`.
- `zabbix-agent` e `zabbix-agent2` inativos; acesso SSH `root@10.34.0.191` validado.

## Goals / Non-Goals

**Goals:**
- Complementar o `/api/health` enxuto do Quimo com checagem real do PostgreSQL (`5432`) e métricas Podman/SO via SSH.
- Manter monitoramento ponta a ponta via Nginx HTTPS (`443`).

**Non-Goals:**
- Alterar o container `quimio_app` em produção para expandir o JSON de `/api/health`.

## Decisions

- **Usar `bancos_adicionais` para `10.34.0.191:5432` + `SshMetricsProvider` (`podman ps`)**: Permite detectar falha no banco mesmo que o endpoint `/api/health` atual da aplicação não teste conexão SQL internamente.

## Risks / Trade-offs

- **[Diferença de comportamento entre `podman ps` e `docker ps` no `SshMetricsProvider`]** → Implementar detecção automática (`command -v podman || command -v docker`) no comando SSH remoto.
