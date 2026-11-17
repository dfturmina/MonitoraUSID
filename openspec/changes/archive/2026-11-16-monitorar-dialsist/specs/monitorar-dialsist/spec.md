## ADDED Requirements

### Requirement: HTTP and database connectivity checks for Dialsist
The MonitoraUSID system SHALL probe `http://10.34.0.83/ufpeds4/` (`possui_rota_health=false`) and test TCP connectivity to local MySQL (`10.34.0.83:3306`) and AGHU Slave (`10.34.0.92:5432`).

#### Scenario: MySQL on `10.34.0.83:3306` or Apache `:80` goes down
- **WHEN** the polling cycle executes for Dialsist
- **THEN** the dashboard marks the failed dependency and records the incident in `health_logs`

### Requirement: Zabbix telemetry for HC-UFPE-VP-DIALSIST
The MonitoraUSID system SHALL retrieve hardware metrics and active problems for `HC-UFPE-VP-DIALSIST` from `ZabbixProvider`.

#### Scenario: the Zabbix host ID for `HC-UFPE-VP-DIALSIST` is configured
- **WHEN** the dashboard loads
- **THEN** CPU, memory, disk usage, and Zabbix alerts are shown on the Dialsist card
