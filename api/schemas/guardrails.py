from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID

class GuardrailBase(BaseModel):
    domain: str
    rule: int
    is_active: bool
class GuardrailCreate(GuardrailBase):
    pass
class GuardrailPatch(BaseModel):
    domain: Optional[str] = None
    rule: Optional[int] = None
    is_active: Optional[bool] = None

class GuardrailOut(GuardrailBase):
    model_config = ConfigDict(from_attrubutes = True)

    id: UUID
    user_id: UUID
    domain: str
    rule: int
    is_active: bool
