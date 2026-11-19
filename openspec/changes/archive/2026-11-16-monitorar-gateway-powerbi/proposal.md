## Why

O **Gateway Power BI** (`10.34.0.70`, `HC-UFPE-VP-ONPREMISSES` / `HC-UFPE-VP-GATEWAY_BI`) é uma VM Windows dedicada ao *On-premises Data Gateway* que consome dados do AGHU (`ugen_bi` `:6544`). A varredura de rede comprovou que ele **não expõe servidor HTTP** (`:80` e `:443` dão timeout), mantendo abertas apenas as portas `3389` (RDP) e `10050` (Zabbix Agent). Hoje o `HealthPollerService` força uma requisição HTTP para todas as aplicações, o que marcaria o Gateway Power BI permanentemente como **Offline**.

## What Changes

- Estender o modelo `Aplicacao` e `HealthPollerService` para suportar tipo de sondagem **TCP / Zabbix** (`tipo_checagem`: `'HTTP'` | `'TCP'` | `'ZABBIX'`) sem depender de porta HTTP 80/443.
- Cadastrar a aplicação **Gateway Power BI** (`10.34.0.70`, `tipo_checagem="TCP"`, porta alvo `10050` ou `3389`, `possui_rota_health=false`, `possui_banco_aghu=true`).
- Integrar via `ZabbixProvider` o monitoramento do host `HC-UFPE-VP-ONPREMISSES` / `HC-UFPE-VP-GATEWAY_BI` (métricas Windows e eventual trigger do serviço `PBIEgwService`).

## Capabilities

### New Capabilities
- `monitorar-gateway-powerbi`: Suporte a aplicações não-HTTP (modo TCP/Zabbix) no HealthPollerService para monitoramento do Gateway Power BI em 10.34.0.70.

### Modified Capabilities
<!-- Nenhuma capability existente em openspec/specs/ sofreu alteração de contrato base. -->

## Impact

`src/models/aplicacao.py`, `src/services/health_poller.py`, `src/routers/monitor.py`, `frontend/src/views/Configuracoes.vue` e `data/app.db`.
