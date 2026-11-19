## ADDED Requirements

### Requirement: HTTPS availability check for MEWS login endpoint
The MonitoraUSID system SHALL probe `https://10.34.0.197/login` (`possui_rota_health=false`, TLS verification configurable for internal certs) and measure response time.

#### Scenario: the Next.js container or Nginx proxy stops responding on port 443
- **WHEN** `HealthPollerService` polls Escala de MEWS
- **THEN** the application is marked offline and triggers Teams alert notification

### Requirement: Docker container and PostgreSQL health monitoring via SSH
The MonitoraUSID system MUST inspect `cinco_hc-app-1`, `cinco_hc-nginx-1`, and `cinco_hc-postgres-1` via `SshMetricsProvider` (`adm-local@10.34.0.197`) and collect CPU, RAM, and disk metrics in the absence of Zabbix Agent.

#### Scenario: `cinco_hc-postgres-1` is unhealthy or stopped while Nginx still serves static assets
- **WHEN** `SshMetricsProvider` runs `docker ps` and resource commands over SSH
- **THEN** the PostgreSQL database status reflects the unhealthy container state and host metrics are updated on the dashboard
