# monitorar-uti-manager Specification

## Purpose
Integração direta da rota /api/health do Reserva UTI (bancos e usuários ativos) com o monitoramento Zabbix da VM HC-UFPE-VP-SAT-UTI. O **UTI Manager** (`10.34.0.192`, `hc-ufpe-vp-sat-uti`) é o sistema mais alinhado ao padrão do framework: executa em Podman Compose (`hc-uti.service`), possui `zabbix-agent2` ativo (`HC-UFPE-VP-SAT-UTI`) e já expõe uma rota `/api/health` completa (`https://10.34.0.192/api/health`) retornando `version`, `active_users` e `databases: {"app_db": "connected", "aghu_postgres": "connected"}`. Resta integrá-lo formalmente no MonitoraUSID.

## Requirements

### Requirement: Standard /api/health contract consumption for UTI Manager
The MonitoraUSID system SHALL poll `https://10.34.0.192/api/health` and extract `version`, `active_users`, and every key in `databases` (`app_db`, `aghu_postgres`) into the dashboard card and `health_logs`.

#### Scenario: `https://10.34.0.192/api/health` returns HTTP 200 with `active_users: 3` and `databases: {"app_db": "connected", "aghu_postgres": "connected"}`
- **WHEN** `HealthPollerService.poll_single_app` processes the response
- **THEN** the card displays version `1.8.1`, `3` active users, and both `app_db` and `aghu_postgres` as connected

### Requirement: Zabbix Agent 2 correlation for HC-UFPE-VP-SAT-UTI
The MonitoraUSID system SHALL query `ZabbixProvider` with the `zabbix_host_id` of `HC-UFPE-VP-SAT-UTI` for CPU, RAM, disk, and active triggers.

#### Scenario: the Zabbix host ID for `HC-UFPE-VP-SAT-UTI` is saved on the application record
- **WHEN** `/api/monitor/dashboard` executes
- **THEN** real hardware metrics and any active Zabbix triggers are attached to the UTI Manager payload
