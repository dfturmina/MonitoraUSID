## Why

O **Metabase** (`10.34.0.114`, `hc-ufpe-vp-metabase`) já possui integração parcial no `MetabaseProvider`, mas a inspeção via SSH revelou que o Nginx (`:80`) filtra por `server_name relatorios.hc-ufpe.ebserh` — requisições diretas para `http://10.34.0.114/api/health` retornam **404**, enquanto `http://127.0.0.1:3000/api/health` (ou com header `Host`) retorna `{"status":"ok"}`. É necessário corrigir a sondagem e consolidar o monitoramento de PostgreSQL local (`:5432`) e Zabbix (`HC-UFPE-VP-METABASE`).

## What Changes

- Cadastrar/atualizar a aplicação **Metabase** apontando para `http://10.34.0.114:3000` (ou `http://relatorios.hc-ufpe.ebserh` com suporte a header `Host`), rota `url_health="/api/health"` (`{"status":"ok"}`).
- Adaptar `HealthPollerService` para reconhecer o contrato nativo do Metabase (`{"status": "ok"}`) sem marcar `Banco Aplicação` genérico ou falhar na leitura de `databases`, delegando a lista real de bancos ao `MetabaseProvider` (`/api/database`).
- Incluir checagem TCP do banco interno `postgresql@15-main` (`10.34.0.114:5432`) e vincular `zabbix_host_id` de `HC-UFPE-VP-METABASE`.

## Capabilities

### New Capabilities
- `monitorar-metabase`: Correção da sondagem `/api/health` do Metabase, monitoramento do PostgreSQL interno e sincronização completa com MetabaseProvider e Zabbix.

### Modified Capabilities
<!-- Nenhuma capability existente em openspec/specs/ sofreu alteração de contrato base. -->

## Impact

`src/services/health_poller.py`, `src/providers/implementations/metabase_provider.py`, `src/routers/monitor.py` e cadastro em `data/app.db`.
