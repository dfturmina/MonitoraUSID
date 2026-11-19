# monitorar-csh-maqueiros Specification

## Purpose
Sondagem HTTP da tela de acesso do CSH Maqueiros, checagem TCP do MariaDB local e correlação com o host Zabbix HCPE-VP-MAQUEIROS. O sistema **CSH (Maqueiros) - Produção** (`10.34.0.111`, VM `hcpe-vp-maqueiros`) gerencia os chamados e serviços de hotelaria/maqueiros integrados ao AGHU (`ugen_integra`), porém ainda não está cadastrado nem sondado pelo **MonitoraUSID**. A inspeção via SSH identificou stack Apache/PHP (`:80`), MariaDB local (`:3306`) e `zabbix-agent2` ativo (`HCPE-VP-MAQUEIROS`), permitindo monitoramento completo sem intervenção no código legado.

## Requirements

### Requirement: HTTP availability check for CSH Maqueiros
The MonitoraUSID system SHALL periodically poll `http://10.34.0.111/admin_3/loginAD.php` via HTTP GET (`possui_rota_health=false`) to determine online status and response time in milliseconds.

#### Scenario: CSH Maqueiros web interface is reachable
- **WHEN** `http://10.34.0.111/admin_3/loginAD.php` returns HTTP 200
- **THEN** the application card is marked online with measured response time in `health_logs`

### Requirement: Local MariaDB and AGHU dependency monitoring
The MonitoraUSID system MUST monitor TCP connectivity to the local MariaDB instance (`10.34.0.111:3306`) and reflect the declared AGHU integration (`ugen_integra`) in the application's database status map.

#### Scenario: MariaDB port 3306 stops accepting TCP connections
- **WHEN** the dynamic `bancos_adicionais` TCP probe fails on `10.34.0.111:3306`
- **THEN** the database map displays the failure state and triggers an alert evaluation

### Requirement: Zabbix host correlation for HCPE-VP-MAQUEIROS
The MonitoraUSID system SHALL retrieve hardware metrics (CPU, RAM in GB, disk in GB) and active triggers from `ZabbixProvider` using the host ID mapped to `HCPE-VP-MAQUEIROS`.

#### Scenario: Zabbix Agent 2 is active on `10.34.0.111:10050`
- **WHEN** the dashboard endpoint queries `ZabbixProvider` for `HCPE-VP-MAQUEIROS`
- **THEN** the returned payload includes CPU, memory, and disk metrics for the host
