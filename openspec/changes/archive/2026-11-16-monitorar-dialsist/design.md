## Context

- Host: `10.34.0.83` (`hc-ufpe-vp-dialsist`), Debian GNU/Linux 12 (bookworm).
- Serviços ativos via SSH: `apache2.service` (`:80`), `mysql.service` (`:3306`, `:33060`), `xrdp.service` (`:3389`), `firewalld.service`, `zabbix-agent.service` (`:10050`, `Server=10.34.0.29,10.34.0.127`, `Hostname=HC-UFPE-VP-DIALSIST`).
- Pastas web em `/var/www/html/`: `ufpeds4`, `ufpe`, `ufpeintegracao`, `teste_ufpe`, `teste.php`; `http://10.34.0.83/ufpeds4/` retornou HTTP 200.

## Goals / Non-Goals

**Goals:**
- Monitorar continuamente o portal web do Dialsist, MySQL local e acessibilidade ao AGHU Slave.
- Correlacionar alertas do agente Zabbix ativo no dashboard.

**Non-Goals:**
- Alterar os arquivos PHP em `/var/www/html/ufpeds4` ou a configuração do `xrdp`.

## Decisions

- **Usar `/ufpeds4/` (ou entrypoint confirmado com a equipe) em vez da raiz `/`**: A raiz `/` serve o `index.html` padrão do Apache; validar `/ufpeds4/` direciona a sondagem para o diretório real da aplicação Dialsist.

## Risks / Trade-offs

- **[`firewalld` ativo no host bloquear portas específicas conforme origem]** → Validar acesso HTTP `:80` e TCP `:3306` a partir do servidor onde o MonitoraUSID roda durante a implantação.
