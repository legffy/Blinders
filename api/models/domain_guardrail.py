from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID

from db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
class DomainGuardrail(Base):
    __tablename__ = "domain_guardrails"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4, index = True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid = True),ForeignKey("users.id",ondelete="CASCADE"), nullable = False, index = True)
    domain: Mapped[str] = mapped_column(String, unique = True, nullable = False, index = True)
    rule: Mapped[int] = mapped_column(Integer, nullable = False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable = False)