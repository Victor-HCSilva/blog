from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class PublicationState(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    state = Column(String(20), default=PublicationState.DRAFT, nullable=False)

    # 1. Conteúdo estruturado (Document AST)
    document = Column(JSONB, nullable=False)

    # 2. Apresentação customizada do autor (Tokens & Theme)
    presentation = Column(JSONB, nullable=False)

    # 3. Classificação e Metadados
    tags = Column(ARRAY(String(50)), default=list, nullable=False)
    reading_time_minutes = Column(Integer, default=1)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    author = relationship("User", back_populates="publications")
    interactions = relationship("UserInteraction", back_populates="publication")

    __table_args__ = (Index("ix_publications_tags", "tags", postgresql_using="gin"),)


class UserInteraction(Base):
    """
    Rastreamento essencial para o ciclo:
    CONSUMIR -> AVALIAR -> RECOMENDAR
    """

    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    publication_id = Column(Integer, ForeignKey("publications.id"), nullable=False)

    # Métricas de consumo consciente (não compulsivo)
    read_ratio = Column(Float, default=0.0)  # % do documento lido (scroll depth)
    time_spent_seconds = Column(Integer, default=0)
    rating = Column(Integer, nullable=True)  # Avaliação explícita (1 a 5 estrelas)
    saved = Column(Integer, default=0)  # 1 se favoritou/salvou

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
