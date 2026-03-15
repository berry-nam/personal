"""SQLAlchemy ORM models for the labeling tool."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LabelingUser(Base):
    __tablename__ = "labeling_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    display_name: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20), default="labeler")
    invite_code_used: Mapped[str | None] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )


class LabelingTask(Base):
    __tablename__ = "labeling_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    query_id: Mapped[str] = mapped_column(String(20), unique=True)
    query_text: Mapped[str] = mapped_column(Text)
    query_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    assigned_to: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("labeling_users.id"), nullable=True
    )
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )

    assignee: Mapped["LabelingUser | None"] = relationship()
    results: Mapped[list["LabelingTaskResult"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )
    labels: Mapped[list["LabelingLabel"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )


class LabelingTaskResult(Base):
    __tablename__ = "labeling_task_results"
    __table_args__ = (UniqueConstraint("task_id", "company_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("labeling_tasks.id", ondelete="CASCADE")
    )
    company_name: Mapped[str] = mapped_column(String(200))
    company_metadata: Mapped[dict | None] = mapped_column(JSONB)
    rank_position: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )

    task: Mapped["LabelingTask"] = relationship(back_populates="results")
    labels: Mapped[list["LabelingLabel"]] = relationship(
        back_populates="result", cascade="all, delete-orphan"
    )


class LabelingRubricCriterion(Base):
    __tablename__ = "labeling_rubric_criteria"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    weight: Mapped[int] = mapped_column(Integer, default=3)
    criteria_type: Mapped[str] = mapped_column(String(30), default="other")
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class LabelingLabel(Base):
    __tablename__ = "labeling_labels"
    __table_args__ = (
        UniqueConstraint("task_id", "result_id", "labeler_id"),
        CheckConstraint("overall_rating >= 1 AND overall_rating <= 5"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("labeling_tasks.id", ondelete="CASCADE")
    )
    result_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("labeling_task_results.id", ondelete="CASCADE")
    )
    labeler_id: Mapped[int] = mapped_column(Integer, ForeignKey("labeling_users.id"))
    overall_rating: Mapped[int] = mapped_column(Integer)
    rank_position: Mapped[int | None] = mapped_column(Integer)
    justification: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )

    task: Mapped["LabelingTask"] = relationship(back_populates="labels")
    result: Mapped["LabelingTaskResult"] = relationship(back_populates="labels")
    labeler: Mapped["LabelingUser"] = relationship()
    rubric_scores: Mapped[list["LabelingRubricScore"]] = relationship(
        back_populates="label", cascade="all, delete-orphan"
    )


class LabelingRubricScore(Base):
    __tablename__ = "labeling_rubric_scores"
    __table_args__ = (UniqueConstraint("label_id", "criterion_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    label_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("labeling_labels.id", ondelete="CASCADE")
    )
    criterion_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("labeling_rubric_criteria.id")
    )
    score: Mapped[str] = mapped_column(String(20))
    note: Mapped[str | None] = mapped_column(Text)

    label: Mapped["LabelingLabel"] = relationship(back_populates="rubric_scores")
    criterion: Mapped["LabelingRubricCriterion"] = relationship()
