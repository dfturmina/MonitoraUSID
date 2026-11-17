## 1. Integração SSH e Poller

- [x] 1.1 Configurar coleta de containers Docker (`cinco_hc-nginx-1`, `cinco_hc-app-1`, `cinco_hc-postgres-1`) no `SshMetricsProvider` para o alias `mews` (`adm-local@10.34.0.197`).
- [x] 1.2 Permitir que o `HealthPollerService` / `monitor.py` mescle o status de containers de banco retornados pelo `SshMetricsProvider` no dicionário `databases` da aplicação.

## 2. Cadastro e Testes

- [x] 2.1 Cadastrar `Escala de MEWS` (`url_base=https://10.34.0.197/login`, `possui_rota_health=false`, `criticidade=ALTA`) vinculado à coleta SSH (`adm-local@10.34.0.197`).
- [x] 2.2 Criar testes unitários simulando container `cinco_hc-postgres-1` healthy/unhealthy e HTTP 200 em `/login`.
