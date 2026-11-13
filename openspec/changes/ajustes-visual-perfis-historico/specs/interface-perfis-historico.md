# Spec: Refinamentos Visuais, Tela de Login, Perfis RBAC e Histórico de Logs

## Requisitos Funcionais (RF)

### RF01 - Padronização do Nome MonitoraUSID
- O título das páginas exibido na aba do navegador (`document.title`) DEVE ser atualizado dinamicamente para `"MonitoraUSID - [Nome da Página]"`.
- A barra lateral (Sidebar) DEVE exibir `"MonitoraUSID"` no topo e a versão no rodapé.

### RF02 - Tela de Login Premium
- A view `Login.vue` DEVE apresentar um layout moderno com card centralizado estilo glassmorphism, background elegante, suporte a tema corporativo, ícone temático de monitoramento e alternância transparente entre login AD (EBSERHNET) e ambiente Mock.

### RF03 - Perfis de Acesso Adequados (RBAC)
- Os perfis de acesso cadastrados e validados no sistema DEVEM ser:
  - `ADMINISTRADOR`: Acesso total (gerenciamento de usuários, adição/remoção de aplicações monitoradas e configurações do Zabbix).
  - `OPERADOR`: Acesso ao dashboard, histórico e capacidade de silenciar/reconhecer alertas temporariamente.
  - `CONSULTA`: Acesso apenas de leitura aos dashboards e relatórios de disponibilidade.

### RF04 - Reestruturação dos Menus de Navegação
- O item de menu "Exemplo" DEVE ser removido da barra lateral e do roteador Vue.
- DEVE ser adicionado o novo item de menu "Histórico" (rota `/historico`).
- O item de menu "Componentes" DEVE permanecer disponível para consulta visual de UI.

### RF05 - Módulo e Tela de Histórico (`/historico`)
- DEVE ser criada a página `Historico.vue` e o endpoint `/api/monitor/historico` para listagem paginada e filtrada por período (Últimas 24h, 7 dias, 30 dias) dos logs de resposta `/api/health` e incidentes Zabbix.
