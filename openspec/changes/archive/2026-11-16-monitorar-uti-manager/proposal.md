## Why

O **UTI Manager** (`10.34.0.192`, `hc-ufpe-vp-sat-uti`) é o sistema mais alinhado ao padrão do framework: executa em Podman Compose (`hc-uti.service`), possui `zabbix-agent2` ativo (`HC-UFPE-VP-SAT-UTI`) e já expõe uma rota `/api/health` completa (`https://10.34.0.192/api/health`) retornando `version`, `active_users` e `databases: {"app_db": "connected", "aghu_postgres": "connected"}`. Resta integrá-lo formalmente no MonitoraUSID.

## What Changes

- Cadastrar a aplicação **UTI Manager (Reserva UTI)** apontando para `https://10.34.0.192` com `possui_rota_health=true`, `url_health="/api/health"`, `possui_banco_aghu=true`, `monitora_usuarios_ativos=true` e `criticidade="ALTA"`.
- Vincular o `zabbix_host_id` do agente ativo `HC-UFPE-VP-SAT-UTI` (`Server=10.34.0.29,10.34.0.127`, porta `10050`).
- Garantir no `HealthPollerService` a leitura correta de `databases` (`app_db` e `aghu_postgres`), `active_users` e `version` (`1.8.1`), além de normalização visual amigável no card.

## Capabilities

### New Capabilities
- `monitorar-uti-manager`: Integração direta da rota /api/health do Reserva UTI (bancos e usuários ativos) com o monitoramento Zabbix da VM HC-UFPE-VP-SAT-UTI.

### Modified Capabilities
<!-- Nenhuma capability existente em openspec/specs/ sofreu alteração de contrato base. -->

## Impact

`src/services/health_poller.py`, cadastro/seed em `data/app.db` (`aplicacoes`) e testes de contrato `/api/health`.
