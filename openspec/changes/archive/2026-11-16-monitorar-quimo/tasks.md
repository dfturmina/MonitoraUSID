## 1. Cadastro e Ajuste de Poller

- [x] 1.1 Cadastrar `Quimo` (`url_base=https://10.34.0.191`, `url_health=/api/health`, `possui_rota_health=true`, `possui_banco_aghu=true`, `bancos_adicionais=[{"nome":"PostgreSQL Quimo","host":"10.34.0.191","porta":5432}]`, `criticidade=ALTA`).
- [x] 1.2 Ajustar `HealthPollerService` para não exibir `Banco Aplicação: connected` genérico quando `bancos_adicionais` estiver configurado e `/api/health` não tiver chave `databases`.

## 2. Coleta SSH Podman e Testes

- [x] 2.1 Suportar `podman ps` no `SshMetricsProvider` para ler o estado de `quimio_app` e `quimio_db_app` além de CPU/RAM/Disco em `10.34.0.191`.
- [x] 2.2 Escrever testes automatizados validando o contrato `/api/health` do Quimo + probe TCP `5432` + mock SSH.
