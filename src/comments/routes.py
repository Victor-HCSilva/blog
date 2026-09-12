from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

# Importe os serviços criados anteriormente
from comments.service import (
    create_comment_service,
    delete_comment_service,
    get_comment_service,
    list_comments_by_publication_service,
    update_comment_service,
)

# Importe a função que fornece a sessão do banco
from core.database import get_db

# Importe a dependência que valida o JWT e retorna o usuário logado
from src.auth import get_current_user
from src.users.schemas import UserResponse

router = APIRouter(prefix="/comments", tags=["Comentários"])


# ---------------------------------------------------------
# Schemas (Pydantic)
# ---------------------------------------------------------
class CommentCreate(BaseModel):
    content: str = Field(
        ..., min_length=1, max_length=250, description="Texto do comentário"
    )
    publication_id: int = Field(..., description="ID da publicação comentada")


class CommentUpdate(BaseModel):
    content: str = Field(
        ..., min_length=1, max_length=250, description="Novo texto do comentário"
    )


class CommentResponse(BaseModel):
    id: int
    content: str
    publication_id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------
# Endpoints / Rotas
# ---------------------------------------------------------


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_in: CommentCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Cria um novo comentário na publicação indicada.
    Requer autenticação (o user_id é extraído automaticamente do token JWT).
    """
    new_comment = await create_comment_service(
        db=db,
        content=comment_in.content,
        user_id=current_user.id,
        publication_id=comment_in.publication_id,
    )
    return new_comment


@router.get("/publication/{publication_id}", response_model=list[CommentResponse])
async def list_comments_by_publication(
    publication_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Lista todos os comentários ativos de uma publicação com paginação.
    Rota pública.
    """
    return await list_comments_by_publication_service(
        db=db, publication_id=publication_id, skip=skip, limit=limit
    )


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Busca um comentário específico por ID."""
    comment = await get_comment_service(db=db, comment_id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comentário não encontrado."
        )
    return comment


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_in: CommentUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Atualiza o texto de um comentário.
    Regra: Apenas o próprio autor do comentário pode editá-lo.
    """
    comment = await get_comment_service(db=db, comment_id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comentário não encontrado."
        )

    # Verifica se o usuário autenticado é o dono do comentário
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para editar este comentário.",
        )

    return await update_comment_service(
        db=db, comment=comment, content=comment_in.content
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Exclui logicamente (soft delete) um comentário.
    Regra: Apenas o próprio autor do comentário pode deletá-lo.
    """
    comment = await get_comment_service(db=db, comment_id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comentário não encontrado."
        )

    # Verifica se o usuário autenticado é o dono do comentário
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para excluir este comentário.",
        )

    await delete_comment_service(db=db, comment=comment)
