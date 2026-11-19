# monitorar-master-tools Specification

## Purpose
Monitoramento multi-nó do cluster Oracle RAC e serviços web/Forms do Master Tools no MonitoraUSID. O **Master Tools** sustenta processos administrativos críticos (compras, licitações e contratos) em um cluster Oracle RAC 19c de dois nós (`rac01` em `10.34.1.120` e `rac02` em `10.34.1.121`, além dos IPs VIP/SCAN `10.34.1.122`–`126`). O MonitoraUSID precisa acompanhar a disponibilidade dos nós web/aplicação (`nginx`, Forms/Reports), os listeners Oracle (`:1521`) e o `node_exporter` (`:9100`) / `zabbix-agent2` ativos no cluster.

## Requirements

### Requirement: Multi-node HTTP and Oracle listener monitoring
The MonitoraUSID system SHALL monitor HTTP availability (`:80` / `:8877`) on `10.34.1.120` (`rac01`) and `10.34.1.121` (`rac02`) and TCP reachability of Oracle `tnslsnr` (`1521`) across the cluster IPs (`10.34.1.120` through `10.34.1.126`).

#### Scenario: one of the Oracle RAC listeners on port 1521 becomes unreachable
- **WHEN** the polling cycle executes TCP checks defined in `bancos_adicionais`
- **THEN** the failed listener IP is flagged in the application database status and triggers alert evaluation

### Requirement: Zabbix hardware and node_exporter telemetry
The MonitoraUSID system SHALL correlate `HCPE-FP-MASTER01` and `HCPE-FP-MASTER02` via `ZabbixProvider` and MAY inspect `http://10.34.1.120:9100/metrics` or SSH `ora_pmon_hcpe*` processes when diagnosing node degradation.

#### Scenario: both RAC nodes are registered with their Zabbix host IDs
- **WHEN** `/api/monitor/dashboard` collects node metrics
- **THEN** CPU, memory, disk, and active Zabbix triggers for each physical server are displayed separately
