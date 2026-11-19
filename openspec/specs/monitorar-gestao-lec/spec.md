# monitorar-gestao-lec Specification

## Purpose
Monitoramento HTTPS + backend FastAPI e telemetria systemd/host via SSH para o Sistema LEC. O sistema **Gestão interna da LEC** (`10.34.0.202`, `HC-UFPE-VP-LEC`) roda como serviço systemd nativo (`sistemalec.service` FastAPI/uvicorn `:8000`) atrás de Nginx HTTPS (`:443`, `comunicacaocirurgica.hc-ufpe.ebserh`). A inspeção via SSH comprovou que o projeto **não possui rota `/api/health`** (`src/routers/health.py` inexistente; `GET /api/health` retorna HTTP 405/404) e **não possui Zabbix Agent ativo**, exigindo sondagem HTTP em `/` + `:8000/docs` e coleta de serviço/métricas via SSH.

## Requirements

### Requirement: Frontend HTTPS and FastAPI backend reachability for Sistema LEC
The MonitoraUSID system SHALL probe `https://10.34.0.202/` (`possui_rota_health=false`) and verify backend FastAPI responsiveness (`:8000/docs` or `sistemalec.service` via SSH).

#### Scenario: `sistemalec.service` crashes while Nginx still responds or returns 502
- **WHEN** the polling cycle checks `https://10.34.0.202/` and `SshMetricsProvider` queries `systemctl is-active sistemalec`
- **THEN** the application card reports offline/degraded status and notifies via Teams

### Requirement: Host resource telemetry via SSH for HC-UFPE-VP-LEC
The MonitoraUSID system MUST collect CPU, memory (GB/%), and disk (GB/%) via `SshMetricsProvider` (`root@10.34.0.202`) since Zabbix Agent is inactive.

#### Scenario: Zabbix Agent is inactive on `10.34.0.202`
- **WHEN** `/api/monitor/dashboard` retrieves metrics for Gestão interna da LEC
- **THEN** real-time host telemetry is rendered in the dashboard card
