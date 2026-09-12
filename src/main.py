import asyncio
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.routes import router as auth_router
from core.database import Base, engine
from publication.routes import router as publication_router
from users.routes import router as users_router

logger = logging.getLogger(__name__)

origins = os.getenv("ALLOW_ORIGINS", "http://localhost:3000").split(",")
debug = os.getenv("DEBUG", "true").lower() == "true"
title = os.getenv("API_TITLE", "API").capitalize()
description = os.getenv("DESCRIPTION", "DESCRIPTION").capitalize()

app = FastAPI(title=title, description=description, debug=debug)

if len(origins) == 0:
    logger.warning("O fallback está ativo, verifique a configuração do arquivo .env.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=os.getenv("ALLOW_CREDENTIALS", "true").lower() == "true",
    allow_methods=os.getenv("ALLOW_METHODS", "GET,PUT,POST,PATCH,DELETE").split(","),
    allow_headers=os.getenv("ALLOW_HEADERS", "*").split(","),
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(publication_router)


@app.on_event("startup")
async def startup():
    for attempt in range(1, 11):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Banco de dados conectado com sucesso")
                return
        except Exception as error:
            logger.warning(
                "Tentativa %d/10 de conexão ao banco falhou: %s", attempt, error
            )
            if attempt < 10:
                await asyncio.sleep(2)

    raise RuntimeError("Não foi possível conectar ao banco de dados após 10 tentativas")
