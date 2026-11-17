## Context

- Host: `10.34.0.4` (`robot-java`), Debian GNU/Linux 8 (jessie), kernel legado.
- Serviços ativos via SSH: `tomcat.service` (Apache Tomcat 8.0.28 em `:8080`, `:8009`, `:8005`) e `zabbix-agent.service` (`:10050`, `Server=10.34.0.29`, `Hostname=HCPE-VP-TOMCAT`).
- Webapps em `/usr/share/tomcat8/webapps/`: `IntegracaoMasterAghu` (possui apenas `ServletContextListener` `RoboIntegracao` no `web.xml`, sem servlet HTTP — `GET /IntegracaoMasterAghu/` retorna 404), `CompararInternacoes` e `osnethc`.

## Goals / Non-Goals

**Goals:**
- Detectar falhas silenciosas do robô `IntegracaoMasterAghu` mesmo quando a porta `8080` do Tomcat continua respondendo.
- Monitorar conectividade de rede entre `10.34.0.4` e os bancos AGHU/Oracle Master.

**Non-Goals:**
- Atualizar o sistema operacional Debian 8 ou recompilar o arquivo `IntegracaoMasterAghu.war`.

## Decisions

- **Verificação do listener via SSH em vez de deploy de novo servlet**: O host roda Debian 8 e código Java legado sem fonte local; checar processo `tomcat`, deploy directory e erros recentes de log via SSH é não-invasivo e imediato.

## Risks / Trade-offs

- **[Log `catalina.out` muito grande ou com mensagens antigas]** → Ler apenas os últimos N minutos/linhas (`tail -n 200`) e checar data de modificação recente para identificar atividade do robô.
