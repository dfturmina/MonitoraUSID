## Context

- Host: `10.34.0.114` (`hc-ufpe-vp-metabase`), Debian GNU/Linux 12 (bookworm).
- Serviços ativos via SSH: `metabase.service` (Java `:3000`), `nginx.service` (`:80` `server_name relatorios.hc-ufpe.ebserh` -> `http://127.0.0.1:3000`, e `:1337`), `postgresql@15-main.service` (`:5432`), `zabbix-agent2.service` (`:10050`, `Hostname=HC-UFPE-VP-METABASE`).
- Testes HTTP comprovaram: `http://10.34.0.114/api/health` -> 404 (Nginx virtual host), `http://127.0.0.1:3000/api/health` -> `{"status":"ok"}`.
- Integração AGHU: `ugen_metabase`.

## Goals / Non-Goals

**Goals:**
- Eliminar falso negativo (404) ao sondar o Metabase por IP direto.
- Exibir todos os bancos sincronizados pelo Metabase via `MetabaseProvider` além do PostgreSQL interno (`5432`) e usuários ativos.

**Non-Goals:**
- Alterar a configuração de virtual host do Nginx em `10.34.0.114` sem necessidade.

## Decisions

- **Sondar `http://10.34.0.114:3000/api/health` (ou `http://relatorios.hc-ufpe.ebserh/api/health` se DNS resolver localmente)**: Acesso direto na porta `3000` independe de resolução DNS do host do MonitoraUSID; validar também o proxy Nginx via `Host: relatorios.hc-ufpe.ebserh` garante que o proxy reverso está respondendo.

## Risks / Trade-offs

- **[Ausência ou expiração de `METABASE_API_KEY`]** → Manter fallback seguro no `MetabaseProvider` mantendo a saúde principal via `/api/health` e TCP `:5432` sem quebrar o dashboard.
