from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)
@api.get('/')
def healthTest() -> dict[str,str]:
    return {'status':"ok"}
