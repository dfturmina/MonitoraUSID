## 1. Mapeamento Zabbix e Cadastro

- [x] 1.1 Suportar resolução automática dos hostnames `HCPE-FP-MASTER01` e `HCPE-FP-MASTER02` em `ZabbixProvider._resolve_host_ids` / `get_host_metrics`.
- [x] 1.2 Cadastrar `Master Tools - Node 1 (RAC01)` (`10.34.1.120:80`, `bancos_adicionais` com `.120`, `.122`, `.125`, `.126` na porta `1521`) e `Master Tools - Node 2 (RAC02)` (`10.34.1.121:80`, `bancos_adicionais` com `.121`, `.123`, `.124` na porta `1521`).

## 2. Coleta Complementar e Testes

- [x] 2.1 Avaliar leitura opcional de `http://10.34.1.120:9100/metrics` (`node_exporter`) e checagem SSH de `ora_pmon_hcpe1`/`ora_pmon_hcpe2` no `SshMetricsProvider`.
- [x] 2.2 Escrever testes unitários validando a agregação de múltiplos listeners `1521` em `bancos_adicionais`.
