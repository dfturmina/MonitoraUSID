## 1. Descoberta e Cadastro

- [x] 1.1 Suportar resolução automática do hostname técnico `HCPE-VP-MAQUEIROS` em `ZabbixProvider._resolve_host_ids` / `get_host_metrics` (sem exigir ID numérico fixo).
- [x] 1.2 Criar script/seed idempotente no MonitoraUSID cadastrando a aplicação `CSH (Maqueiros) - Produção` (`url_base=http://10.34.0.111/admin_3/loginAD.php`, `possui_rota_health=false`, `possui_banco_aghu=true`, `criticidade=ALTA`).
- [x] 1.3 Configurar `bancos_adicionais` com `[{"nome": "MariaDB CSH", "host": "10.34.0.111", "porta": 3306}]`.

## 2. Validação e Testes

- [x] 2.1 Adicionar teste automatizado em `tests/` simulando resposta HTTP 200 em `/admin_3/loginAD.php`, probe TCP `:3306` e resposta do `ZabbixProvider`.
- [x] 2.2 Validar no endpoint `/api/monitor/dashboard` e no card do Dashboard Vue a exibição correta de latência, MariaDB e métricas da VM.
