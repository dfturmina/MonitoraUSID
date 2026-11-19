## Context

- Host: `10.34.0.219` (`hc-ufpe-vp-wokibi`), Debian GNU/Linux 13 (trixie).
- Serviços ativos via SSH: `next-server` (`:3000`, HTTP 200), `python app_anony.py` (`:8080/health` -> `{"model":"noharm-ai/anony","ready":true}`), container Docker `wokibi-mongodb` (`mongo`, `:27017`), `jupyter-lab` (`127.0.0.1:8888`).
- `zabbix-agent` e `zabbix-agent2` estão inativos.
- Integração AGHU prevista (`ugen_wokibi` `:5432`).

## Goals / Non-Goals

**Goals:**
- Monitorar tanto a disponibilidade do modelo de IA (`ready: true`) quanto o frontend web e o MongoDB.
- Fornecer telemetria de CPU/RAM/Disco no dashboard via `SshMetricsProvider` usando o mesmo contrato de saída do Zabbix.

**Non-Goals:**
- Instalar `zabbix-agent2` na VM `10.34.0.219`.
- Gerenciar ou reiniciar notebooks do `jupyter-lab`.

## Decisions

- **Usar `/health` na porta `8080` como health check primário e checar `:3000` como serviço/endpoint adicional**: `/health` retorna explicitamente `ready: true` para o modelo `noharm-ai/anony`.
- **Padronizar `SshMetricsProvider` com cache TTL (ex.: 30s) e coleta assíncrona (`asyncssh`)**: Evita abrir sessões SSH a cada refresh rápido da UI e mantém a thread principal do FastAPI desbloqueada.

## Risks / Trade-offs

- **[Latência ou timeout SSH atrasar o endpoint `/api/monitor/dashboard`]** → Executar coleta SSH em paralelo com `asyncio.gather` e timeout curto (3–4s), com cache em memória e fallback gracioso.
