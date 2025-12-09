import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import decode_access_token
from db.session import get_db
from models.user import User

auth_scheme: HTTPBearer = HTTPBearer(auto_error = False)

async def get_current_user(
        credentials: Annotated[
            HTTPAuthorizationCredentials | None,
            Depends(auth_scheme),
        ],
        db: AsyncSession = Depends(get_db),
) -> User:
    
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Not authenticated",
        )
    token: str = credentials.credentials

    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired token",
        )
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid token payload",
        )
    try:
        user_id  = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid token subject",
        )
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user: User | None = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "User not found",
        )
    return user