## Why

O **GED Linus** (`10.34.0.124`, `hc-ufpe-vp-ged`) hospeda o sistema Rails `e-custodia` (via Puma + Nginx `:80`) e exporta/monta armazenamento NFSv4 (`:2049`) para gestão eletrônica de documentos. A inspeção SSH detectou que o `zabbix-agent2` local está com `Hostname=Zabbix server` genérico no arquivo de configuração, o que pode impedir o Zabbix de associar corretamente o host, exigindo correção ou fallback via SSH.

## What Changes

- Cadastrar a aplicação **GED Linus** apontando para `http://10.34.0.124/usuarios/sign_in` (`possui_rota_health=false`, `criticidade=ALTA`).
- Configurar checagem TCP das portas `:80` (Nginx) e `:2049` (NFS) e verificação via `SshMetricsProvider` (usuário `ubuntu@10.34.0.124`) do processo `puma` (`e-custodia/releases/24/tmp/sockets/puma.sock`), montagem NFS e uso de disco.
- Avaliar/corrigir ou mapear corretamente o `zabbix_host_id` no Zabbix (verificando se o agente responde como `HC-UFPE-VP-GED` ou devido ao `Hostname=Zabbix server` requer fallback SSH).

## Capabilities

### New Capabilities
- `monitorar-ged-linus`: Monitoramento do GED Linus (`e-custodia`) cobrindo Nginx/Puma, NFSv4, espaço em disco crítico de documentos e Zabbix/SSH.

### Modified Capabilities
<!-- Nenhuma capability existente em openspec/specs/ sofreu alteração de contrato base. -->

## Impact

`src/providers/implementations/ssh_metrics_provider.py`, `src/services/health_poller.py`, cadastro em `data/app.db` e Dashboard Vue.
