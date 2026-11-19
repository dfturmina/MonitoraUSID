## 1. Cadastro e Conferência de Contrato

- [x] 1.1 Configurar `zabbix_host_id=HC-UFPE-VP-SAT-UTI` (resolvido automaticamente por `ZabbixProvider`) com fallback SSH `uti`.
- [x] 1.2 Cadastrar `UTI Manager` no banco `data/app.db` (`url_base=https://10.34.0.192`, `url_health=/api/health`, `possui_rota_health=true`, `possui_banco_aghu=true`, `monitora_usuarios_ativos=true`, `criticidade=ALTA`).

## 2. Validação e Testes

- [x] 2.1 Validar no `HealthPollerService` que `aghu_postgres` satisfaz a checagem de banco AGHU (`"aghu" in k.lower()`) sem adicionar chave falsa `not_in_route`.
- [x] 2.2 Adicionar teste automatizado com o payload real do Reserva UTI e verificar renderização no Dashboard.
