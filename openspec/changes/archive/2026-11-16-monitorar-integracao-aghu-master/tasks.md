## 1. Inspeção de Logs e Cadastro

- [x] 1.1 Configurar checagem em `SshMetricsProvider` para detectar deploy `IntegracaoMasterAghu` e falhas recentes nos logs `catalina.out` do Tomcat.
- [x] 1.2 Cadastrar `Integração AGHU x Master Tools` com `zabbix_host_id=HCPE-VP-TOMCAT` (resolvido automaticamente por `ZabbixProvider`), `ssh_host=integracao-master`, `url_base=http://10.34.0.4:8080/`, `possui_rota_health=false` e `possui_banco_aghu=true`.

## 2. Verificação de Processo/Log e Testes

- [x] 2.1 Adicionar suporte no `SshMetricsProvider` para checar serviço systemd `tomcat` e integridade recente do `IntegracaoMasterAghu`.
- [x] 2.2 Criar testes unitários simulando Tomcat 200 com falha no listener detectada via SSH.
