# Spec: Dashboard Aprimorado, Métricas Zabbix, Auto-Refresh e Redesenho da Sidebar

## Requisitos Funcionais (RF)

### RF01 - Redesenho da Barra Lateral (Sidebar)
- A barra lateral DEVE utilizar uma paleta de cores consistente com a Tela de Login (fundo slate/dark com destaques em verde esmeralda).
- DEVE exibir a logo/marca visual moderna do **MonitoraUSID**.
- O menu "Início" DEVE ser renomeado para **"Dashboard"**.
- O menu "Componentes" DEVE ser removido.

### RF02 - Auto-Refresh no Dashboard
- O Dashboard DEVE oferecer um seletor de intervalo de atualização automática (Desativado, 5s, 10s, 30s).
- Ao selecionar um intervalo, o frontend DEVE executar sondagens periódicas automáticas no endpoint `/api/monitor/dashboard` sem recarregar a página.

### RF03 - Métricas do Zabbix por Aplicação
- Cada card de aplicação cadastrada DEVE exibir métricas de infraestrutura obtidas via Zabbix API ou Poller:
  - Uso de CPU (%)
  - Uso de Memória RAM (%)
  - Uso de Disco (%)
  - Latência de Conectividade (ms)

### RF04 - Status Detalhado dos Bancos de Dados
- O card de cada aplicação DEVE exibir a conectividade dos bancos informada pela rota health:
  - Banco Local / Aplicação (ex: OK / Falha)
  - Conexão AGHU PostgreSQL (ex: Conectado / Não Configurado)

### RF05 - Simplificação de Rótulos
- O rótulo "Versão SemVer" DEVE ser simplificado para apenas **"Versão"**.
