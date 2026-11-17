# monitorar-integracao-aghu-master Specification

## Purpose
Monitoramento do servidor Tomcat `robot-java` e verificação de saúde do listener background `RoboIntegracao` via SSH e Zabbix. A VM `robot-java` (`10.34.0.4`, hostname Zabbix `HCPE-VP-TOMCAT`) executa no Apache Tomcat 8 o listener `IntegracaoMasterAghu.war` (`RoboIntegracao`), responsável por sincronizar dados do AGHU (`ugen_integra` `:6544`) para o Master Tools (`:1521`). Como o WAR é um *ServletContextListener* sem endpoint HTTP dedicado (`/IntegracaoMasterAghu/` retorna 404), testar apenas HTTP é insuficiente para saber se o robô está vivo.

## Requirements

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
