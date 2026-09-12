from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from comments.models import Comment


async def create_comment_service(
    *, db: AsyncSession, content: str, user_id: int, publication_id: int
) -> Comment:
    """Cria um comentário associado ao usuário logado e à publicação."""
    new_comment = Comment(
        content=content,
        user_id=user_id,
        publication_id=publication_id,
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment


async def list_comments_by_publication_service(
    *, db: AsyncSession, publication_id: int, skip: int = 0, limit: int = 10
):
    """Lista comentários ativos de uma publicação específica."""
    query = (
        select(Comment)
        .where(Comment.publication_id == publication_id, Comment.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


async def get_comment_service(*, db: AsyncSession, comment_id: int) -> Comment | None:
    """Busca um comentário ativo por ID."""
    query = select(Comment).where(Comment.id == comment_id, Comment.is_active == True)
    result = await db.execute(query)
    return result.scalars().first()


async def update_comment_service(
    *, db: AsyncSession, comment: Comment, content: str
) -> Comment:
    """Atualiza o conteúdo do comentário."""
    comment.content = content

    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment_service(*, db: AsyncSession, comment: Comment) -> None:
    """Realiza a exclusão lógica (soft delete)."""
    comment.is_active = False
    await db.commit()
