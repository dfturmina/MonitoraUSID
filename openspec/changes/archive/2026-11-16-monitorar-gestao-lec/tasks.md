## 1. Cadastro e Checagem Systemd

- [x] 1.1 Cadastrar `Gestão interna da LEC` no MonitoraUSID (`url_base=https://10.34.0.202`, `possui_rota_health=false`, `possui_banco_aghu=true`, `criticidade=ALTA`).
- [x] 1.2 Configurar no `SshMetricsProvider` a verificação de `sistemalec.service` e `nginx.service` em `10.34.0.202` além de CPU/RAM/Disco.

## 2. Validação e Testes

- [x] 2.1 Verificar conectividade TCP de saída para AGHU (`10.34.0.92:5432`) se aplicável em `bancos_adicionais`.
- [x] 2.2 Adicionar testes unitários cobrindo HTTP 502 do Nginx quando `sistemalec.service` cai e coleta SSH.
