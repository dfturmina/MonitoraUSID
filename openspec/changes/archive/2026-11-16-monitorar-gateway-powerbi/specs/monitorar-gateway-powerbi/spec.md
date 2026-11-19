## ADDED Requirements

### Requirement: Non-HTTP TCP and Zabbix monitoring mode in HealthPollerService
The MonitoraUSID system SHALL support a `TCP` (or `ZABBIX`) check mode on `Aplicacao` so that hosts without HTTP servers are evaluated via TCP port reachability and Zabbix host status instead of failing an HTTP GET request.

#### Scenario: an application such as Gateway Power BI (`10.34.0.70`) is configured with `tipo_checagem='TCP'` on port `10050` (or `3389`)
- **WHEN** `HealthPollerService.poll_single_app` runs
- **THEN** it verifies TCP connectivity (`asyncio.open_connection`), records response latency in ms, and marks `is_online=true` without performing an HTTP GET

### Requirement: Windows and Data Gateway telemetry via Zabbix
The MonitoraUSID system SHALL retrieve CPU, memory, disk `C:`, and active triggers for the Gateway Power BI host from `ZabbixProvider`.

#### Scenario: Zabbix Agent on `10.34.0.70:10050` is active and mapped to a `zabbix_host_id`
- **WHEN** `/api/monitor/dashboard` runs
- **THEN** the Gateway Power BI card displays online TCP status and Windows hardware metrics
