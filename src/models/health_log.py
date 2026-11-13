"""
Modelo SQLAlchemy de Histórico de Health Check (Health Log)
============================================================
Armazena os registros de sondagem periódica da rota /api/health
de cada aplicação monitorada pelo sistema.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..resources.database import Base


class HealthLog(Base):
    __tablename__ = "health_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    aplicacao_id = Column(Integer, ForeignKey("aplicacoes.id"), nullable=False, index=True)
    status_http = Column(Integer, nullable=False, index=True)  # ex: 200, 500, 0 (offline)
    latency_ms = Column(Integer, nullable=False, default=0)
    status_db = Column(String, nullable=True)                  # ex: ok, error, disconnected
    versao_semver = Column(String, nullable=True)              # ex: v1.0.0
    checked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    aplicacao = relationship("Aplicacao", back_populates="health_logs")

    def __repr__(self):
        return f"<HealthLog id={self.id} aplicacao_id={self.aplicacao_id} status_http={self.status_http} latency={self.latency_ms}ms>"
