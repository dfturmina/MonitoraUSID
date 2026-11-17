## Context

- Host: `10.34.0.202` (`HC-UFPE-VP-LEC`), Debian GNU/Linux 13 (trixie).
- Serviços ativos via SSH: `sistemalec.service` (`/var/app/sistemalec`, `uvicorn src.main:app` na porta `:8000`) e `nginx.service` (`:80`->301->`:443`, `comunicacaocirurgica.hc-ufpe.ebserh`).
- Rotas observadas: `/var/app/sistemalec/src/routers/` não tem `health.py`; `https://10.34.0.202/` retorna HTML 200 e `http://10.34.0.202:8000/docs` retorna Swagger 200.
- `zabbix-agent` e `zabbix-agent2` inativos; integração AGHU declarada (`ugen_gestaolec` `:5432`).

## Goals / Non-Goals

**Goals:**
- Monitorar disponibilidade do Sistema LEC sem depender da existência da rota `/api/health` no servidor remoto.
- Supervisionar `sistemalec.service` e recursos de VM via SSH.

**Non-Goals:**
- Editar o código em `/var/app/sistemalec` nesta change (escopo focado no MonitoraUSID).

## Decisions

- **Sondar `https://10.34.0.202/` (`possui_rota_health=false`) + validar `sistemalec.service` via `SshMetricsProvider`**: Como `nginx` encaminha `/` para `127.0.0.1:8000`, se o FastAPI cair o Nginx responde 502 (que `status_code < 500` já marca como offline!); a checagem systemd via SSH adiciona diagnóstico preciso da causa.

## Risks / Trade-offs

- **[Falso positivo caso `/docs` seja desativado no futuro em produção]** → Basear o status online em `https://10.34.0.202/` (`< 500`) combinado com `systemctl is-active sistemalec` via SSH.
