## 1. Provider SSH e Adaptação do Poller

- [x] 1.1 Criar `SshMetricsProvider` em `src/providers/implementations/ssh_metrics_provider.py` (com configuração de host/usuário via campo da aplicação ou inventário seguro sem senhas hardcoded, usando a chave SSH local).
- [x] 1.2 Atualizar `HealthPollerService` para validar campo `ready === true` na rota `/health` do Wokibi e verificar também a porta HTTP `:3000` e MongoDB `:27017`.

## 2. Cadastro e Testes

- [x] 2.1 Cadastrar `Wokibi` no banco local apontando para `http://10.34.0.219:8080` (`url_health=/health`, `bancos_adicionais` com MongoDB `27017` e frontend `3000`) e habilitar coleta SSH.
- [x] 2.2 Adicionar testes unitários com mocks para `SshMetricsProvider` e validação do payload `{"ready": true}`.
