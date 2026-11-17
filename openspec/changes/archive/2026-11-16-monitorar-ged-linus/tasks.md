## 1. Verificação Zabbix e Cadastro

- [x] 1.1 Configurar `zabbix_host_id=HC-UFPE-VP-GED` com fallback automático para `SshMetricsProvider` (`ssh_host=ged`) caso o agente `Zabbix server` não resolva no Zabbix.
- [x] 1.2 Cadastrar `GED Linus` no MonitoraUSID (`url_base=http://10.34.0.124/usuarios/sign_in`, `possui_rota_health=false`, `bancos_adicionais` com NFS `:2049`).

## 2. Coleta SSH e Testes

- [x] 2.1 Adicionar checagem SSH (`ubuntu@10.34.0.124`) no `SshMetricsProvider` para validar processo `puma` e métricas de CPU/RAM/disco como fonte primária ou fallback.
- [x] 2.2 Implementar testes unitários validando HTTP 200 em `/usuarios/sign_in` e fallback SSH.
