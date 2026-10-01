# SPEC.md - Especificação do Sistema Monitora USID

## 1. Visão Geral e Resultados Esperados
Este documento é a ÚNICA fonte de verdade para a orquestração do desenvolvimento do **Monitora USID**. O objetivo é construir uma aplicação web de monitoramento visual centralizado dos sistemas do SETISD/HC-UFPE com experiência de usuário (UX) e design aprimorados em relação ao Grafana.

### Objetivos de Alto Nível
- [ ] Implementar integração com a API JSON-RPC do Zabbix para obtenção de hosts e alertas.
- [ ] Implementar sondagem automática e assíncrona das rotas `/api/health` dos sistemas do setor.
- [ ] Desenvolver Dashboard visual em tempo real com cards de status, métricas de latência/disponibilidade e painel de incidentes.
- [ ] Manter autenticação corporativa via AD/LDAP Ebserh e RBAC local (Administrador, Operador, Consulta).
- [ ] Garantir trilhas de auditoria imutáveis para alterações de cadastros e configurações.

## 2. Contexto do Projeto
As definições detalhadas estão distribuídas nos seguintes documentos:
- [Validação e Fluxo de Negócio](00-validacao-negocio.md)
- [Visão do Produto](01-visao.md)
- [Requisitos Funcionais e Não Funcionais](02-requisitos.md)
- [Casos de Uso](03-casos-uso.md)
- [Modelo de Dados](04-modelo-dados.md)
- [Interfaces e UX](05-interfaces.md)
- [Arquitetura em Camadas](06-arquitetura.md)
- [Glossário](07-glossario.md)

## 3. Limites de Escopo e Guardrails
**A IA DEVE:**
- Seguir a arquitetura padrão em camadas (`Resource -> Provider -> Controller -> Router`).
- Garantir 100% de conformidade no auditor `audit_framework.py`.
- Utilizar chamadas HTTP assíncronas (`httpx`) para consulta ao Zabbix e rotas `/api/health`.

**A IA NÃO DEVE:**
- Armazenar credenciais da API do Zabbix diretamente no código.
- Bloquear a thread principal do FastAPI durante a sondagem de status.
- Expor rotas de dados de monitoramento sem autenticação JWT (Default-Private Router).

## 4. Task Breakdown (Plano de Implementação)
### Fase 1: Infraestrutura e Integrações
- [ ] [TASK-001] Criar modelo de dados para Aplicações Monitoradas e Histórico de Métricas.
- [ ] [TASK-002] Implementar Zabbix Provider (`src/providers/implementations/zabbix_provider.py`).
- [ ] [TASK-003] Implementar Serviço de Sondagem Assíncrona de Health (`src/services/health_poller.py`).

### Fase 2: API REST & Dashboard Frontend
- [ ] [TASK-004] Criar Roteador REST `/api/monitor` (Endpoints de status, alertas e estatísticas).
- [ ] [TASK-005] Desenvolver Dashboard visual no Vue 3 (Cards, Grid de Saúde, Gráficos e Incidentes).
- [ ] [TASK-006] Validar auditoria de conformidade (`python audit_framework.py .`).

## 5. Critérios de Verificação Global
- [ ] 100% de conformidade no `audit_framework.py`.
- [ ] Cobertura de testes unitários/integração para o poller e Zabbix provider.
- [ ] Zero dados sensíveis hardcoded.
