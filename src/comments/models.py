from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from core.common_fields import ActivableMixin, TimeStampMixin
from core.database import Base


class Comment(ActivableMixin, TimeStampMixin, Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(250), nullable=False)
    publication_id = Column(
        Integer, ForeignKey("publications.id"), nullable=False, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Opcional: Adicionar relacionamentos para carregar fácil o autor ou a publicação
    # user = relationship("User")
    # publication = relationship("Publication")
