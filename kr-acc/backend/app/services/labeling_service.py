"""Business logic for the labeling tool."""

import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.labeling_models import (
    LabelingLabel,
    LabelingRubricCriterion,
    LabelingRubricScore,
    LabelingTask,
    LabelingTaskResult,
    LabelingUser,
)


async def import_queries_from_json(session: AsyncSession, json_path: str) -> int:
    """Import queries from finetuning JSON. Returns count of new tasks created."""
    path = Path(json_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    queries = data["queries"]

    existing = set()
    result = await session.execute(select(LabelingTask.query_id))
    for row in result.scalars():
        existing.add(row)

    count = 0
    for q in queries:
        if q["id"] in existing:
            continue
        task = LabelingTask(
            query_id=q["id"],
            query_text=q["text"],
            query_metadata={
                "uc": q.get("uc"),
                "sector": q.get("sector"),
                "size": q.get("size"),
                "complexity": q.get("complexity"),
                "source": q.get("source"),
                "audit": q.get("audit"),
            },
        )
        session.add(task)
        count += 1

    await session.commit()
    return count


async def list_tasks(
    session: AsyncSession,
    page: int = 1,
    size: int = 20,
    status: str | None = None,
    assigned_to: int | None = None,
) -> tuple[list[LabelingTask], int]:
    """List tasks with optional filtering. Returns (tasks, total)."""
    q = select(LabelingTask)
    count_q = select(func.count(LabelingTask.id))

    if status:
        q = q.where(LabelingTask.status == status)
        count_q = count_q.where(LabelingTask.status == status)
    if assigned_to is not None:
        q = q.where(LabelingTask.assigned_to == assigned_to)
        count_q = count_q.where(LabelingTask.assigned_to == assigned_to)

    total = (await session.execute(count_q)).scalar_one()
    q = q.order_by(LabelingTask.id).offset((page - 1) * size).limit(size)
    result = await session.execute(q)
    return list(result.scalars()), total


async def get_next_task(session: AsyncSession, user_id: int) -> LabelingTask | None:
    """Get the next task assigned to this user. Only admin-assigned tasks can be worked on."""
    result = await session.execute(
        select(LabelingTask)
        .where(LabelingTask.assigned_to == user_id, LabelingTask.status == "assigned")
        .order_by(LabelingTask.query_id)
        .options(selectinload(LabelingTask.results), selectinload(LabelingTask.labels))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_task_detail(session: AsyncSession, task_id: int) -> LabelingTask | None:
    """Get task with results and labels eagerly loaded."""
    result = await session.execute(
        select(LabelingTask)
        .where(LabelingTask.id == task_id)
        .options(
            selectinload(LabelingTask.results),
            selectinload(LabelingTask.labels).selectinload(LabelingLabel.rubric_scores),
        )
    )
    return result.scalar_one_or_none()


async def skip_task(session: AsyncSession, task_id: int, user_id: int) -> bool:
    """Release assignment on a task."""
    result = await session.execute(
        select(LabelingTask).where(
            LabelingTask.id == task_id,
            LabelingTask.assigned_to == user_id,
            LabelingTask.status == "assigned",
        )
    )
    task = result.scalar_one_or_none()
    if task is None:
        return False

    task.status = "pending"
    task.assigned_to = None
    task.assigned_at = None
    await session.commit()
    return True


async def submit_labels(
    session: AsyncSession,
    task_id: int,
    user_id: int,
    labels_data: list[dict],
) -> list[LabelingLabel]:
    """Submit batch labels for a task."""
    # Delete existing labels from this user for this task
    existing = await session.execute(
        select(LabelingLabel).where(
            LabelingLabel.task_id == task_id,
            LabelingLabel.labeler_id == user_id,
        )
    )
    for label in existing.scalars():
        await session.delete(label)
    await session.flush()

    created = []
    for ldata in labels_data:
        label = LabelingLabel(
            task_id=task_id,
            result_id=ldata["result_id"],
            labeler_id=user_id,
            overall_rating=ldata["overall_rating"],
            rank_position=ldata.get("rank_position"),
            justification=ldata.get("justification"),
        )
        session.add(label)
        await session.flush()

        for rs in ldata.get("rubric_scores", []):
            score = LabelingRubricScore(
                label_id=label.id,
                criterion_id=rs["criterion_id"],
                score=rs["score"],
                note=rs.get("note"),
            )
            session.add(score)

        created.append(label)

    # Mark task completed
    await session.execute(
        update(LabelingTask)
        .where(LabelingTask.id == task_id)
        .values(status="completed", completed_at=datetime.now(timezone.utc))
    )
    await session.commit()
    return created


async def save_draft_labels(
    session: AsyncSession,
    task_id: int,
    user_id: int,
    labels_data: list[dict],
) -> int:
    """Save partial labels as draft without completing the task."""
    # Delete existing labels from this user for this task
    existing = await session.execute(
        select(LabelingLabel).where(
            LabelingLabel.task_id == task_id,
            LabelingLabel.labeler_id == user_id,
        )
    )
    for label in existing.scalars():
        await session.delete(label)
    await session.flush()

    count = 0
    for ldata in labels_data:
        label = LabelingLabel(
            task_id=task_id,
            result_id=ldata["result_id"],
            labeler_id=user_id,
            overall_rating=ldata["overall_rating"],
            rank_position=ldata.get("rank_position"),
            justification=ldata.get("justification"),
        )
        session.add(label)
        await session.flush()

        for rs in ldata.get("rubric_scores", []):
            score = LabelingRubricScore(
                label_id=label.id,
                criterion_id=rs["criterion_id"],
                score=rs["score"],
                note=rs.get("note"),
            )
            session.add(score)
        count += 1

    # Keep task as "assigned" — do NOT mark completed
    await session.commit()
    return count


async def add_results_to_task(
    session: AsyncSession, task_id: int, results_data: list[dict]
) -> int:
    """Add or update company results for a task (upsert). Returns count."""
    count = 0
    for r in results_data:
        stmt = pg_insert(LabelingTaskResult).values(
            task_id=task_id,
            company_name=r["company_name"],
            company_metadata=r.get("company_metadata"),
            rank_position=r.get("rank_position"),
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["task_id", "company_name"],
            set_={
                "company_metadata": stmt.excluded.company_metadata,
                "rank_position": stmt.excluded.rank_position,
            },
        )
        await session.execute(stmt)
        count += 1
    await session.commit()
    return count


async def get_progress(session: AsyncSession) -> dict:
    """Dashboard progress stats."""
    total = (await session.execute(select(func.count(LabelingTask.id)))).scalar_one()

    status_counts = {}
    for s in ("pending", "assigned", "completed", "reviewed"):
        cnt = (
            await session.execute(
                select(func.count(LabelingTask.id)).where(LabelingTask.status == s)
            )
        ).scalar_one()
        status_counts[s] = cnt

    # Per-labeler stats — completed + assigned + current task info
    all_users = (
        await session.execute(
            select(LabelingUser).where(LabelingUser.is_active.is_(True))
        )
    ).scalars().all()

    per_labeler = []
    for u in all_users:
        completed = (await session.execute(
            select(func.count(LabelingTask.id)).where(
                LabelingTask.assigned_to == u.id,
                LabelingTask.status.in_(["completed", "reviewed"]),
            )
        )).scalar_one()
        assigned = (await session.execute(
            select(func.count(LabelingTask.id)).where(
                LabelingTask.assigned_to == u.id,
                LabelingTask.status == "assigned",
            )
        )).scalar_one()
        # Current task
        current = (await session.execute(
            select(LabelingTask.query_id).where(
                LabelingTask.assigned_to == u.id,
                LabelingTask.status == "assigned",
            ).limit(1)
        )).scalar_one_or_none()

        # Assigned query_id range → convert to row numbers (1-indexed)
        assigned_range = (await session.execute(
            select(
                func.min(LabelingTask.query_id),
                func.max(LabelingTask.query_id),
            ).where(
                LabelingTask.assigned_to == u.id,
                LabelingTask.status == "assigned",
            )
        )).one()

        range_start_num = None
        range_end_num = None
        if assigned_range[0] and assigned_range[1]:
            # Row number = count of tasks with query_id <= X (all tasks, query_id order)
            range_start_num = (await session.execute(
                select(func.count(LabelingTask.id)).where(
                    LabelingTask.query_id < assigned_range[0]
                )
            )).scalar_one() + 1
            range_end_num = (await session.execute(
                select(func.count(LabelingTask.id)).where(
                    LabelingTask.query_id <= assigned_range[1]
                )
            )).scalar_one()

        per_labeler.append({
            "id": u.id,
            "name": u.display_name,
            "email": u.email,
            "role": u.role,
            "completed": completed,
            "assigned": assigned,
            "current_task": current,
            "assigned_range_start": range_start_num,
            "assigned_range_end": range_end_num,
        })

    return {
        "total_tasks": total,
        **status_counts,
        "per_labeler": per_labeler,
    }


async def assign_task(
    session: AsyncSession, task_id: int, user_id: int
) -> LabelingTask | None:
    """Admin: assign a specific task to a user."""
    result = await session.execute(
        select(LabelingTask).where(LabelingTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    if task is None:
        return None
    if task.status not in ("pending", "assigned"):
        return None

    task.status = "assigned"
    task.assigned_to = user_id
    task.assigned_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(task)
    return task


async def bulk_assign_tasks(
    session: AsyncSession, user_id: int, start_num: int, end_num: int
) -> int:
    """Admin: bulk assign pending tasks by task row number (1-indexed).

    Row numbers are based on *all* tasks ordered by query_id,
    regardless of status. This matches what the admin sees in the UI.
    """
    # Number tasks by query_id order, then pick rows start_num..end_num
    # that are still pending
    all_tasks = await session.execute(
        select(LabelingTask)
        .order_by(LabelingTask.query_id)
        .offset(start_num - 1)
        .limit(end_num - start_num + 1)
    )
    tasks = list(all_tasks.scalars())

    now = datetime.now(timezone.utc)
    count = 0
    for t in tasks:
        if t.status == "pending":
            t.status = "assigned"
            t.assigned_to = user_id
            t.assigned_at = now
            count += 1

    await session.commit()
    return count


async def bulk_unassign_tasks(
    session: AsyncSession,
    user_id: int,
    start_num: int | None = None,
    end_num: int | None = None,
) -> int:
    """Admin: unassign tasks from a user back to pending.

    If start_num/end_num provided, only unassign tasks in that row range.
    Otherwise unassign all assigned tasks for the user.
    """
    if start_num and end_num:
        # Get tasks by row number range (all tasks ordered by query_id)
        all_tasks = await session.execute(
            select(LabelingTask)
            .order_by(LabelingTask.query_id)
            .offset(start_num - 1)
            .limit(end_num - start_num + 1)
        )
        tasks = [
            t for t in all_tasks.scalars()
            if t.assigned_to == user_id and t.status == "assigned"
        ]
    else:
        result = await session.execute(
            select(LabelingTask).where(
                LabelingTask.assigned_to == user_id,
                LabelingTask.status == "assigned",
            )
        )
        tasks = list(result.scalars())

    count = 0
    for t in tasks:
        t.status = "pending"
        t.assigned_to = None
        t.assigned_at = None
        count += 1
    await session.commit()
    return count


async def list_labelers(session: AsyncSession) -> list[dict]:
    """List all active labelers."""
    result = await session.execute(
        select(LabelingUser).where(LabelingUser.is_active.is_(True)).order_by(LabelingUser.id)
    )
    return [
        {"id": u.id, "display_name": u.display_name, "email": u.email, "role": u.role}
        for u in result.scalars()
    ]


async def get_uc_stats(session: AsyncSession) -> list[dict]:
    """Get count of pending tasks grouped by UC (use case) from query_metadata."""
    from sqlalchemy import text
    result = await session.execute(text(
        "SELECT query_metadata->>'uc' as uc, count(*) as cnt "
        "FROM labeling_tasks WHERE status = 'pending' "
        "GROUP BY query_metadata->>'uc' ORDER BY uc"
    ))
    return [{"uc": row[0], "count": row[1]} for row in result.all()]


async def export_labels(session: AsyncSession) -> list[dict]:
    """Export all completed labels for fine-tuning."""
    tasks = await session.execute(
        select(LabelingTask)
        .where(LabelingTask.status.in_(["completed", "reviewed"]))
        .options(
            selectinload(LabelingTask.results),
            selectinload(LabelingTask.labels)
            .selectinload(LabelingLabel.rubric_scores)
            .selectinload(LabelingRubricScore.criterion),
        )
    )

    entries = []
    for task in tasks.scalars():
        results = []
        for label in task.labels:
            # Find matching result
            result_obj = next((r for r in task.results if r.id == label.result_id), None)
            results.append({
                "company_name": result_obj.company_name if result_obj else "unknown",
                "company_metadata": result_obj.company_metadata if result_obj else {},
                "overall_rating": label.overall_rating,
                "rank_position": label.rank_position,
                "justification": label.justification,
                "rubric_scores": {
                    rs.criterion.name: {"score": rs.score, "note": rs.note}
                    for rs in label.rubric_scores
                    if rs.criterion
                },
            })
        entries.append({
            "query_id": task.query_id,
            "query_text": task.query_text,
            "query_metadata": task.query_metadata,
            "results": results,
        })
    return entries


async def seed_rubric_criteria(session: AsyncSession) -> int:
    """Seed v2 rubric criteria. Deactivates old criteria, adds new ones."""
    # Deactivate all existing criteria
    await session.execute(
        update(LabelingRubricCriterion).values(is_active=False)
    )

    defaults = [
        ("업종/사업부합", "요청 업종·사업영역에 해당하는가?", 3, "sector_fit", 1),
        ("매출조건부합", "매출 범위 조건을 충족하는가?", 3, "revenue_fit", 2),
        ("수익성조건부합", "영업이익·이익률 조건을 충족하는가?", 2, "profitability_fit", 3),
        ("규모/형태부합", "기업규모, 기업유형(외감 등) 조건에 맞는가?", 2, "size_fit", 4),
        ("지역조건부합", "수도권·지역 조건에 맞는가?", 1, "location_fit", 5),
        ("투자적합성", "M&A 구조, 소유구조, 성장성 관점에서 적합한가?", 2, "investment_fit", 6),
    ]

    count = 0
    for name, desc, weight, ctype, order in defaults:
        existing = await session.execute(
            select(LabelingRubricCriterion).where(LabelingRubricCriterion.name == name)
        )
        row = existing.scalar_one_or_none()
        if row is None:
            session.add(
                LabelingRubricCriterion(
                    name=name,
                    description=desc,
                    weight=weight,
                    criteria_type=ctype,
                    display_order=order,
                )
            )
            count += 1
        else:
            # Re-activate if it already exists
            row.is_active = True
            row.description = desc
            row.weight = weight
            row.criteria_type = ctype
            row.display_order = order
    await session.commit()
    return count
