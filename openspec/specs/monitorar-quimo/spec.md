# monitorar-quimo Specification

## Purpose
Monitoramento do Quimo via HTTPS /api/health, probe TCP PostgreSQL 5432, e coleta de métricas/containers Podman via SSH. O **Quimo** (`10.34.0.191`, `hc-ufpe-vp-sat-quimio`) opera com Nginx (`:443`) fazendo proxy para containers Podman (`quimio_app` FastAPI `:8080` e `quimio_db_app` PostgreSQL 15 `:5432`), além da integração AGHU (`ugen_quimio`). Sua rota `/api/health` retorna apenas `{"status":"healthy","service":...,"version":"1.0.0"}` (sem lista de bancos) e o servidor **não possui Zabbix Agent ativo**, exigindo combinação de `/api/health`, probe TCP `:5432` e coleta SSH.

## Requirements

### Requirement: Health polling and TCP PostgreSQL verification for Quimo
The MonitoraUSID system SHALL poll `https://10.34.0.191/api/health` for HTTP 200 and `version`, probe TCP `10.34.0.191:5432` (`quimio_db_app`), and preserve declared AGHU status.

#### Scenario: `quimio_db_app` stops accepting connections on port 5432 while `quimio_app` returns HTTP 200 on `/api/health`
- **WHEN** `HealthPollerService` executes HTTP and `bancos_adicionais` TCP checks
- **THEN** the database map reports the failure on `PostgreSQL Quimo` (`10.34.0.191:5432`)

### Requirement: Podman and VM telemetry via SSH for Quimo
The MonitoraUSID system MUST collect CPU, memory (GB/%), disk (GB/%), and Podman container status (`quimio_app`, `quimio_db_app`) via `SshMetricsProvider` (`root@10.34.0.191`).

#### Scenario: no Zabbix Agent is active on `10.34.0.191`
- **WHEN** `/api/monitor/dashboard` gathers infrastructure telemetry for Quimo
- **THEN** host resource metrics and container health are populated in the dashboard payload
