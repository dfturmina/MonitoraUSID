## Why

O **Dialsist** (`10.34.0.83`, `hc-ufpe-vp-dialsist`) apoia o serviço de diálise com aplicações PHP em Apache (`:80`), MySQL Community Server (`:3306`) e integração direta com o AGHU Slave (`10.34.0.92:5432` via `ugen_dialsist`). Ele já possui `zabbix-agent` ativo (`HC-UFPE-VP-DIALSIST`), faltando integrá-lo ao MonitoraUSID.

## What Changes

- Cadastrar a aplicação **Dialsist** apontando para `http://10.34.0.83/ufpeds4/` (`possui_rota_health=false`, `possui_banco_aghu=true`).
- Configurar monitoramento TCP dinâmico (`bancos_adicionais`) do MySQL local (`10.34.0.83:3306`) e do AGHU Slave (`10.34.0.92:5432`).
- Vincular o `zabbix_host_id` do agente `HC-UFPE-VP-DIALSIST` (`Server=10.34.0.29,10.34.0.127`, porta `10050`).

## Capabilities

### New Capabilities
- `monitorar-dialsist`: Sondagem HTTP do Dialsist, verificação TCP do MySQL local e AGHU Slave, e métricas de VM via Zabbix HC-UFPE-VP-DIALSIST.

### Modified Capabilities
<!-- Nenhuma capability existente em openspec/specs/ sofreu alteração de contrato base. -->

## Impact

`src/services/health_poller.py`, cadastro em `data/app.db` (`aplicacoes`) e Dashboard Vue.
