## Why

O **RealBlood** (agência transfusional, criticidade assistencial alta) roda em duas VMs Windows: `10.34.0.218` (`HC-UFPE-VP-REALBLOOD-APP`, portas abertas `[80, 443, 3389]`) e `10.34.0.217` (`HC-UFPE-VP-REALBLOOD-BD`, portas abertas `[80, 443, 1433, 3389]`), integradas ao AGHU (`ugen_realblood` `:6544`). Como são servidores Windows sem SSH (porta 22 fechada) e sem Zabbix Agent respondendo na porta `10050`, o monitoramento precisa combinar sondagem HTTP IIS, teste TCP do SQL Server (`1433`) e correlação Zabbix.

## What Changes

- Cadastrar a aplicação **RealBlood** apontando para `http://10.34.0.218/` (`possui_rota_health=false`, `possui_banco_aghu=true`, `criticidade="ALTA"`).
- Configurar `bancos_adicionais` para sondar o SQL Server (`10.34.0.217:1433`), a interface web do servidor BD (`10.34.0.217:80`) e a porta AGHU.
- Mapear os `zabbix_host_id` de `HC-UFPE-VP-REALBLOOD-APP` e `HC-UFPE-VP-REALBLOOD-BD` no Zabbix (verificando coleta passiva/ativa ou ICMP/WMI caso `10050` esteja bloqueado no Firewall do Windows).

## Capabilities

### New Capabilities
- `monitorar-realblood`: Monitoramento HTTP das duas VMs Windows do RealBlood, checagem TCP do SQL Server (1433) e integração com Zabbix.

### Modified Capabilities
<!-- Nenhuma capability existente em openspec/specs/ sofreu alteração de contrato base. -->

## Impact

`src/services/health_poller.py`, `src/providers/implementations/zabbix_provider.py` (compatibilidade Windows já parcial) e cadastro em `data/app.db`.
