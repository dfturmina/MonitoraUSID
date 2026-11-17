## Why

O sistema **CSH (Maqueiros) - Produção** (`10.34.0.111`, VM `hcpe-vp-maqueiros`) gerencia os chamados e serviços de hotelaria/maqueiros integrados ao AGHU (`ugen_integra`), porém ainda não está cadastrado nem sondado pelo **MonitoraUSID**. A inspeção via SSH identificou stack Apache/PHP (`:80`), MariaDB local (`:3306`) e `zabbix-agent2` ativo (`HCPE-VP-MAQUEIROS`), permitindo monitoramento completo sem intervenção no código legado.

## What Changes

- Adicionar registro/seed de aplicação para **CSH (Maqueiros) - Produção** apontando para `http://10.34.0.111/admin_3/loginAD.php` (`possui_rota_health=false`, `possui_banco_aghu=true`).
- Configurar monitoramento TCP dinâmico (`bancos_adicionais`) para o MariaDB local (`10.34.0.111:3306`) e verificação da integração AGHU.
- Vincular o `zabbix_host_id` referente ao agente ativo `HCPE-VP-MAQUEIROS` (`Server=10.34.0.29`, porta `10050`) para coleta de CPU, RAM, disco e triggers.

## Capabilities

### New Capabilities
- `monitorar-csh-maqueiros`: Sondagem HTTP da tela de acesso do CSH Maqueiros, checagem TCP do MariaDB local e correlação com o host Zabbix HCPE-VP-MAQUEIROS.

### Modified Capabilities
<!-- Nenhuma capability existente em openspec/specs/ sofreu alteração de contrato base. -->

## Impact

`src/routers/monitor.py`, `src/services/health_poller.py`, seeds/cadastros no banco local `data/app.db` (`aplicacoes`) e Dashboard Vue (`frontend/src/views/Home.vue`).
