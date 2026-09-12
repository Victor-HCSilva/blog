from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from core.common_fields import ActivableMixin, TimeStampMixin
from core.database import Base


class Publication(ActivableMixin, TimeStampMixin, Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    document = Column(JSONB, nullable=False)
    presentation = Column(JSONB, nullable=False)
    like = Column(Integer, default=0)
    dislike = Column(Integer, default=0)
    author = relationship("User", back_populates="publications")
