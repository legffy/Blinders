from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from db.base import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4, index = True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid = True), ForeignKey("users.id", ondelete = "CASCADE"), nullable = False, index = True)

    token_hash: Mapped[str] = mapped_column(String, nullable = False, unique = True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), nullable = False, server_default = func.now(),
                                                 )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), nullable = False)