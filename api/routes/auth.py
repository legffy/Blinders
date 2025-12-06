from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.session import get_db
from models.user import User
from core.security import hash_password,  verify_password
from schemas.auth import SignupBody, LoginBody

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
        db: AsyncSession = Depends(get_db)
)-> dict:
    stmt = select(User).where(User.email == body.email) 
    result  = await db.execute(stmt)
    user: User | None = result.scalars().first()

    if user is None:
        raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Incorrect Email"
            )

    if not verify_password(body.password,user.password_hash):
        raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Incorrect Password"
            )
    return {
            "message": "Login successful",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "created_at":user.created_at,
            }
        }
        

