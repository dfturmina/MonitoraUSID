# Proposal: Integração com Sistemas Reais, Métricas Absolutas Zabbix e Suporte Dinâmico à Rota /api/health

## Contexto e Motivação
Para conectar o **MonitoraUSID** a sistemas reais rodando na infraestrutura do hospital (HC-UFPE/SETISD) e integrados ao Zabbix, é preciso evoluir o consumo de métricas e a interpretação dos contratos de resposta:
1. **Valores Absolutos de Hardware:** Além dos percentuais (CPU %, RAM %, Disco %), o Zabbix Provider e a interface devem exibir os valores absolutos utilizados/totais de Memória (ex: `8.2 GB / 16.0 GB`) e Disco (ex: `120.5 GB / 500.0 GB`).
2. **Tempo de Resposta em Vez de "Latência HTTP":** Substituição do termo técnico confuso por **"Tempo de Resposta"** (ms).
3. **Múltiplos Bancos de Dados Dinâmicos:** A rota `/api/health` pode retornar diferentes bancos de dados (PostgreSQL, SQLite, Oracle, etc.). O sistema deve iterar dinamicamente sobre a chave `databases` do JSON sem assumir nomes engessados ("SQLite" ou "PG").
4. **Leitura de Usuários Conectados:** Suporte à exibição da métrica de **Usuários Conectados / Sessões Ativas** retornada na rota `/api/health` dos sistemas baseados no Framework (`active_users` ou `active_sessions`).
5. **Integração Real Híbrida (Zabbix API + Poller HTTP Direct):** 
   - A conectividade e status da aplicação/bancos/usuários são obtidos via requisição HTTP direta na rota `/api/health` cadastrada.
   - O consumo de hardware (CPU, Memória GB, Disco GB e Ping ICMP) e alertas em tempo real são consultados diretamente na API do Zabbix (`zabbix_host_id`).

## Objetivos Principais
- **Métricas em GB:** Exibição clara de RAM e Disco em GB usados/totais.
- **Usuários Ativos:** Card exibindo contagem de usuários conectados no sistema.
- **Suporte a Múltiplos Bancos Genéricos:** Renderização flexível de qualquer banco de dados relatado na rota health.
- **Ajustes de Rótulos:** Substituição de "Latência HTTP" por "Tempo de Resposta".
