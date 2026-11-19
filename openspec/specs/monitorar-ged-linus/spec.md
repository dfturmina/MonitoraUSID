# monitorar-ged-linus Specification

## Purpose
Monitoramento do GED Linus (`e-custodia`) cobrindo Nginx/Puma, NFSv4, espaço em disco crítico de documentos e Zabbix/SSH. O **GED Linus** (`10.34.0.124`, `hc-ufpe-vp-ged`) hospeda o sistema Rails `e-custodia` (via Puma + Nginx `:80`) e exporta/monta armazenamento NFSv4 (`:2049`) para gestão eletrônica de documentos. A inspeção SSH detectou que o `zabbix-agent2` local está com `Hostname=Zabbix server` genérico no arquivo de configuração, o que pode impedir o Zabbix de associar corretamente o host, exigindo correção ou fallback via SSH.

## Requirements

### Requirement: HTTP and Puma/NFS availability for GED Linus
The MonitoraUSID system SHALL check `http://10.34.0.124/usuarios/sign_in` for HTTP 200 availability and monitor the `puma` application process and NFS (`2049`) / disk capacity.

#### Scenario: the Rails Puma socket stops serving or disk usage exceeds critical threshold
- **WHEN** the polling cycle executes HTTP and `SshMetricsProvider` checks on `10.34.0.124`
- **THEN** the GED Linus card reports degraded/offline state and alerts via Teams

### Requirement: Telemetry fallback when Zabbix Hostname mismatches
The MonitoraUSID system SHALL use `ZabbixProvider` when a valid `zabbix_host_id` is matched, or fall back to `SshMetricsProvider` (`ubuntu@10.34.0.124`) to provide CPU, RAM, and disk GB metrics.

#### Scenario: `zabbix_agent2` on `10.34.0.124` has a mismatched `Hostname=Zabbix server`
- **WHEN** `/api/monitor/dashboard` requests host metrics for GED Linus
- **THEN** the system still displays real CPU, RAM, and disk metrics collected via SSH
