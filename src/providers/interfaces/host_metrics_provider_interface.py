"""
Interface para Provedores de Métricas de Host (Zabbix / SSH)
==============================================================
Define o contrato padrão para coleta de telemetria de infraestrutura
(CPU, RAM, Disco e serviços locais) independente da origem.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class HostMetricsProviderInterface(ABC):
    """Interface base para provedores de métricas de sistema operacional."""

    @abstractmethod
    async def get_host_metrics(
        self,
        host_identifier: str,
        servicos_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Retorna métricas padronizadas de CPU, memória, disco e serviços do host."""
        pass
