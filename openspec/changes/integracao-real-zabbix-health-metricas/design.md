# Design: Estrutura do Payload e Integração Híbrida Real

## Estrutura do Payload `/api/monitor/dashboard`

```json
{
  "applications": [
    {
      "aplicacao_id": 1,
      "nome": "Sistema de Faturamento",
      "full_url": "http://10.233.1.50:8000/api/health",
      "is_online": true,
      "status_http": 200,
      "latency_ms": 14,
      "active_users": 18,
      "versao_semver": "v1.2.0",
      "databases_detail": {
        "Banco Aplicação": "Conectado",
        "Banco AGHU": "Conectado"
      },
      "zabbix": {
        "cpu_usage": 32,
        "memory_used_gb": 8.4,
        "memory_total_gb": 16.0,
        "memory_usage": 52.5,
        "disk_used_gb": 142.0,
        "disk_total_gb": 500.0,
        "disk_usage": 28.4,
        "ping_latency_ms": 5
      }
    }
  ]
}
```

## Ajuste na Rota Health Local (`src/routers/health.py`)

Atualização do endpoint `/api/health` para retornar a contagem de sessões ativas (`active_users`), permitindo que a própria aplicação servidor reporte usuários conectados.
