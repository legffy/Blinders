from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.refresh_token import RefreshToken

def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def create_refresh_token_value() -> str:
    return secrets.token_urlsafe(48)

async def save_refresh_token(
        db: AsyncSession,
        user_id: uuid.UUID,
        token_value: str,
        ttl_seconds: int,
) -> None:
    now: datetime = datetime.now(timezone.utc)
    expires_at: datetime = now + timedelta(seconds=ttl_seconds)

    rt: RefreshToken = RefreshToken(
        user_id = user_id,
        token_hash = _hash_token(token_value),
        expires_at = expires_at,
    )
    db.add(rt)
    await db.commit()

async def validate_refresh_token(db: AsyncSession, token_value: str) -> uuid.UUID | None:
    token_hash: str = _hash_token(token_value)
    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    result = await db.execute(stmt)
    rt: RefreshToken | None = result.scalars().first()
    if rt is None:
        return None
    now: datetime = datetime.now(timezone.utc)
    if rt.expires_at <= now:
        await db.execute(delete(RefreshToken).where(RefreshToken.id == rt.id))
        await db.commit()
        return None
    return rt.user_id
async def revoke_refresh_token(db: AsyncSession, token_value: str) -> None:
    token_hash: str = _hash_token(token_value)
    await db.execute(delete(RefreshToken).where(RefreshToken.token_hash == token_hash))
    await db.commit()