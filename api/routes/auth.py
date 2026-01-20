from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import os
import secrets
from urllib.parse import urlencode
import httpx
from db.session import get_db
from models.user import User
from core.security import hash_password,  verify_password
from schemas.auth import SignupBody, LoginBody
from typing import Any, Dict, Optional
from core.security import create_access_token
from pathlib import Path
from core.deps import get_current_user
from core.cookies import (
    COOKIE_SECURE,
    COOKIE_SAMESITE,
    COOKIE_PATH,
    ACCESS_COOKIE_MAX_AGE_SECONDS,
    ACCESS_COOKIE_NAME,
)
from core.cookies import REFRESH_COOKIE_NAME, REFRESH_COOKIE_MAX_AGE_SECONDS
from core.refresh import (
    create_refresh_token_value,
    save_refresh_token,
    validate_refresh_token,
    revoke_refresh_token,
)

router: APIRouter = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/signup")
async def signup(
    body: SignupBody,
    db: AsyncSession = Depends(get_db),
)-> dict:
    stmt = select(User).where(User.email == body.email)
    result = await db.execute(stmt)
    existing_user: User | None = result.scalars().first()

    if existing_user is not None:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Email already registered",
        )
    password_hash: str = hash_password(body.password)

    user: User = User(
        email = body.email,
        password_hash = password_hash
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "message": "Signup successful",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "created_at": user.created_at,
        }
    }
@router.post("/login")
async def login(
        body: LoginBody,
        response: Response,
        db: AsyncSession = Depends(get_db),
)-> dict:
    stmt = select(User).where(User.email == body.email) 
    result  = await db.execute(stmt)
    user: User | None = result.scalars().first()

    if user is None:
        raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Incorrect Email"
            )
    if user.password_hash is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account uses Google sign-in. Please continue with Google.",
        )
    if not verify_password(body.password,user.password_hash):
        raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Incorrect Password"
            )

    access_token: str =create_access_token(str(user.id))
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_COOKIE_MAX_AGE_SECONDS,
        path=COOKIE_PATH,
    )

    refresh_value: str = create_refresh_token_value()
    await save_refresh_token(db, user.id, refresh_value, REFRESH_COOKIE_MAX_AGE_SECONDS)
    response.set_cookie(
        key = REFRESH_COOKIE_NAME,
        value = refresh_value,
        httponly = True,
        secure = COOKIE_SECURE,
        samesite = COOKIE_SAMESITE,
        max_age = REFRESH_COOKIE_MAX_AGE_SECONDS,
        path = COOKIE_PATH,
    )
    return {
            "message": "Login successful",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "created_at":user.created_at,
            },
        }
    
@router.get("/me")
async def read_me(current_user: User = Depends(get_current_user)) -> dict:
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "created_at": current_user.created_at,
    }
@router.post("/logout")
async def logout(request: Request, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    refresh_value: str | None = request.cookies.get(REFRESH_COOKIE_NAME)
    if refresh_value is not None:
        await revoke_refresh_token(db, refresh_value)

    resp: JSONResponse = JSONResponse({"ok": True})
    resp.delete_cookie(
        key=ACCESS_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path=COOKIE_PATH,
    )
    resp.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path=COOKIE_PATH,
    )
    return resp

# Google OAuth

GOOGLE_CLIENT_ID: str = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET: str = os.environ["GOOGLE_CLIENT_SECRET"]

BACKEND_BASE_URL: str = os.environ.get("BACKEND_BASE_URL", "http://localhost:8000")
FRONTEND_BASE_URL: str = os.environ.get("FRONTEND_BASE_URL", "http://localhost:3000")

GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL: str = "https://www.googleapis.com/oauth2/v3/userinfo"

GOOGLE_REDIRECT_URI: str = f"{BACKEND_BASE_URL}/auth/google/callback"
OAUTH_STATE_COOKIE: str = "oauth_state"

class GoogleTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: str
    id_token: str | None = None
    refresh_token: str | None = None


class GoogleUserInfo(BaseModel):
    sub: str
    email: str
    email_verified: bool | None = None
    name: str | None = None
    picture: str | None = None


@router.get("/google/start")
def google_start() -> RedirectResponse:
    state: str = secrets.token_urlsafe(32)

    params: dict[str, str] = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }

    auth_url: str = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    resp: RedirectResponse = RedirectResponse(url=auth_url, status_code=302)

    resp.set_cookie(
        key=OAUTH_STATE_COOKIE,
        value=state,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=10 * 60,
        path=COOKIE_PATH,
    )

    return resp


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    expected_state: str | None = request.cookies.get(OAUTH_STATE_COOKIE)
    if expected_state is None or expected_state != state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")

    async with httpx.AsyncClient(timeout=10.0) as client:
        token_res = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": GOOGLE_REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_res.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to exchange code for token")

        tokens: GoogleTokenResponse = GoogleTokenResponse.model_validate(token_res.json())

        userinfo_res = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens.access_token}"},
        )

        if userinfo_res.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch Google user info")

        guser: GoogleUserInfo = GoogleUserInfo.model_validate(userinfo_res.json())

    # --- Upsert user ---
    # Requires your User model to have: google_sub, name, avatar_url (and password_hash nullable)
    stmt = select(User).where((User.google_sub == guser.sub) | (User.email == guser.email))
    result = await db.execute(stmt)
    user: User | None = result.scalars().first()

    if user is None:
        user = User(
            email=guser.email,
            password_hash=None,
            google_sub=guser.sub,
            name=guser.name,
            avatar_url=guser.picture,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        changed: bool = False
        if getattr(user, "google_sub", None) != guser.sub:
            user.google_sub = guser.sub
            changed = True
        if guser.name is not None and getattr(user, "name", None) != guser.name:
            user.name = guser.name
            changed = True
        if guser.picture is not None and getattr(user, "avatar_url", None) != guser.picture:
            user.avatar_url = guser.picture
            changed = True

        if changed:
            await db.commit()
            await db.refresh(user)

    # Mint your normal JWT + set cookie
    token: str = create_access_token(str(user.id))

    resp: RedirectResponse = RedirectResponse(url=f"{FRONTEND_BASE_URL}/", status_code=302)

    # clear oauth_state cookie
    resp.delete_cookie(
        key=OAUTH_STATE_COOKIE,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path=COOKIE_PATH,
    )

    # set auth cookie
    resp.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_COOKIE_MAX_AGE_SECONDS,
        path=COOKIE_PATH,
    )

    return resp

@router.post("/refresh")
async def refresh(request: Request, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    refresh_value: str | None = request.cookies.get(REFRESH_COOKIE_NAME)
    if refresh_value is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    user_id = await validate_refresh_token(db, refresh_value)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    new_access: str = create_access_token(str(user_id))

    resp: JSONResponse = JSONResponse({"ok": True})
    resp.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=new_access,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_COOKIE_MAX_AGE_SECONDS,
        path=COOKIE_PATH,
    )
    return resp
