import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Puxa a URL do .env. Se não achar (rodando fora do docker, por ex), usa o localhost como fallback.
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://hw_user:hw_password@localhost:5432/hw_db"
)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
