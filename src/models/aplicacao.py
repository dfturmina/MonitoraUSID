"""
Modelo SQLAlchemy de Aplicação Monitorada
===========================================
Representa um sistema do setor cadastrado no Monitora USID para acompanhamento
de disponibilidade (health polling) e métricas/alertas do Zabbix.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from ..resources.database import Base


class Aplicacao(Base):
    __tablename__ = "aplicacoes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False, index=True)
    descricao = Column(String, nullable=True)
    url_base = Column(String, nullable=False)
    possui_rota_health = Column(Boolean, nullable=False, default=True)
    url_health = Column(String, nullable=False, default="/api/health")
    possui_banco_aghu = Column(Boolean, nullable=False, default=False)
    monitora_usuarios_ativos = Column(Boolean, nullable=False, default=False)
    zabbix_host_id = Column(String, nullable=True, index=True)
    criticidade = Column(String, nullable=False, default="MEDIA")  # ALTA, MEDIA, BAIXA
    integracao_id = Column(Integer, nullable=True)  # ID da Integracao cadastrada
    bancos_adicionais = Column(String, nullable=True)  # JSON string com lista de [{"nome": "...", "host": "...", "porta": 5432}]
    tipo_checagem = Column(String, nullable=False, default="HTTP")  # HTTP, TCP, ZABBIX
    porta_tcp = Column(Integer, nullable=True)
    ssh_host = Column(String, nullable=True)  # Alias ~/.ssh/config ou user@ip
    http_headers = Column(String, nullable=True)  # JSON string com headers HTTP customizados
    servicos_monitorados = Column(String, nullable=True)  # JSON string com checks SSH/extra_http
    ativo = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    health_logs = relationship("HealthLog", back_populates="aplicacao", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Aplicacao id={self.id} nome='{self.nome}' criticidade='{self.criticidade}' ativo={self.ativo}>"
