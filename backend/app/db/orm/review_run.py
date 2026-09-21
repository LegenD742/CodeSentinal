import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReviewRun(Base):
    """One execution of the full agent pipeline against a specific commit SHA."""
    __tablename__ = "review_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pull_request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pull_requests.id"))
    trigger_sha: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), default="queued")  # see core.constants.RunStatus
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)  # low|medium|high|critical
    verdict_action: Mapped[str | None] = mapped_column(String(20), nullable=True)  # APPROVE|COMMENT|REQUEST_CHANGES
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    agent_trace: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # per-node timings/logs
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    pull_request = relationship("PullRequest", back_populates="review_runs")
    findings = relationship("Finding", back_populates="review_run", cascade="all, delete-orphan")
