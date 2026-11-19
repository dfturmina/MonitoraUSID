## 1. Descoberta e Cadastro

- [x] 1.1 Validar entrypoint `http://10.34.0.83/ufpeds4/` e configurar `zabbix_host_id=HC-UFPE-VP-DIALSIST` com fallback SSH (`ssh_host=dialsist`) via `ZabbixProvider._resolve_host_ids`.
- [x] 1.2 Cadastrar `Dialsist` no MonitoraUSID (`possui_rota_health=false`, `possui_banco_aghu=true`, `bancos_adicionais` com MySQL `10.34.0.83:3306` e AGHU Slave `10.34.0.92:5432`).

## 2. Validação e Testes

- [x] 2.1 Criar teste automatizado cobrindo o polling de `Dialsist` com múltiplos bancos em `bancos_adicionais`.
- [x] 2.2 Verificar exibição no Dashboard e persistência em `health_logs`.
