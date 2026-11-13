"""
Roteador de CRUD de Integrações External Services (/api/integracoes)
======================================================================
Permite gerenciar cadastros de chaves de API, URLs e tokens de sistemas externos
como Metabase, Grafana e Prometheus para uso dinâmico pelas aplicações.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..auth.auth import auth_handler
from ..resources.database import get_app_db_session
from ..models.integracao import Integracao

router = APIRouter(
    prefix="/api/integracoes",
    tags=["Integrações de Terceiros"],
    dependencies=[Depends(auth_handler.decode_token)]
)


class IntegracaoCreate(BaseModel):
    nome: str
    provedor: str = "METABASE"  # METABASE, GRAFANA, PROMETHEUS, REST
    url_base: str
    api_key: str
    ativo: bool = True


class IntegracaoResponse(BaseModel):
    id: int
    nome: str
    provedor: str
    url_base: str
    api_key_masked: str
    ativo: bool

    class Config:
        from_attributes = True


@router.get("", response_model=List[IntegracaoResponse])
async def list_integracoes(session: AsyncSession = Depends(get_app_db_session)):
    """Lista todas as integrações cadastradas."""
    stmt = select(Integracao).where(Integracao.ativo == True)
    res = await session.execute(stmt)
    integracoes = res.scalars().all()

    out = []
    for item in integracoes:
        key_masked = f"{item.api_key[:6]}...{item.api_key[-4:]}" if len(item.api_key) > 10 else "***"
        out.append(IntegracaoResponse(
            id=item.id,
            nome=item.nome,
            provedor=item.provedor,
            url_base=item.url_base,
            api_key_masked=key_masked,
            ativo=item.ativo
        ))
    return out


@router.post("", response_model=IntegracaoResponse, status_code=status.HTTP_201_CREATED)
async def create_integracao(
    payload: IntegracaoCreate,
    session: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """Cadastra uma nova integração externa."""
    # Apenas admin pode criar
    if "GLO-SEC-HCPE-SETISD" not in current_user.get("groups", []):
        raise HTTPException(status_code=403, detail="Apenas administradores podem cadastrar integrações.")

    nova = Integracao(
        nome=payload.nome,
        provedor=payload.provedor.upper(),
        url_base=payload.url_base,
        api_key=payload.api_key,
        ativo=payload.ativo
    )
    session.add(nova)
    await session.commit()
    await session.refresh(nova)

    key_masked = f"{nova.api_key[:6]}...{nova.api_key[-4:]}" if len(nova.api_key) > 10 else "***"
    return IntegracaoResponse(
        id=nova.id,
        nome=nova.nome,
        provedor=nova.provedor,
        url_base=nova.url_base,
        api_key_masked=key_masked,
        ativo=nova.ativo
    )


@router.delete("/{integracao_id}")
async def delete_integracao(
    integracao_id: int,
    session: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """Remove uma integração externa."""
    if "GLO-SEC-HCPE-SETISD" not in current_user.get("groups", []):
        raise HTTPException(status_code=403, detail="Apenas administradores podem remover integrações.")

    stmt = select(Integracao).where(Integracao.id == integracao_id)
    res = await session.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Integração não encontrada.")

    item.ativo = False
    await session.commit()
    return {"message": "Integração desativada com sucesso."}
