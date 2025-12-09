import bcrypt
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt, JWTError

from core.config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def hash_password(password: str) -> str:
    password_bytes: bytes = password.encode("utf-8")
    salt: bytes = bcrypt.gensalt()
    hashed: bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")
def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_bytes: bytes = plain_password.encode("utf-8")
    hashed_bytes: bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hashed_bytes)

def create_access_token(subject: str, extra_claims: Dict[str, Any] | None = None) -> str:
    to_encode: Dict[str,Any]  = extra_claims.copy(timezone.utc) if extra_claims is not None else {}
    expire: datetime = datetime.now(timezone.utc) + timedelta(
        minutes =  ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    to_encode["sub"] = subject
    to_encode["exp"] = expire

    encoded_jwt: str = jwt.encode(
        to_encode,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str) -> Dict[str, Any]:
    payload: Dict[str, Any] = jwt.decode(
        token,
        JWT_SECRET,
        algorithms= [JWT_ALGORITHM],
    )
    print(payload)
    return payload