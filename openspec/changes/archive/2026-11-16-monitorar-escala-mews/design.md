## Context

- Host: `10.34.0.197` (`hc-ufpe-vp-sat-mews`), Debian GNU/Linux 13 (trixie).
- Containers Docker ativos: `cinco_hc-nginx-1` (`:80`->301->`:443`), `cinco_hc-app-1` (Next.js `:3000` interno, `/login` retorna HTTP 200), `cinco_hc-postgres-1` (`postgres:16-alpine`, `5432/tcp` apenas na rede interna Docker, status `(healthy)`).
- Runner ativo: `actions.runner.HU-INNOVATION-CINCO_HC.hc-ufpe-vp-sat-mews.service`.
- `zabbix-agent` e `zabbix-agent2` inativos; usuário SSH validado: `adm-local@10.34.0.197`.

## Goals / Non-Goals

**Goals:**
- Monitorar disponibilidade HTTPS e saúde interna do `cinco_hc-postgres-1` sem expor a porta 5432 externamente.
- Coletar métricas de CPU/RAM/Disco da VM via SSH no padrão visual do MonitoraUSID.

**Non-Goals:**
- Alterar o repositório `/home/adm-local/CINCO_HC` ou expor a porta 5432 no `docker-compose.yml`.

## Decisions

- **Monitorar `https://10.34.0.197/login` em vez de `/`**: A raiz `/` retorna `307 Temporary Redirect` para `/login`; sondar `/login` diretamente valida a renderização SSR do Next.js (HTTP 200).
- **Ler o healthcheck do `cinco_hc-postgres-1` via `docker ps` no `SshMetricsProvider`**: Como o Postgres não publica porta no host (`5432/tcp` interno), `docker ps` informa com precisão se está `healthy` sem comprometer o isolamento de rede.

## Risks / Trade-offs

- **[Permissão do usuário `adm-local` para executar `docker ps`]** → Confirmar na implantação se `adm-local` pertence ao grupo `docker` ou ajustar regra `sudo -n docker ps` sem senha.
