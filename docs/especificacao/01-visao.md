# Documento de Visão - Monitora USID

## 1. Problema e Oportunidade
* **O Problema**: O setor de TI e Saúde Digital (SETISD) necessita acompanhar em tempo real a disponibilidade de diversos sistemas e serviços de infraestrutura. Ferramentas tradicionais como Zabbix e Grafana fornecem dados técnicos profundos, mas carecem de uma visão consolidada, amigável e com usabilidade focada no contexto operacional do setor.
* **Impacto**: Dificuldade em identificar rapidamente falhas de aplicação (ex: queda de banco de dados específico ou lentidão na rota health) e falta de um painel sintético executivo para acompanhamento do status do ecossistema de TI.
* **Solução Proposta**: O **Monitora USID** é uma plataforma visual centralizada que consome métricas do Zabbix e realiza sondagem da rota `/api/health` das aplicações do hospital, exibindo dashboards visuais modernos e intuitivos.

## 2. Partes Interessadas (Stakeholders)
* Equipe de TI e Desenvolvimento (SETISD/HC-UFPE).
* Gestão de TI e Coordenação do Setor.
* Operadores de Infraestrutura e Suporte.

## 3. Escopo do Produto
* Dashboard visual em tempo real com cards de status, gráficos de disponibilidade e painel de incidentes.
* Integração com Zabbix API para alertas e métricas.
* Polling automatizado da rota `/api/health` de aplicações baseadas no Framework SETISD.
* Autenticação corporativa AD/LDAP e controle de acesso RBAC.

## 4. Metas e Objetivos de Negócio
* Reduzir o tempo médio de detecção (MTTD) de indisponibilidade de aplicações em até 50%.
* Centralizar o status de saúde de 100% dos sistemas do SETISD em um único painel.