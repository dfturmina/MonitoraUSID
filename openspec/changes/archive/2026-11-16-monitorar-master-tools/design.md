## Context

- Nós inspecionados via SSH: `rac01.hc-ufpe.ebserh` (`10.34.1.120`, VIPs `.122`, `.125`, `.126`) e `rac02.hc-ufpe.ebserh` (`10.34.1.121`, VIPs `.123`, `.124`), Oracle Linux Server 8.5.
- Processos ativos: Oracle Grid/OHASD (`oracle-ohasd.service`), instâncias Oracle `ora_pmon_hcpe1` / `ora_pmon_hcpe2`, listeners `tnslsnr` na porta `1521` (service `HCPE.WORLD`), `nginx` (`:80`, `:8877`, `:389`, `:8889`), Oracle Forms/Reports (`frmweb`, `rwserver`, Java `:8889`/`:9240`/`:8092`), `node_exporter` (`:9100`) e `zabbix-agent2` (`HCPE-FP-MASTER01` e `HCPE-FP-MASTER02`).

## Goals / Non-Goals

**Goals:**
- Garantir visibilidade independente dos dois nós físicos do Master Tools e de todos os IPs do cluster RAC.
- Detectar indisponibilidade de listeners Oracle (`1521`) ou proxy web (`80`/`8877`) em segundos.

**Non-Goals:**
- Executar queries SQL pesadas diretamente no banco Oracle de produção durante o polling.
- Alterar configurações do Oracle Grid Infrastructure ou `nginx` nos servidores `rac01`/`rac02`.

## Decisions

- **Modelar `rac01` e `rac02` como duas entradas vinculadas no MonitoraUSID**: Cada servidor possui `zabbix_host_id` próprio (`HCPE-FP-MASTER01` e `HCPE-FP-MASTER02`). Alternativa descartada: monitorar apenas o VIP `.125` (ocultaria falha em um dos nós do cluster).
- **Monitoramento dos VIPs `.122`–`.126` via `bancos_adicionais` TCP `:1521`**: Evita criar 7 cards redundantes no dashboard mantendo visibilidade de todos os endpoints SCAN/VIP.

## Risks / Trade-offs

- **[VIPs migrarem entre `rac01` e `rac02` durante failover]** → A checagem TCP por IP continua válida independentemente do nó que detém o VIP; registrar o hostname observado via SSH apenas como metadado informativo.
