## 1. Extensão do Modelo e Poller para Modo TCP

- [x] 1.1 Adicionar coluna opcional `tipo_checagem` (default `'HTTP'`) e `porta_tcp` em `src/models/aplicacao.py` e no schema Pydantic de `src/routers/monitor.py`.
- [x] 1.2 Atualizar `HealthPollerService.poll_single_app` para executar sondagem TCP assíncrona com medição de `latency_ms` quando `tipo_checagem == 'TCP'` (e consulta Zabbix se `'ZABBIX'`).

## 2. Cadastro do Gateway Power BI e Testes

- [x] 2.1 Configurar `zabbix_host_id=HC-UFPE-VP-ONPREMISSES` para resolução automática em `ZabbixProvider`.
- [x] 2.2 Cadastrar `Gateway Power BI` (`10.34.0.70`, `tipo_checagem='TCP'`, `porta_tcp=10050`, `possui_banco_aghu=true`) e atualizar o modal de cadastro em `frontend/src/views/Home.vue` com seleção de `tipo_checagem`, `porta_tcp` e `ssh_host`.
- [x] 2.3 Adicionar testes unitários no `pytest` validando o modo `TCP` (sucesso e timeout).
