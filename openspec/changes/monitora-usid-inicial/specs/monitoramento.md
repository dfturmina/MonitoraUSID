# Spec: Módulo de Monitoramento de Sistemas e Integração Zabbix / Health

## Requisitos Funcionais (RF)

### RF01 - Cadastro e Gerenciamento de Aplicações Monitoradas
- O sistema DEVE permitir o cadastro de aplicações/sistemas do setor com os campos: Nome, Descrição, URL Base, URL da Rota Health (ex: `/api/health`), Host ID do Zabbix, Criticidade (Alta, Média, Baixa) e Status de Monitoramento (Ativo/Inativo).

### RF02 - Sondagem Periódica de Rota `/api/health`
- O backend DEVE executar rotinas de checagem (polling) periódica da rota `/api/health` de cada aplicação cadastrada.
- DEVE interpretar a resposta HTTP JSON contendo status da aplicação, status da conexão com banco de dados e versão SemVer.
- DEVE registrar histórico de disponibilidade (uptime, latência de resposta, código de status HTTP).

### RF03 - Integração com Zabbix API
- O sistema DEVE autenticar-se na API do Zabbix utilizando credenciais de API/Token configuradas em variáveis de ambiente `.env`.
- DEVE consultar os alertas ativos (Triggers em estado de problema) e métricas chave de infraestrutura (CPU, Memória, Disco, Conectividade).

### RF04 - Painel / Dashboard Visual estilo Grafana Aprimorado
- O frontend Vue 3 DEVE apresentar um Dashboard em tempo real contendo:
  - Cards de Status Geral (Total de Sistemas, Sistemas Saudáveis, Sistemas com Alertas, Sistemas Indisponíveis).
  - Grid visual dos Sistemas com badge de estado (Online, Degradado, Offline) e tempo de resposta (ms).
  - Painel de Alerta/Incidentes ativos ordenados por severidade.
  - Gráficos de disponibilidade e tempo de resposta ao longo do tempo.

### RF05 - Autenticação & Permissões (AD / RBAC)
- O acesso ao Monitora USID DEVE utilizar o mecanismo de autenticação AD + RBAC nativo do Framework SETISD.
- Perfil `ADMINISTRADOR`: Permite cadastrar/editar aplicações e configurações de integração.
- Perfil `CONSULTA` / `OPERADOR`: Permite visualizar dashboards e relatórios de disponibilidade.

## Requisitos Não Funcionais (RNF)

- **RNF01 - Usabilidade e Estética:** Interface com tema dark/light corporativo premium, com componentes visuais altamente intuitivos e micro-animações.
- **RNF02 - Desempenho:** A sondagem de rotas health deve ser assíncrona (`httpx.AsyncClient`), sem bloquear o loop principal do FastAPI.
- **RNF03 - Segurança:** Nenhuma credencial do Zabbix ou token de serviço deve estar hardcoded no código.
