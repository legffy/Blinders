from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from db.session import get_db
from core.deps import get_current_user_domain_guardrails
from typing import Dict
from models.user import User
from models.domain_guardrail import DomainGuardrail
from schemas.guardrails import guardrailDTO
from core.deps import get_current_user
router: APIRouter = APIRouter(
    prefix = "/guardrails",
    tags = ["guardrails"]
)

@router.get("/")
async def read_guardrails(guardrails: DomainGuardrail = Depends(get_current_user_domain_guardrails)) -> dict:
    return {
        "guardrails":[
            {
                "id": str(gr.id),
                "domain": gr.domain,
                "rule": gr.rule,
                "is_active": gr.is_active
            }
            for gr in guardrails
        ],
        "count": len(guardrails),
    }
@router.post("/")
async def add_guardrail(body: guardrailDTO, db: AsyncSession = Depends(get_db),
                  ):
    guardrail = DomainGuardrail(**body.dict())   
    db.add(guardrail)
    await db.commit()
    await db.refresh(guardrail)
    return {
        "message": "guardrail added",
        "guardrail":{
            "user_id": str(guardrail.user_id),
            "id": str(guardrail.id),
            "domain": str(guardrail.domain),
            "rule": guardrail.rule,
            "is_active": guardrail.is_active
        }
    }