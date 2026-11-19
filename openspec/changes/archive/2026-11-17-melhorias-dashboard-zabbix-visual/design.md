# Design: Dashboard Aprimorado com Zabbix, Auto-Refresh e Redesenho da Sidebar

## Componentes Visuais & Integração

1. **Logo e Sidebar (`DefaultLayout.vue`):**
   - Criação do componente de Logo SVG estilizado com ícone de pulso de monitoramento e tipografia moderna.
   - Atualização das classes CSS da sidebar para `bg-slate-900 border-r border-slate-800 text-slate-100`.
   - Links de navegação: Dashboard (`/`), Histórico (`/historico`), Configurações (`/configuracoes`).

2. **Auto-Refresh e Cards de Aplicação (`Home.vue`):**
   - Inclusão do dropdown de seleção de auto-refresh (`setInterval` reativo).
   - Renderização dos indicadores virtuais de CPU, RAM e Disco nos cards de cada sistema.

3. **Backend & Zabbix Provider (`src/routers/monitor.py`, `zabbix_provider.py`):**
   - Retorno estruturado do status dos múltiplos bancos (`app_db`, `aghu_postgres`).
   - Mapeamento de métricas Zabbix de CPU, RAM e Disco para o payload do Dashboard.
