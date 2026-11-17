# Tasks: Integração Real Zabbix, Métricas Absolutas em GB e Usuários Conectados

- [x] **[TASK-001]** Atualizar `src/routers/health.py` para expor o número de usuários ativos (`active_users`) e estrutura de bancos <!-- id: 1 -->
- [x] **[TASK-002]** Atualizar `src/services/health_poller.py` para extrair usuários ativos e mapeamento dinâmico de bancos de dados <!-- id: 2 -->
- [x] **[TASK-003]** Expandir `src/providers/implementations/zabbix_provider.py` para retornar valores em GB de Memória e Disco (`memory_used_gb`, `memory_total_gb`, `disk_used_gb`, `disk_total_gb`) <!-- id: 3 -->
- [x] **[TASK-004]** Atualizar o payload de `/api/monitor/dashboard` em `src/routers/monitor.py` <!-- id: 4 -->
- [x] **[TASK-005]** Atualizar `frontend/src/views/Home.vue` para exibir valores em GB, usuários ativos, bancos dinâmicos e trocar "Latência HTTP" por "Tempo de Resposta" <!-- id: 5 -->
- [x] **[TASK-006]** Recompilar o frontend Vue 3 e rodar auditoria com `audit_framework.py` <!-- id: 6 -->
