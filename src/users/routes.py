from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from users.schemas import UserCreate, UserResponse, UserUpdate
from users.service import (
    create_user_service,
    delete_user_service,
    get_user_service,
    list_users_service,
    update_user_service,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user_service(
        db=db,
        username=user_in.username,
        password=user_in.password,
    )


@router.get("", response_model=list[UserResponse])
async def list_users(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    return await list_users_service(db=db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_service(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, user_in: UserUpdate, db: AsyncSession = Depends(get_db)
):
    user = await get_user_service(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )

    return await update_user_service(
        db=db,
        user=user,
        username=user_in.username,
        password=user_in.password,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_service(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )

    await delete_user_service(db=db, user=user)
