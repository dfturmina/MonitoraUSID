# Monitora USID

> **Sistema Centralizado de Monitoramento Visual de Aplicações e Infraestrutura do SETISD**  
> *Desenvolvido sobre o Padrão Oficial de Desenvolvimento do Hospital das Clínicas da UFPE (HC-UFPE / EBSERH).*

---

## 🏛️ Visão Geral

O **Monitora USID** é uma aplicação web voltada ao monitoramento em tempo real dos sistemas e serviços do Setor de TI e Saúde Digital (SETISD) do HC-UFPE. 

Projetado para oferecer uma **usabilidade e apelo visual superiores aos dashboards tradicionais (como Grafana)**, o Monitora USID centraliza a visibilidade operacional da equipe, integrando-se à **API do Zabbix** para dados de infraestrutura e realizando a sondagem automática da rota `/api/health` estabelecida pelos sistemas baseados no **Framework-SETISD-HC-UFPE**.

---

## 🚀 Pilares do Sistema & Arquitetura

- **📊 Dashboard Visual Executivo & Operacional:**
  - Interface moderna estilo Grafana aprimorado com cards de status, gráficos de latência/disponibilidade e visualização clara de incidentes.
  - Componentes visuais ricos com suporte a temas dark/light e atualização contínua em tempo real.
- **🔌 Integração Nativa com Zabbix API:**
  - Coleta automática de alertas (Triggers em estado de problema) e métricas de servidores/hosts via API JSON-RPC do Zabbix.
- **🩺 Sondagem Automática `/api/health`:**
  - Checagem periódica assíncrona da rota de diagnóstico `/api/health` de cada aplicação do setor, verificando status do banco de dados, uptime e versão do código (SemVer).
- **🛡️ Autenticação Híbrida & Segurança Corporativa (AD + RBAC + Security Headers):**
  - Integração com **Active Directory (AD/LDAP Ebserh)** em produção e provedor **Mock** para desenvolvimento local.
  - Controle de acesso baseado em papéis (RBAC local: Administrador, Operador, Consulta).
  - Tokens JWT + Refresh Tokens HttpOnly com auto-renovação transparente.
  - Middleware de Security Headers e *Default-Private Router Pattern* no FastAPI.
- **⚡ Backend Moderno (FastAPI) & Frontend Reativo (Vue 3 / Vite):**
  - Python 3.12+ assíncrono com FastAPI, SQLAlchemy 2.0 e `httpx`.
  - Vue 3 SPA (Composition API / TypeScript) servido diretamente pelo FastAPI.

---

## 📂 Estrutura do Projeto

```text
MonitoraUSID/
├── .env.example          # Modelo de variáveis de ambiente (inclui Zabbix API)
├── AGENTS.md             # Diretrizes universais para Agentes de IA
├── audit_framework.py    # Auditor de Conformidade Arquitetural (11 Pilares)
├── Dockerfile            # Receita de build multi-estágio
├── compose.yaml          # Orquestração de contêiner
├── pyproject.toml        # Dependências e configurações Python
├── dev.sh                # Script de execução paralela para desenvolvimento
├── start.sh              # Script de build e execução local do servidor
├── openspec/             # Especificações orientadas a mudanças (OpenSpec)
│   └── changes/          # Propostas de mudança ativas
├── docs/                 # Documentação detalhada
│   ├── especificacao/    # Especificação do sistema (Visão, Requisitos, SDD)
│   ├── ARCHITECTURE.md   # Arquitetura em camadas e padrão Provider
│   ├── AUTHENTICATION.md # Sistema de Autenticação (AD / Mock / JWT)
│   └── SETUP.md          # Guia de instalação, testes e deploy
├── frontend/             # Aplicação SPA Vue 3 (Vite + TypeScript)
│   ├── src/
│   │   ├── components/   # Componentes visuais (StatusCards, MetricsChart, Grid)
│   │   ├── views/        # Telas (Dashboard, Monitoramento, Configurações, Admin)
│   │   └── services/     # Cliente HTTP e comunicação de APIs
├── src/                  # Backend FastAPI
│   ├── auth/             # Módulos de autenticação AD e JWT
│   ├── controllers/      # Regras de negócio de monitoramento e Zabbix
│   ├── providers/        # Acesso desacoplado (Zabbix, Health Poller, Postgres)
│   ├── resources/        # Gerenciamento de conexões
│   └── routers/          # Endpoints HTTP REST (`/api/monitor`, `/api/health`, `/api/auth`)
└── tests/                # Testes automatizados (pytest)
```

---

## 🚦 Início Rápido (Quick Start)

### 1. Configuração do Ambiente
```bash
# Clone o repositório
git clone https://github.com/dfturmina/MonitoraUSID.git
cd MonitoraUSID

# Copie o arquivo de exemplo de ambiente
cp .env.example .env
```

### 2. Executar em Modo Desenvolvimento (Hot Reload)
Executa o Backend (`http://localhost:8000`) e o Frontend Vite (`http://localhost:5173`) em paralelo:
```bash
./dev.sh
```

### 3. Rodar a Suíte de Testes e Auditor de Conformidade
```bash
# Testes unitários/integração
uv run pytest

# Verificação de conformidade de arquitetura (11 pilares)
uv run python audit_framework.py .
```

---

## 🔍 OpenSpec Workflow

Este repositório utiliza o **OpenSpec** para gerenciamento de especificações e propostas de mudança.

- **Verificar status das especificações:**
  ```bash
  openspec status --change monitora-usid-inicial
  ```
- **Listar especificações ativas:**
  ```bash
  openspec list
  ```

---

## 📚 Documentação Detalhada

Para mais detalhes sobre a arquitetura e especificações do sistema:

- **[ Gabarito de Especificação do Monitora USID (`docs/especificacao/SPEC.md`)](./docs/especificacao/SPEC.md)**
- **[ Visão do Produto (`docs/especificacao/01-visao.md`)](./docs/especificacao/01-visao.md)**
- **[ Requisitos do Sistema (`docs/especificacao/02-requisitos.md`)](./docs/especificacao/02-requisitos.md)**
- **[ Diretrizes e Regras para Agentes de IA (`AGENTS.md`)](./AGENTS.md)**
- **[ Arquitetura em Camadas (`docs/ARCHITECTURE.md`)](./docs/ARCHITECTURE.md)**

---

**SETISD - Setor de TI e Saúde Digital | HC-UFPE (EBSERH)**
