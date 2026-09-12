from sqlalchemy import Boolean, Column, DateTime, func


class ActivableMixin:
    is_active = Column(Boolean, default=True, nullable=False)


class TimeStampMixin:
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
