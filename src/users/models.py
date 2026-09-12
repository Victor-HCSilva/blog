from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from core.common_fields import ActivableMixin, TimeStampMixin
from core.database import Base


class User(ActivableMixin, TimeStampMixin, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(12), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    publications = relationship(
        "Publication",
        back_populates="author",
        cascade="all, delete-orphan",
    )
