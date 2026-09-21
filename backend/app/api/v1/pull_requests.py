from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.orm.pull_request import PullRequest
from app.db.orm.review_run import ReviewRun
from app.models.pull_request import PullRequestOut
from app.models.review_run import ReviewRunOut

router = APIRouter(prefix="/prs", tags=["pull_requests"])


@router.get("/{pr_id}", response_model=PullRequestOut)
async def get_pull_request(pr_id: UUID, db: AsyncSession = Depends(get_db)):
    pr = await db.get(PullRequest, pr_id)
    if pr is None:
        raise HTTPException(status_code=404, detail="Pull request not found")
    return pr


@router.get("/{pr_id}/runs", response_model=list[ReviewRunOut])
async def list_review_runs(pr_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ReviewRun).where(ReviewRun.pull_request_id == pr_id).order_by(ReviewRun.started_at.desc())
    )
    return result.scalars().all()
