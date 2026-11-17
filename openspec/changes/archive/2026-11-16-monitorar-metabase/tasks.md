## 1. Ajustes de Sondagem e Cadastro

- [x] 1.1 Atualizar `HealthPollerService` para suportar `http_headers` opcionais (ex.: `Host: relatorios.hc-ufpe.ebserh`) ou usar `http://10.34.0.114:3000/api/health` e reconhecer `{"status":"ok"}`.
- [x] 1.2 Cadastrar `Metabase` com `zabbix_host_id=HC-UFPE-VP-METABASE`, `ssh_host=metabase`, `http_headers={"Host":"relatorios.hc-ufpe.ebserh"}`, `monitora_usuarios_ativos=true`, `possui_banco_aghu=true` e `bancos_adicionais=[{"nome":"PostgreSQL Metabase","host":"10.34.0.114","porta":5432}]`.

## 2. Validação Integrada e Testes

- [x] 2.1 Garantir integração com tabela `integracoes` (`provedor='METABASE'`) usando a API Key via variável de ambiente/configuração segura.
- [x] 2.2 Executar testes automatizados cobrindo `/api/health` do Metabase e fallback caso API Key esteja ausente.
