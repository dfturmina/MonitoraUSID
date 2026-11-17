## Context

- Host: `10.34.0.124` (`hc-ufpe-vp-ged`), Ubuntu 22.04.4 LTS.
- Serviços ativos via SSH: `nginx.service` (`:80`), Puma `ruby` (`/home/ubuntu/e-custodia/releases/24/tmp/sockets/puma.sock`), serviços NFS (`nfs-mountd`, `nfsdcld`, porta `:2049`), `bacula-fd` (`:9102`) e `zabbix-agent2.service` (`:10050`, `Server=10.34.0.29,10.34.8.3`, `Hostname=Zabbix server`).
- HTTP verificado: `GET http://10.34.0.124/` -> `302` para `/usuarios/sign_in`; `GET http://10.34.0.124/usuarios/sign_in` -> `200 OK`.
- VM de banco relacionada no inventário: `HC-UFPE-VP-GED-DB`.

## Goals / Non-Goals

**Goals:**
- Garantir monitoramento da disponibilidade HTTP do GED Linus e da integridade do volume de documentos/NFS.
- Superar a ambiguidade de configuração do `zabbix_agent2` garantindo telemetria real de disco e memória.

**Non-Goals:**
- Alterar o código Ruby/Rails em `/home/ubuntu/e-custodia`.

## Decisions

- **Usar `/usuarios/sign_in` como URL monitorada + SSH para Puma/disco**: Evita contabilizar redirect 302 puro sem renderização Rails e garante leitura precisa do uso de disco onde ficam os documentos digitalizados.

## Risks / Trade-offs

- **[Disco de armazenamento de documentos crescer rapidamente]** → Destacar percentual e GB usados de disco via Zabbix ou SSH com alerta preventivo.
