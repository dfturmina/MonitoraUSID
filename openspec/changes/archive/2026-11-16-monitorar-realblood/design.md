## Context

- VMs Windows identificadas na varredura de rede:
  - `10.34.0.218` (`HC-UFPE-VP-REALBLOOD-APP`): portas abertas `[80, 443, 3389]`; `http://10.34.0.218/` retornou HTTP 200 (IIS).
  - `10.34.0.217` (`HC-UFPE-VP-REALBLOOD-BD`): portas abertas `[80, 443, 1433, 3389]`; `http://10.34.0.217/` retornou HTTP 200 (IIS) e SQL Server ativo em `1433`.
- SSH (`22`) e Zabbix passivo (`10050`) inacessíveis; integração AGHU via `ugen_realblood` (`6544`).

## Goals / Non-Goals

**Goals:**
- Monitorar disponibilidade web da camada de aplicação (`.218`) e porta do SQL Server (`.217:1433`).
- Integrar métricas Windows do Zabbix (caso o agente Windows opere em modo ativo para `10.34.0.29`).

**Non-Goals:**
- Configurar WinRM ou SSH nas VMs Windows do RealBlood nesta change.

## Decisions

- **Usar `http://10.34.0.218/` (APP) como `url_base` e `10.34.0.217:1433` (BD) em `bancos_adicionais`**: Concentra a visão de negócio do RealBlood em um único card cobrindo as duas camadas.

## Risks / Trade-offs

- **[Agente Zabbix Windows ausente ou bloqueado na VM]** → Verificar na API `host.get` do Zabbix se há dados via checks ativos; caso não haja, exibir apenas status HTTP + TCP SQL Server `1433` sem marcar falso erro de hardware.
