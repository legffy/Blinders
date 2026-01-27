import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import decode_access_token
from db.session import get_db
from models.user import User
from models.domain_guardrail import DomainGuardrail

auth_scheme: HTTPBearer = HTTPBearer(auto_error = False)

async def get_current_user(
        request: Request,
        db: AsyncSession = Depends(get_db),
) -> User:
    

    token: str | None = request.cookies.get("access_token")
    if token is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing access_token cookie",
    )
    try:
        payload: dict = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id: uuid.UUID = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user: User | None = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
async def get_current_user_domain_guardrails(user: User = Depends(get_current_user), db:AsyncSession = Depends(get_db)) -> DomainGuardrail:
    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Missing user"
        )
    try:
        user_id: uuid.UUID = user.id
    except ValueError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail  ="Invalid user id",
        )
    stmt = select(DomainGuardrail).where(DomainGuardrail.user_id == user_id)
    result = await db.execute(stmt)
    DomainGuardrails: list[DomainGuardrail] | None = result.scalars().all()
    if DomainGuardrails is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detial = "Domains not found",
        )
    return DomainGuardrails
