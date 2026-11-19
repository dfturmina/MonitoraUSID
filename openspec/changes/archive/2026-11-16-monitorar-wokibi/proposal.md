## Why

O **Wokibi** (`10.34.0.219`, `hc-ufpe-vp-wokibi`) é uma plataforma de IA para dados de hemodiálise composta por frontend Next.js (`:3000`), serviço Python de anonimização (`app_anony.py` em `:8080/health` retornando `{"model":"noharm-ai/anony","ready":true}`) e container Docker `wokibi-mongodb` (`:27017`). O servidor **não possui Zabbix Agent ativo**, portanto o MonitoraUSID precisa coletar métricas de SO e containers via SSH (`SshMetricsProvider`).

## What Changes

- Cadastrar a aplicação **Wokibi** apontando para `http://10.34.0.219:8080` com `url_health="/health"` (e checagem secundária do frontend Next.js `:3000`).
- Monitorar o container `wokibi-mongodb` via TCP (`10.34.0.219:27017` em `bancos_adicionais`) e status Docker.
- Implementar `SshMetricsProvider` (`root@10.34.0.219` com chave SSH configurada) para coletar CPU, RAM (GB/%), disco (GB/%), status do container `wokibi-mongodb` e processos `app_anony.py`/`next-server` na ausência de Zabbix.

## Capabilities

### New Capabilities
- `monitorar-wokibi`: Monitoramento de saúde da API IA (:8080/health), frontend Next.js (:3000), MongoDB (:27017) e telemetria de VM via SSH para o Wokibi.

### Modified Capabilities
<!-- Nenhuma capability existente em openspec/specs/ sofreu alteração de contrato base. -->

## Impact

`src/providers/interfaces/host_metrics_provider_interface.py`, `src/providers/implementations/ssh_metrics_provider.py`, `src/services/health_poller.py`, `src/routers/monitor.py` e `data/app.db`.
