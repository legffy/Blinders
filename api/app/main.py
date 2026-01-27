from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.session import engine
from sqlalchemy import text
from routes import auth
from routes import guardrails
api = FastAPI()
api.include_router(auth.router)
api.include_router(guardrails.router)

api.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000","https://blinders-sigma.vercel.app","chrome-extension://ojfeionphkobiplkdlcbejikdddimjdg"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)
@api.get('/')
async def healthTest() -> dict[str,str]:
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return {'status':"here"}
    except Exception as e:
        return {"status": "error","detail": str(e)}

