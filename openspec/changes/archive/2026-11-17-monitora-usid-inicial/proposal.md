# Proposal: Sistema Monitora USID (Monitoramento Visual de Sistemas do Setor)

## Contexto e Motivação
A equipe do SETISD / USID (Hospital das Clínicas da UFPE) necessita de um sistema centralizado e altamente intuitivo para monitorar a saúde, disponibilidade e desempenho das aplicações do setor. Embora o Zabbix capture métricas de infraestrutura e o Grafana forneça dashboards técnicos, há uma demanda por uma solução customizada, visualmente atraente e com excelente usabilidade para o dia a dia operacional e executivo da equipe.

O **Monitora USID** é construído sobre a arquitetura de referência `Framework-SETISD-HC-UFPE` (Python FastAPI + Vue 3 / Vite), herdando segurança (AD/LDAP, RBAC, Security Headers, audit logs), padronização e facilidade de manutenção.

## Objetivos Principais
1. **Visualização Superior & UX Moderna:** Interface visual estilo Dashboard executivo/operacional com componentes ricos, cards de status em tempo real e visualização de incidentes.
2. **Integração com Zabbix:** Conectar-se à API do Zabbix para extrair status de hosts, alertas ativos (triggers) e métricas de desempenho.
3. **Consumo de Rota Health Padronizada:** Consumir periodicamente a rota `/api/health` de cada sistema baseado no Framework SETISD para monitorar status do banco de dados, versão e disponibilidade do serviço.
4. **Alertas & Notificações Visuais:** Painel de incidentes com priorização por severidade (Crítico, Alto, Médio, Baixo).

## Escopo das Modificações Iniciais
- **Documentação Base:** Atualização do `README.md` e dos documentos em `docs/especificacao/` para refletir o produto **Monitora USID**.
- **Modelagem Inicial:** Estruturação dos modelos de dados para cadastro de Aplicações Monitoradas, Endpoints Health, Credenciais/Integração Zabbix e Histórico de Métricas.
- **Backend FastAPI:** Inclusão de serviços/controllers para polling de `/api/health` e integração com a API Zabbix.
- **Frontend Vue 3:** Interface web responsiva com visualização de cards de status, gráficos de disponibilidade e tabelas de incidentes.
