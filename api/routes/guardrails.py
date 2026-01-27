from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from db.session import get_db
from models.domain_guardrail import DomainGuardrail
from core.deps import get_current_user_domain_guardrails
from typing import Dict
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