from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, DateTime, func
from pydantic import BaseModel
from db.session import get_db
from core.deps import get_current_user_domain_guardrails
from typing import Dict, Optional, Any
from models.user import User
from models.domain_guardrail import DomainGuardrail
from models.guardrail_state import GuardrailState
from schemas.guardrails import GuardrailBase, GuardrailCreate, GuardrailOut, GuardrailPatch
from core.deps import get_current_user
from uuid import UUID
from sqlalchemy.dialects.postgresql import insert

async def bump_guardrail_version(db: AsyncSession, user_id: UUID) -> int:
    stmt = insert(GuardrailState).values(user_id = user_id, version = 1)
    stmt = stmt.on_conflict_do_update(
        index_elements = [GuardrailState.user_id],
        set_ = {
            "version": GuardrailState.version + 1,
            "updated_at": func.now(),
        },
    ).returning(GuardrailState.version)

    result = await db.execute(stmt)
    new_version: int = result.scalar_one()
    return new_version
class GuardrailsMetaOut(BaseModel):
    version: int
router: APIRouter = APIRouter(
    prefix = "/guardrails",
    tags = ["guardrails"]
)

def normalize_domain(raw: str) -> str:
    d: str = raw.strip().lower()
    if d.startswith("www."):
        d = d[4:]
    return d
@router.get("/")
async def read_guardrails(guardrails: DomainGuardrail = Depends(get_current_user_domain_guardrails)):
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
    normalized_domain: str = normalize_domain(body.domain)
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
    await bump_guardrail_version(db, current_user.id)
    await db.commit()

    guardrail = result.scalar_one()
    return guardrail
@router.patch("/{guardrail_id}", response_model=GuardrailOut)
async def update_guardrail(
    guardrail_id: UUID,
    body: GuardrailPatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GuardrailOut:
    stmt = select(DomainGuardrail).where(
        DomainGuardrail.id == guardrail_id,
        DomainGuardrail.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    guardrail: Optional[DomainGuardrail] = result.scalar_one_or_none()
    if guardrail is None:
        raise HTTPException(status_code=404, detail="Guardrail not found")

    patch_data: dict[str, Any] = body.model_dump(exclude_unset=True)

    new_domain: Optional[str] = None
    if "domain" in patch_data and patch_data["domain"] is not None:
        d: str = str(patch_data["domain"]).strip().lower()
        if d.startswith("www."):
            d = d[4:]
        new_domain = d

    # If changing domain, check for collision first
    if new_domain is not None and new_domain != guardrail.domain:
        collision_stmt = select(DomainGuardrail).where(
            DomainGuardrail.user_id == current_user.id,
            DomainGuardrail.domain == new_domain,
        )
        collision_result = await db.execute(collision_stmt)
        existing: Optional[DomainGuardrail] = collision_result.scalar_one_or_none()

        if existing is not None:
            # merge updates into existing
            if "rule" in patch_data:
                existing.rule = int(patch_data["rule"])
            if "is_active" in patch_data:
                existing.is_active = bool(patch_data["is_active"])

            # delete the one we were patching
            await db.delete(guardrail)

            await bump_guardrail_version(db, current_user.id)
            await db.commit()
            await db.refresh(existing)
            return existing

        # no collision => safe to change domain
        guardrail.domain = new_domain

    # apply rest of updates
    for k, v in patch_data.items():
        if k == "domain":
            continue
        setattr(guardrail, k, v)

    await bump_guardrail_version(db, current_user.id)

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail="You already have a guardrail for that domain.") from e

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
    await db.delete(guardrail)
    await bump_guardrail_version(db, current_user.id)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    return Response(status_code = status.HTTP_204_NO_CONTENT) 



@router.get("/meta", response_model = GuardrailsMetaOut)
async def guardrails_meta(db: AsyncSession = Depends(get_db), 
                          current_user: User = Depends(get_current_user)) -> GuardrailsMetaOut:
    stmt = select(GuardrailState.version).where(GuardrailState.user_id == current_user.id)
    result = await db.execute(stmt)
    version: Optional[int] = result.scalar_one_or_none()
    return GuardrailsMetaOut(version = version or 0)