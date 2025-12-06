from pydantic import BaseModel, EmailStr


class SignupBody(BaseModel):
    email: EmailStr
    password: str
class LoginBody(BaseModel):
    email: EmailStr
    password: str