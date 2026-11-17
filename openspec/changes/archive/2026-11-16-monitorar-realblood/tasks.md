## 1. Descoberta Zabbix e Rota Aplicacional

- [x] 1.1 Configurar `zabbix_host_id=HC-UFPE-VP-REALBLOOD-APP` e validar suporte a itens de disco Windows (`C:,used` / `C:,total`) em `ZabbixProvider`.
- [x] 1.2 Cadastrar `RealBlood` apontando para `http://10.34.0.218/` (HTTP 200 IIS) com `bancos_adicionais` sondando `10.34.0.217:1433` (SQL Server) e `10.34.0.217:80`.

## 2. Validação e Testes

- [x] 2.1 Validar no `ZabbixProvider` a extração de `C:,used` / `C:,total` em hosts Windows.
- [x] 2.2 Adicionar teste automatizado para sondagem HTTP + TCP `1433` do RealBlood.
