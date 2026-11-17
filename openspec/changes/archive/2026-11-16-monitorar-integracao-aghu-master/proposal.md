## Why

A VM `robot-java` (`10.34.0.4`, hostname Zabbix `HCPE-VP-TOMCAT`) executa no Apache Tomcat 8 o listener `IntegracaoMasterAghu.war` (`RoboIntegracao`), responsável por sincronizar dados do AGHU (`ugen_integra` `:6544`) para o Master Tools (`:1521`). Como o WAR é um *ServletContextListener* sem endpoint HTTP dedicado (`/IntegracaoMasterAghu/` retorna 404), testar apenas HTTP é insuficiente para saber se o robô está vivo.

## What Changes

- Cadastrar a aplicação **Integração AGHU x Master Tools** (`http://10.34.0.4:8080/`, `possui_rota_health=false`, `possui_banco_aghu=true`) vinculada ao Zabbix `HCPE-VP-TOMCAT`.
- Implementar verificação híbrida via SSH (`SshMetricsProvider`) no host `10.34.0.4` para validar o serviço `tomcat.service`, presença ativa da thread/deploy `IntegracaoMasterAghu` e últimas linhas sem erro fatal no `catalina.out`.
- Validar conectividade TCP com os bancos de origem/destino (AGHU `:6544` e Oracle Master `10.34.1.125:1521`).

## Capabilities

### New Capabilities
- `monitorar-integracao-aghu-master`: Monitoramento do servidor Tomcat `robot-java` e verificação de saúde do listener background `RoboIntegracao` via SSH e Zabbix.

### Modified Capabilities
<!-- Nenhuma capability existente em openspec/specs/ sofreu alteração de contrato base. -->

## Impact

`src/providers/implementations/ssh_metrics_provider.py`, `src/services/health_poller.py`, `src/routers/monitor.py` e cadastro em `data/app.db`.
