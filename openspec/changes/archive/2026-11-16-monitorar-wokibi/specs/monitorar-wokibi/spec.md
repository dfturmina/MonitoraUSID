## ADDED Requirements

### Requirement: AI service /health and Next.js frontend checks for Wokibi
The MonitoraUSID system SHALL probe `http://10.34.0.219:8080/health`, validate HTTP 200 with JSON `ready == true`, verify `http://10.34.0.219:3000/` availability, and check TCP connectivity to MongoDB (`10.34.0.219:27017`).

#### Scenario: `app_anony.py` returns `{"ready": false}` or HTTP error on port 8080
- **WHEN** `HealthPollerService` polls Wokibi
- **THEN** Wokibi is flagged as offline/degraded even if port 3000 responds

### Requirement: SSH host telemetry fallback when Zabbix Agent is absent
The MonitoraUSID system MUST collect CPU, memory (used/total GB), disk (used/total GB), and Docker container state (`wokibi-mongodb`) via `SshMetricsProvider` when `zabbix_host_id` is absent.

#### Scenario: no Zabbix Agent is active on `10.34.0.219`
- **WHEN** `/api/monitor/dashboard` builds the metrics payload for Wokibi
- **THEN** the card displays real-time host metrics collected via `asyncssh`/SSH in the same schema used by `ZabbixProvider`
