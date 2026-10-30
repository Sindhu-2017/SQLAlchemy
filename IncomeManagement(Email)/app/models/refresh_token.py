from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
    text,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    __table_args__ = (
        CheckConstraint("expires_at > created_at",name="ck_refresh_token_expiry_after_creation"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    # unique identifier generated for each token
    jti: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        index=True,
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )