## Context

- Host: `10.34.0.111` (`hcpe-vp-maqueiros`), Debian GNU/Linux 11 (bullseye).
- Serviços em execução observados via SSH: `apache2.service` (`:80`), `mariadb.service` (`:3306`), `zabbix-agent2.service` (`:10050`, `Server=10.34.0.29`, `Hostname=HCPE-VP-MAQUEIROS`).
- Aplicação PHP em `/var/www/html/` (contendo `admin_3/loginAD.php` retornando HTTP 200), sem rota `/api/health`.
- Integração AGHU documentada na planilha com usuário `ugen_integra` (porta `6544`).

## Goals / Non-Goals

**Goals:**
- Monitorar disponibilidade web do CSH Maqueiros sem modificar o código PHP em `/var/www/html`.
- Garantir visibilidade da saúde do banco MariaDB local (`3306`) e métricas de VM via Zabbix.

**Non-Goals:**
- Alterar os arquivos PHP do CSH em `10.34.0.111` para criar `/api/health`.
- Monitorar o ambiente de homologação (escopo restrito à produção `10.34.0.111`).

## Decisions

- **Sondagem HTTP direta na URL de login (`admin_3/loginAD.php`)**: A raiz `/` serve um `index.html` estático padrão; validar `/admin_3/loginAD.php` exercita o runtime PHP do Apache. Alternativa descartada: validar apenas `/` (não detectaria falha no PHP-FPM/mod_php).
- **Checagem de banco via `bancos_adicionais` TCP (`3306`) + Zabbix Agent 2**: O host já possui `zabbix-agent2` configurado para `10.34.0.29`, evitando coleta redundante via SSH.

## Risks / Trade-offs

- **[Redirects de autenticação AD alterarem status HTTP]** → Configurar o `HealthPollerService` para aceitar HTTP `< 500` no modo `possui_rota_health=false` e monitorar especificamente erros 5xx ou timeout.
- **[Host ID não cadastrado no Zabbix local do ambiente]** → Incluir tarefa de descoberta/confirmação do `zabbix_host_id` pelo nome `HCPE-VP-MAQUEIROS` via API `host.get`.
