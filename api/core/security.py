import bcrypt


def hash_password(password: str) -> str:
    password_bytes: bytes = password.encode("utf-8")
    salt: bytes = bcrypt.gensalt()
    hashed: bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")
def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_bytes: bytes = plain_password.encode("utf-8")
    hashed_bytes: bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hashed_bytes)