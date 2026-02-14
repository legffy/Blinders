from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from db.session import get_db
from core.deps import get_current_user_domain_guardrails
from typing import Dict, Optional, Any
from models.user import User
from models.domain_guardrail import DomainGuardrail
from schemas.guardrails import GuardrailBase, GuardrailCreate, GuardrailOut, GuardrailPatch
from core.deps import get_current_user
from uuid import UUID
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
@router.post("/", response_model = GuardrailOut)
async def add_guardrail(body: GuardrailCreate, db: AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user)) -> GuardrailOut:
    normalized_domain: str = body.domain.strip().lower()

    stmt = insert(DomainGuardrail).values(
        user_id=current_user.id,
        domain=normalized_domain,
        rule=body.rule,
        is_active=body.is_active,
    )

    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id", "domain"],  # must match unique constraint
        set_={
            "rule": body.rule,
            "is_active": body.is_active,
        },
    ).returning(DomainGuardrail)

    result = await db.execute(stmt)
    await db.commit()

    guardrail = result.scalar_one()
    return guardrail
@router.patch("/{guardrail_id}", response_model = GuardrailOut)
async def update_guardrail(guardrail_id: UUID,body: GuardrailPatch, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> GuardrailOut:
    stmt = select(DomainGuardrail).where(DomainGuardrail.id == guardrail_id, DomainGuardrail.user_id == current_user.id)
    result = await db.execute(stmt)
    guardrail: Optional[DomainGuardrail] = result.scalar_one_or_none()
    if guardrail is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Guardrail not found"
        )
    patch_data: dict[str, Any]  = body.model_dump(exclude_unset=True)
    if len(patch_data) == 0:
        # No fields provided; treat as no-op
        return GuardrailOut.model_validate(guardrail)
    for name, value in patch_data.items():
        setattr(guardrail, name, value)
    
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    await db.refresh(guardrail)
    return guardrail
@router.delete("/{guardrail_id}")
async def delete_guardrail(guardrail_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> str:
    stmt = select(DomainGuardrail).where(DomainGuardrail.id == guardrail_id, DomainGuardrail.user_id == current_user.id)
    result = await db.execute(stmt)
    guardrail: Optional[DomainGuardrail] = result.scalar_one_or_none()
    if guardrail is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Guardrail not found"
        )
    try:
        await db.delete(guardrail)
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    return "success"  
