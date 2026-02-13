from pydantic import BaseModel
import uuid
class guardrailDTO(BaseModel):
    user_id: uuid.UUID
    domain: str
    rule: int
    is_active: bool