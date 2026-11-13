# Design: Refinamento de Interface, RBAC e Módulo de Histórico

## Arquitetura Frontend & Roteamento

1. **Alteração no Layout (`DefaultLayout.vue`):**
   - Atualização do título da marca para **MonitoraUSID**.
   - Atualização das rotas no menu de navegação:
     - `/` -> Dashboard
     - `/historico` -> Histórico de Logs & Incidentes
     - `/componentes` -> Guia de UI
     - `/configuracoes` -> Perfis & Configurações

2. **Reformulação da Tela de Login (`Login.vue`):**
   - Design responsivo com suporte a degradê sutil, card elevado com sombras suaves e estados de carregamento.

3. **Novo Endpoint de Histórico (`src/routers/monitor.py`):**
   - Inclusão do endpoint `GET /api/monitor/historico` para consulta ordenada e filtrada da tabela `health_logs`.

4. **Configuração de Perfis de Acesso (`src/auth/auth.py` e `data/app.db`):**
   - Mapeamento dos papéis: `ADMINISTRADOR`, `OPERADOR`, `CONSULTA`.
