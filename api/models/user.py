from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from db.base import Base
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy.sql import func
class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4, index = True)
    email: Mapped[str] = mapped_column(String, unique = True, nullable = False, index = True)
    password_hash: Mapped[str] = mapped_column(String, nullable = False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), server_default = func.now())
guardrails = relationship(
    "DomainGuardrail",
    backref="user",
    cascade="all, delete-orphan",
)