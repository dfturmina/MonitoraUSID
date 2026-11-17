## Why

O **Master Tools** sustenta processos administrativos críticos (compras, licitações e contratos) em um cluster Oracle RAC 19c de dois nós (`rac01` em `10.34.1.120` e `rac02` em `10.34.1.121`, além dos IPs VIP/SCAN `10.34.1.122`–`126`). O MonitoraUSID precisa acompanhar a disponibilidade dos nós web/aplicação (`nginx`, Forms/Reports), os listeners Oracle (`:1521`) e o `node_exporter` (`:9100`) / `zabbix-agent2` ativos no cluster.

## What Changes

- Cadastrar os dois nós principais (`Master Tools - RAC01` em `10.34.1.120` e `Master Tools - RAC02` em `10.34.1.121`) no MonitoraUSID com `possui_rota_health=false`.
- Configurar monitoramento TCP dos listeners Oracle RAC (`10.34.1.120:1521`, `10.34.1.121:1521` e VIPs/SCAN `10.34.1.122`–`10.34.1.126:1521`) e checagem HTTP das portas web (`:80` e `:8877`).
- Integrar métricas dos hosts `HCPE-FP-MASTER01` e `HCPE-FP-MASTER02` via `ZabbixProvider` (`zabbix-agent2` `:10050`), com suporte opcional a verificação de instâncias `ora_pmon_hcpe1`/`hcpe2` e `node_exporter` (`:9100/metrics`) via `SshMetricsProvider`.

## Capabilities

### New Capabilities
- `monitorar-master-tools`: Monitoramento multi-nó do cluster Oracle RAC e serviços web/Forms do Master Tools no MonitoraUSID.

### Modified Capabilities
<!-- Nenhuma capability existente em openspec/specs/ sofreu alteração de contrato base. -->

## Impact

`src/services/health_poller.py`, `src/providers/implementations/ssh_metrics_provider.py` (opcional para RAC), tabela `aplicacoes` e Dashboard Vue.
