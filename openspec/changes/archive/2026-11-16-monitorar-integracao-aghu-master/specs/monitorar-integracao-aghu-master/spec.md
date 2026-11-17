## ADDED Requirements

### Requirement: Tomcat base availability and RoboIntegracao health check
The MonitoraUSID system SHALL probe `http://10.34.0.4:8080/` for Tomcat availability AND verify via `SshMetricsProvider` that `tomcat.service` is running with `IntegracaoMasterAghu` deployed.

#### Scenario: Tomcat responds HTTP 200 on port 8080 but `IntegracaoMasterAghu` stopped or logged critical exceptions
- **WHEN** the SSH inspection script checks `systemctl is-active tomcat` and `catalina.out` on `10.34.0.4`
- **THEN** the MonitoraUSID status surfaces degraded integration health and notifies via Teams

### Requirement: Zabbix host telemetry for HCPE-VP-TOMCAT
The MonitoraUSID system SHALL fetch CPU, memory, and disk telemetry for `HCPE-VP-TOMCAT` from `ZabbixProvider`.

#### Scenario: Zabbix Agent (`10.34.0.4:10050`) is active
- **WHEN** the dashboard endpoint queries `ZabbixProvider`
- **THEN** VM resource metrics and active Zabbix triggers appear on the card
