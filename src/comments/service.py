from fastapi import HTTPException, status
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from comments.models import Comment

password_hash = PasswordHash.recommended()


async def create_Comment_service(
    *, db: AsyncSession, content: str, password: str
) -> Comment:
    result = await db.execute(select(Comment).where(Comment.content == content))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Comment já está em uso."
        )

    new_Comment = Comment(content=content, password=password_hash.hash(password))
    db.add(new_Comment)
    await db.commit()
    await db.refresh(new_Comment)
    return new_Comment


async def list_Comments_service(*, db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Comment).offset(skip).limit(limit))
    return result.scalars().all()


async def get_Comment_service(*, db: AsyncSession, Comment_id: int) -> Comment | None:
    result = await db.execute(select(Comment).where(Comment.id == Comment_id))
    return result.scalars().first()


async def update_Comment_service(
    *, db: AsyncSession, Comment: Comment, content: str | None, password: str | None
) -> Comment:
    if content is not None:
        Comment.content = content
    if password is not None:
        Comment.password = password_hash.hash(password)

    await db.commit()
    await db.refresh(Comment)
    return Comment


async def delete_Comment_service(*, db: AsyncSession, Comment: Comment) -> None:
    Comment.is_active = False
    await db.commit()
