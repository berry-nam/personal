"""Labeling tool API endpoints — auth, tasks, labels, admin, rubric."""

import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    create_access_token,
    get_current_labeler,
    hash_password,
    require_admin,
    verify_password,
)
from app.config import settings
from app.database import get_session
from app.models.labeling_models import (
    LabelingLabel,
    LabelingRubricCriterion,
    LabelingTask,
    LabelingTaskResult,
    LabelingUser,
)
from app.schemas.labeling_schemas import (
    AddCompanyRequest,
    AddResultsRequest,
    BatchResultsRequest,
    LabelingUserOut,
    LoginRequest,
    ProgressOut,
    RegisterRequest,
    RubricCriterionCreate,
    RubricCriterionOut,
    SubmitLabelsRequest,
    TaskDetailOut,
    TaskListResponse,
    TaskResultOut,
    TaskSummaryOut,
    TokenResponse,
)
from app.services import labeling_service

router = APIRouter(prefix="/labeling", tags=["labeling"])


# ── Auth ──────────────────────────────────────────────────────────────────────


@router.post("/auth/register", response_model=TokenResponse)
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_session)):
    if body.invite_code != settings.labeling_invite_code:
        raise HTTPException(status_code=403, detail="Invalid invite code")

    existing = await session.execute(
        select(LabelingUser).where(LabelingUser.email == body.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = LabelingUser(
        email=body.email,
        display_name=body.display_name,
        password_hash=hash_password(body.password),
        invite_code_used=body.invite_code,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token(user.id, user.role)
    return TokenResponse(access_token=token, user=LabelingUserOut.model_validate(user))


@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(LabelingUser).where(LabelingUser.email == body.email, LabelingUser.is_active.is_(True))
    )
    user = result.scalar_one_or_none()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id, user.role)
    return TokenResponse(access_token=token, user=LabelingUserOut.model_validate(user))


@router.get("/auth/me", response_model=LabelingUserOut)
async def me(user: LabelingUser = Depends(get_current_labeler)):
    return user


# ── Tasks ─────────────────────────────────────────────────────────────────────


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(get_current_labeler),
):
    tasks, total = await labeling_service.list_tasks(session, page, size, status)
    pages = math.ceil(total / size) if total else 0

    items = []
    for t in tasks:
        items.append(TaskSummaryOut(
            id=t.id,
            query_id=t.query_id,
            query_text=t.query_text,
            query_metadata=t.query_metadata,
            status=t.status,
            assigned_to=t.assigned_to,
            assigned_at=t.assigned_at,
            completed_at=t.completed_at,
            created_at=t.created_at,
        ))
    return TaskListResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/tasks/current")
async def current_task(
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(get_current_labeler),
):
    """Get the user's currently assigned task (if any), without assigning a new one."""
    result = await session.execute(
        select(LabelingTask)
        .where(LabelingTask.assigned_to == user.id, LabelingTask.status == "assigned")
        .limit(1)
    )
    task = result.scalar_one_or_none()
    if task is None:
        return None
    # Count labels for progress
    label_count = (await session.execute(
        select(func.count(LabelingLabel.id)).where(
            LabelingLabel.task_id == task.id, LabelingLabel.labeler_id == user.id
        )
    )).scalar_one()
    result_count = (await session.execute(
        select(func.count(LabelingTaskResult.id)).where(LabelingTaskResult.task_id == task.id)
    )).scalar_one()
    return {
        "id": task.id,
        "query_id": task.query_id,
        "query_text": task.query_text,
        "result_count": result_count,
        "label_count": label_count,
    }


@router.get("/tasks/next")
async def next_task(
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(get_current_labeler),
):
    task = await labeling_service.get_next_task(session, user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="No tasks available")
    return _task_detail_response(task)


