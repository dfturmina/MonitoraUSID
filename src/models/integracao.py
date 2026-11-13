"""
Modelo SQLAlchemy de Integração de Serviços de Terceiros
==========================================================
Armazena chaves de API, URLs e credenciais de integração com sistemas externos
como Metabase, Grafana, Prometheus ou APIs REST customizadas.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from ..resources.database import Base


class Integracao(Base):
    __tablename__ = "integracoes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False, index=True)  # Ex: "Metabase HC-UFPE"
    provedor = Column(String, nullable=False, default="METABASE")  # METABASE, GRAFANA, PROMETHEUS, REST
    url_base = Column(String, nullable=False)  # Ex: "http://relatorios.hc-ufpe.ebserh"
    api_key = Column(String, nullable=False)  # Token / Chave de API
    ativo = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<Integracao id={self.id} nome='{self.nome}' provedor='{self.provedor}' ativo={self.ativo}>"
