# monitorar-realblood Specification

## Purpose
Monitoramento HTTP das duas VMs Windows do RealBlood, checagem TCP do SQL Server (1433) e integração com Zabbix. O **RealBlood** (agência transfusional, criticidade assistencial alta) roda em duas VMs Windows: `10.34.0.218` (`HC-UFPE-VP-REALBLOOD-APP`, portas abertas `[80, 443, 3389]`) e `10.34.0.217` (`HC-UFPE-VP-REALBLOOD-BD`, portas abertas `[80, 443, 1433, 3389]`), integradas ao AGHU (`ugen_realblood` `:6544`). Como são servidores Windows sem SSH (porta 22 fechada) e sem Zabbix Agent respondendo na porta `10050`, o monitoramento precisa combinar sondagem HTTP IIS, teste TCP do SQL Server (`1433`) e correlação Zabbix.

## Requirements

### Requirement: HTTP and SQL Server TCP availability checks for RealBlood
The MonitoraUSID system SHALL probe `http://10.34.0.218/` (`possui_rota_health=false`) and test TCP connectivity to the RealBlood SQL Server (`10.34.0.217:1433`) via `bancos_adicionais`.

#### Scenario: SQL Server on `10.34.0.217:1433` becomes unreachable while IIS on `.218` responds HTTP 200
- **WHEN** `HealthPollerService` polls RealBlood
- **THEN** the SQL Server dependency is marked with connection error in the database map

### Requirement: Windows Zabbix host integration for RealBlood
The MonitoraUSID system SHALL retrieve available Windows telemetry (CPU, memory, disk `C:`, ICMP/agent status) from `ZabbixProvider` when `HC-UFPE-VP-REALBLOOD-APP` is registered in Zabbix.

#### Scenario: the Windows Zabbix host reports `C:` disk and memory metrics
- **WHEN** `ZabbixProvider.get_host_metrics` parses the host items
- **THEN** the Windows metrics are normalized into the standard GB/percentage format on the dashboard
