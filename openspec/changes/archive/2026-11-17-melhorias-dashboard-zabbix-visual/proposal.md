# Proposal: Melhorias Visuais, Integração Avançada Zabbix, Auto-Refresh e Marca do MonitoraUSID

## Contexto e Motivação
Para evoluir a usabilidade e o dinamismo do **MonitoraUSID**, o usuário solicitou uma rodada de melhorias na interface visual e na exibição de métricas operacionais:
1. **Paleta de Cores e Sidebar:** Alinhar o fundo da barra lateral (Sidebar) com o padrão visual esmeralda/slate sofisticado da tela de Login.
2. **Navegação Limpa:** Alterar o item de menu "Início" para "Dashboard" e excluir o menu "Componentes".
3. **Auto-Refresh Configurável:** Permitir que o usuário selecione o intervalo de atualização automática dos dados do Dashboard (ex: 5s, 10s, 30s ou Desativado).
4. **Métricas Zabbix no Grid de Sistemas:** Integrar medições de CPU %, RAM %, Disco % e latência Zabbix diretamente nos cards de cada aplicação monitorada.
5. **Detalhamento de Conexão com Bancos:** Exibir detalhamento de múltiplos bancos na rota health (ex: Conexão Banco App e Conexão AGHU).
6. **Ajuste de Rótulo:** Substituir o texto `Versão SemVer` para apenas `Versão`.
7. **Identidade Visual / Logo:** Criar e integrar uma logo visual estilizada para o MonitoraUSID no topo da sidebar e login.

## Escopo das Modificações
- **Frontend Vue 3 (`DefaultLayout.vue`, `Home.vue`):** Atualização de estilos CSS da sidebar, seletores de auto-refresh em tempo real, exclusão do menu componentes, logo SVG moderna e exibição de métricas Zabbix e status múltiplo de bancos de dados.
- **Backend FastAPI (`monitor.py`, `zabbix_provider.py`):** Expansão do provedor do Zabbix para retornar métricas de CPU, RAM e Disco agregadas por host ID e status detalhado dos bancos.
