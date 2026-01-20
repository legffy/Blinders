import os

IS_PROD: bool = os.getenv("ENV") == "prod"

COOKIE_SECURE: bool = True if IS_PROD else False
COOKIE_SAMESITE: str = "none" if IS_PROD else "lax"
COOKIE_PATH: str = "/"

ACCESS_COOKIE_NAME: str = "access_token"
ACCESS_COOKIE_MAX_AGE_SECONDS: int = 60 * 15 # 15 minutes

REFRESH_COOKIE_NAME: str = "refresh_token"
REFRESH_COOKIE_MAX_AGE_SECONDS: int = 60 * 60 * 24 * 14 # 14 days