from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ZabbixProviderInterface(ABC):
    """Interface para provedores de dados e integração com o Zabbix."""

    @abstractmethod
    async def get_active_problems(self, host_ids: List[str] | None = None) -> List[Dict[str, Any]]:
        """Retorna a lista de triggers/problemas ativos do Zabbix."""
        pass

    @abstractmethod
    async def get_host_metrics(self, host_id: str) -> Dict[str, Any]:
        """Retorna métricas chave (CPU, Memória, Status) de um host específico."""
        pass