@router.get("/tasks/{task_id}")
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(get_current_labeler),
):
    task = await labeling_service.get_task_detail(session, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return _task_detail_response(task)


@router.post("/tasks/{task_id}/reopen")
async def reopen_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(get_current_labeler),
):
    """Re-open a completed task for editing."""
    result = await session.execute(select(LabelingTask).where(LabelingTask.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status not in ("completed", "reviewed"):
        raise HTTPException(status_code=400, detail="Task is not completed")
    # Only the original labeler or admin can reopen
    if task.assigned_to != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    task.status = "assigned"
    task.completed_at = None
    await session.commit()
    return {"status": "reopened", "task_id": task.id}


@router.post("/tasks/{task_id}/skip")
async def skip_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(get_current_labeler),
):
    ok = await labeling_service.skip_task(session, task_id, user.id)
    if not ok:
        raise HTTPException(status_code=400, detail="Cannot skip this task")
    return {"status": "skipped"}


# ── Labels ────────────────────────────────────────────────────────────────────


@router.post("/tasks/{task_id}/labels")
async def submit_labels(
    task_id: int,
    body: SubmitLabelsRequest,
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(get_current_labeler),
):
    labels_data = [l.model_dump() for l in body.labels]
    created = await labeling_service.submit_labels(session, task_id, user.id, labels_data)
    return {"status": "submitted", "count": len(created)}


@router.post("/tasks/{task_id}/labels/draft")
async def save_draft_labels(
    task_id: int,
    body: SubmitLabelsRequest,
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(get_current_labeler),
):
    labels_data = [l.model_dump() for l in body.labels]
    count = await labeling_service.save_draft_labels(session, task_id, user.id, labels_data)
    return {"status": "draft_saved", "count": count}


# ── Labeler: add company ──────────────────────────────────────────────────────


@router.post("/tasks/{task_id}/add-company")
async def labeler_add_company(
    task_id: int,
    body: AddCompanyRequest,
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(get_current_labeler),
):
    """Let the assigned labeler (or admin) add a company to a task."""
    result = await session.execute(select(LabelingTask).where(LabelingTask.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.assigned_to != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not assigned to this task")

    from sqlalchemy.dialects.postgresql import insert as pg_insert

    # Determine next rank_position (after all existing results)
    max_rank = (await session.execute(
        select(func.max(LabelingTaskResult.rank_position)).where(
            LabelingTaskResult.task_id == task_id
        )
    )).scalar_one_or_none() or 0
    next_rank = max_rank + 1

    # Inject source=manual marker into metadata
    meta = dict(body.company_metadata) if body.company_metadata else {}
    meta["source"] = "manual"

    stmt = pg_insert(LabelingTaskResult).values(
        task_id=task_id,
        company_name=body.company_name,
        company_metadata=meta,
        rank_position=next_rank,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["task_id", "company_name"],
        set_={"company_metadata": stmt.excluded.company_metadata},
    ).returning(LabelingTaskResult.id, LabelingTaskResult.company_name)
    result = await session.execute(stmt)
    row = result.one()
    await session.commit()
    return {"id": row.id, "company_name": row.company_name}


@router.delete("/tasks/{task_id}/results/{result_id}")
async def delete_result(
    task_id: int,
    result_id: int,
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(get_current_labeler),
):
    """Delete a company result from a task (labeler or admin)."""
    result = await session.execute(select(LabelingTask).where(LabelingTask.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.assigned_to != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not assigned to this task")

    tr = await session.execute(
        select(LabelingTaskResult).where(
            LabelingTaskResult.id == result_id, LabelingTaskResult.task_id == task_id
        )
    )
    tr_obj = tr.scalar_one_or_none()
    if tr_obj is None:
        raise HTTPException(status_code=404, detail="Result not found")

    await session.delete(tr_obj)
    await session.commit()
    return {"status": "deleted", "id": result_id}


# ── Admin ─────────────────────────────────────────────────────────────────────


@router.post("/admin/import-queries")
async def import_queries(
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(require_admin),
):
    # Try multiple paths: inside container, or mounted etl directory
    import os
    for candidate in [
        "/app/finetuning_queries_final.json",
        "etl/data/finetuning_queries_final.json",
        "../etl/data/finetuning_queries_final.json",
    ]:
        if os.path.exists(candidate):
            json_path = candidate
            break
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Queries JSON file not found")
    count = await labeling_service.import_queries_from_json(session, json_path)
    return {"imported": count}


@router.post("/admin/tasks/{task_id}/results")
async def add_results(
    task_id: int,
    body: AddResultsRequest,
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(require_admin),
):
    # Verify task exists
    result = await session.execute(select(LabelingTask).where(LabelingTask.id == task_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Task not found")

    results_data = [r.model_dump() for r in body.results]
    count = await labeling_service.add_results_to_task(session, task_id, results_data)
    return {"added": count}


@router.post("/admin/tasks/batch-results")
async def batch_add_results(
    body: BatchResultsRequest,
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(require_admin),
):
    total = 0
    for query_id, results in body.tasks.items():
        result = await session.execute(
            select(LabelingTask).where(LabelingTask.query_id == query_id)
        )
        task = result.scalar_one_or_none()
        if task is None:
            continue
        results_data = [r.model_dump() for r in results]
        total += await labeling_service.add_results_to_task(session, task.id, results_data)
    return {"added": total}


@router.get("/admin/labelers")
async def list_labelers(
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(require_admin),
):
    return await labeling_service.list_labelers(session)


@router.post("/admin/tasks/{task_id}/assign")
async def assign_task(
    task_id: int,
    body: dict,
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(require_admin),
):
    user_id = body.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")
    task = await labeling_service.assign_task(session, task_id, user_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found or not assignable")
    return {"status": "assigned", "task_id": task.id, "assigned_to": user_id}


@router.post("/admin/tasks/bulk-assign")
async def bulk_assign_tasks(
    body: dict,
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(require_admin),
):
    """Bulk assign pending tasks by task number range (1-indexed, all tasks ordered by query_id)."""
    user_id = body.get("user_id")
    start = body.get("start", 1)
    end = body.get("end", 1)
    if not user_id or start < 1 or end < start:
        raise HTTPException(status_code=400, detail="user_id, start, end required (1-indexed)")
    count = await labeling_service.bulk_assign_tasks(session, user_id, start, end)
    return {"status": "assigned", "count": count, "assigned_to": user_id}


@router.post("/admin/tasks/bulk-unassign")
async def bulk_unassign_tasks(
    body: dict,
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(require_admin),
):
    """Unassign tasks from a user. Optionally specify start/end range."""
    user_id = body.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")
    start = body.get("start")
    end = body.get("end")
    count = await labeling_service.bulk_unassign_tasks(session, user_id, start, end)
    return {"status": "unassigned", "count": count}


@router.get("/admin/progress", response_model=ProgressOut)
async def progress(
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(get_current_labeler),
):
    return await labeling_service.get_progress(session)


@router.get("/admin/uc-stats")
async def uc_stats(
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(get_current_labeler),
):
    return await labeling_service.get_uc_stats(session)


@router.get("/admin/export")
async def export_labels(
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(require_admin),
):
    return await labeling_service.export_labels(session)


@router.post("/admin/seed-rubric")
async def seed_rubric(
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(require_admin),
):
    count = await labeling_service.seed_rubric_criteria(session)
    return {"seeded": count}


# ── Rubric ────────────────────────────────────────────────────────────────────


@router.get("/rubric", response_model=list[RubricCriterionOut])
async def list_rubric(
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(get_current_labeler),
):
    result = await session.execute(
        select(LabelingRubricCriterion)
        .where(LabelingRubricCriterion.is_active.is_(True))
        .order_by(LabelingRubricCriterion.display_order)
    )
    return list(result.scalars())


@router.post("/rubric", response_model=RubricCriterionOut)
async def create_rubric_criterion(
    body: RubricCriterionCreate,
    session: AsyncSession = Depends(get_session),
    user: LabelingUser = Depends(require_admin),
):
    criterion = LabelingRubricCriterion(**body.model_dump())
    session.add(criterion)
    await session.commit()
    await session.refresh(criterion)
    return criterion


# ── Helpers ───────────────────────────────────────────────────────────────────


def _task_detail_response(task: LabelingTask) -> dict:
    """Convert a task with eagerly loaded relations to a response dict."""
    return {
        "id": task.id,
        "query_id": task.query_id,
        "query_text": task.query_text,
        "query_metadata": task.query_metadata,
        "status": task.status,
        "assigned_to": task.assigned_to,
        "results": [
            {
                "id": r.id,
                "company_name": r.company_name,
                "company_metadata": r.company_metadata,
                "rank_position": r.rank_position,
            }
            for r in task.results
        ],
        "labels": [
            {
                "id": l.id,
                "result_id": l.result_id,
                "labeler_id": l.labeler_id,
                "overall_rating": l.overall_rating,
                "rank_position": l.rank_position,
                "justification": l.justification,
                "rubric_scores": [
                    {
                        "criterion_id": rs.criterion_id,
                        "score": rs.score,
                        "note": rs.note,
                    }
                    for rs in l.rubric_scores
                ] if hasattr(l, "rubric_scores") and l.rubric_scores else [],
            }
            for l in task.labels
        ],
    }
