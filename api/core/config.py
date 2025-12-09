import os
from pathlib import Path

from dotenv import load_dotenv

env_path: Path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

JWT_SECRET: str = os.getenv("JWT_SECRET")
if JWT_SECRET == "":
    raise RuntimeError("JWT_SECRET is not set")

JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"),
)
