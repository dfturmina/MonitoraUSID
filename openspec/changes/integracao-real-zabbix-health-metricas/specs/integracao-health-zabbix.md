# Spec: Contrato da Rota /api/health, Métricas Absolutas Zabbix e Usuários Ativos

## Requisitos Funcionais (RF)

### RF01 - Exibição de Valores Absolutos de Hardware (Zabbix)
- O Zabbix Provider e o Dashboard DEVEM retornar e exibir os valores absolutos de Memória RAM usada/total (ex: `8.4 GB / 16.0 GB`) e Espaço em Disco usado/total (ex: `142.0 GB / 500.0 GB`), além das porcentagens.

### RF02 - Métricas da Rota `/api/health`
- O `HealthPollerService` DEVE extrair da rota `/api/health` das aplicações:
  - Status HTTP e Uptime.
  - Dicionário dinâmico de `databases` (ex: `{"app_db": "connected", "aghu_db": "connected"}`), sem fixar nomenclaturas de tipos de banco no código.
  - Número de **Usuários Conectados / Sessões Ativas** (campo `active_users` ou `active_sessions`).

### RF03 - Ajuste de Nomenclatura no Frontend
- O rótulo "Latência HTTP" DEVE ser alterado para **"Tempo de Resposta"**.
- O rótulo "Versão SemVer" DEVE ser alterado para **"Versão"**.

### RF04 - Integração Híbrida Real
- O Dashboard DEVE combinar dados de health HTTP (Sondagem direta na URL cadastrada) com dados de infraestrutura do Zabbix (consulta por `zabbix_host_id` na API JSON-RPC).
