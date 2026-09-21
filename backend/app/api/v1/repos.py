from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.orm.pull_request import PullRequest
from app.db.orm.repository import Repository
from app.models.pull_request import PullRequestOut
from app.models.repository import RepositoryOut

router = APIRouter(prefix="/repos", tags=["repositories"])


@router.get("", response_model=list[RepositoryOut])
async def list_repositories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Repository).order_by(Repository.created_at.desc()))
    return result.scalars().all()


@router.get("/{repo_id}/prs", response_model=list[PullRequestOut])
async def list_pull_requests(repo_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = await db.get(Repository, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    result = await db.execute(
        select(PullRequest)
        .where(PullRequest.repository_id == repo_id)
        .order_by(PullRequest.updated_at.desc())
    )
    return result.scalars().all()
