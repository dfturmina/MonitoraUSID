## ADDED Requirements

### Requirement: Health polling and TCP PostgreSQL verification for Quimo
The MonitoraUSID system SHALL poll `https://10.34.0.191/api/health` for HTTP 200 and `version`, probe TCP `10.34.0.191:5432` (`quimio_db_app`), and preserve declared AGHU status.

#### Scenario: `quimio_db_app` stops accepting connections on port 5432 while `quimio_app` returns HTTP 200 on `/api/health`
- **WHEN** `HealthPollerService` executes HTTP and `bancos_adicionais` TCP checks
- **THEN** the database map reports the failure on `PostgreSQL Quimo` (`10.34.0.191:5432`)

### Requirement: Podman and VM telemetry via SSH for Quimo
The MonitoraUSID system MUST collect CPU, memory (GB/%), disk (GB/%), and Podman container status (`quimio_app`, `quimio_db_app`) via `SshMetricsProvider` (`root@10.34.0.191`).

#### Scenario: no Zabbix Agent is active on `10.34.0.191`
- **WHEN** `/api/monitor/dashboard` gathers infrastructure telemetry for Quimo
- **THEN** host resource metrics and container health are populated in the dashboard payload
