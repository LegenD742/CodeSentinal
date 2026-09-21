from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.orm.finding import Finding
from app.db.orm.review_run import ReviewRun
from app.models.review_run import ReviewRunDetailOut

router = APIRouter(prefix="/runs", tags=["findings"])


@router.get("/{run_id}", response_model=ReviewRunDetailOut)
async def get_review_run_with_findings(run_id: UUID, db: AsyncSession = Depends(get_db)):
    run = await db.get(ReviewRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Review run not found")

    result = await db.execute(select(Finding).where(Finding.review_run_id == run_id))
    findings = result.scalars().all()

    return ReviewRunDetailOut(**{**run.__dict__, "findings": findings})
