import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Finding(Base):
    """A single structured issue raised by an agent and (optionally) verified by the Critic."""
    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("review_runs.id"))

    source_agent: Mapped[str] = mapped_column(String(30))       # bug|security|performance|quality
    category: Mapped[str] = mapped_column(String(30))
    severity: Mapped[str] = mapped_column(String(20))           # critical|high|medium|low|info
    confidence: Mapped[float] = mapped_column(Integer)          # 0-100, post-critic confidence

    file_path: Mapped[str] = mapped_column(String(1000))
    start_line: Mapped[int] = mapped_column(Integer)
    end_line: Mapped[int] = mapped_column(Integer)

    title: Mapped[str] = mapped_column(String(300))
    explanation: Mapped[str] = mapped_column(Text)
    evidence: Mapped[str] = mapped_column(Text)                 # quoted diff/code snippet + tool output
    suggested_fix: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_patch: Mapped[str | None] = mapped_column(Text, nullable=True)  # unified diff, optional

    tool_origin: Mapped[str | None] = mapped_column(String(50), nullable=True)  # semgrep|bandit|eslint|llm|hybrid
    rule_id: Mapped[str | None] = mapped_column(String(200), nullable=True)

    critic_verdict: Mapped[str | None] = mapped_column(String(20), nullable=True)  # confirmed|downgraded|rejected
    critic_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_posted_to_github: Mapped[bool] = mapped_column(Boolean, default=False)
    github_comment_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    review_run = relationship("ReviewRun", back_populates="findings")
