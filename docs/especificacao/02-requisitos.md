# Especificação de Requisitos - Monitora USID

## 1. Requisitos Funcionais (RF)
| ID | Título | Descrição | Prioridade |
| :--- | :--- | :--- | :---: |
| RF001 | Autenticação AD/LDAP | Autenticação corporativa via Active Directory Ebserh e RBAC local. | Essencial |
| RF002 | Cadastro de Aplicações | Cadastro e gestão dos sistemas do setor (URL health, Zabbix host ID, criticidade). | Essencial |
| RF003 | Polling de Health | Checagem periódica assíncrona da rota `/api/health` das aplicações. | Essencial |
| RF004 | Integração Zabbix | Leitura de alertas e métricas de infraestrutura da API JSON-RPC do Zabbix. | Essencial |
| RF005 | Dashboard Visual | Interface reativa em tempo real com status grid, gráficos de latência e painel de incidentes. | Essencial |
| RF006 | Trilha de Auditoria | Registro imutável em `audit_logs` de modificações em cadastros e configurações. | Importante |

### 📌 Legenda de Níveis de Prioridade:
- **Essencial (Alta):** Funcionalidade indispensável para o funcionamento básico da aplicação.
- **Importante (Média):** Funcionalidade que agrega valor significativo ao negócio.
- **Desejável (Baixa):** Funcionalidade complementar ou melhoria secundária.

## 2. Requisitos Não Funcionais (RNF)
| ID | Categoria | Descrição |
| :--- | :--- | :--- |
| RNF001 | Usabilidade & UX | Interface visual atraente (estilo Grafana aprimorado), tema dark/light e micro-animações. |
| RNF002 | Desempenho Assíncrono | Coleta de métricas e sondagem HTTP assíncrona (`httpx`) sem bloquear o evento loop do FastAPI. |
| RNF003 | Criptografia & Tokens | JWT assinados com HS256 e Cookies HttpOnly para Refresh Tokens. |
| RNF004 | Segurança HTTP | Middleware de Security Headers (`no-store`, `X-Frame-Options: DENY`, `XSS-Protection`). |
| RNF005 | Governança de Segredos | Variáveis de ambiente centralizadas (`src/config.py`) sem credenciais hardcoded. |

## 3. Detalhamento SDD (CARE)

### [CARE-RF003] Polling de Health
* **Context (Contexto)**: Lista de aplicações ativas cadastradas no sistema.
* **Action (Ação)**: Worker em background faz GET assíncrono em `/api/health` de cada aplicação.
* **Result (Resultado)**: Atualiza histórico de latência, uptime e status no banco de dados.
* **Evaluation (Avaliação)**: Executar suíte de testes `pytest` validando respostas com status 200 (Online) e falhas (Offline).

### [CARE-RF004] Integração Zabbix
* **Context (Contexto)**: Credenciais de API do Zabbix configuradas no `.env`.
* **Action (Ação)**: `ZabbixProvider` faz requisição JSON-RPC para buscar triggers ativas e dados de performance.
* **Result (Resultado)**: Retorna lista padronizada de incidentes e métricas para o Controller/Router.
* **Evaluation (Avaliação)**: Testes unitários com mocks da API do Zabbix.