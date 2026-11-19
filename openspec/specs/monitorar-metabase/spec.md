# monitorar-metabase Specification

## Purpose
Correção da sondagem `/api/health` do Metabase, monitoramento do PostgreSQL interno e sincronização completa com MetabaseProvider e Zabbix. O **Metabase** (`10.34.0.114`, `hc-ufpe-vp-metabase`) já possui integração parcial no `MetabaseProvider`, mas a inspeção via SSH revelou que o Nginx (`:80`) filtra por `server_name relatorios.hc-ufpe.ebserh` — requisições diretas para `http://10.34.0.114/api/health` retornam **404**, enquanto `http://127.0.0.1:3000/api/health` (ou com header `Host`) retorna `{"status":"ok"}`. É necessário corrigir a sondagem e consolidar o monitoramento de PostgreSQL local (`:5432`) e Zabbix (`HC-UFPE-VP-METABASE`).

## Requirements

### Requirement: Native Metabase /api/health contract handling
The MonitoraUSID system SHALL probe the Metabase health endpoint (`:3000/api/health` or via `relatorios.hc-ufpe.ebserh`) and interpret HTTP 200 with `{"status": "ok"}` as online without requiring a `databases` key inside `/api/health`.

#### Scenario: Metabase `/api/health` returns `{"status": "ok"}`
- **WHEN** `HealthPollerService` polls the Metabase application
- **THEN** the application is marked online and `MetabaseProvider` populates all configured database statuses and active users

### Requirement: Local PostgreSQL 15 and Zabbix Agent 2 monitoring
The MonitoraUSID system SHALL verify TCP connectivity on `10.34.0.114:5432` (PostgreSQL metadata DB) and retrieve VM metrics from `ZabbixProvider` for `HC-UFPE-VP-METABASE`.

#### Scenario: PostgreSQL on port 5432 stops listening
- **WHEN** the polling cycle checks `bancos_adicionais`
- **THEN** the PostgreSQL metadata DB failure is surfaced immediately
