from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from contextlib import contextmanager
import models
import schemas
import logging

logger = logging.getLogger(__name__)

@contextmanager
def commit_or_rollback(db: Session):
    try:
        yield
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise

def get_board(db: Session, board_id: int) -> Optional[models.Board]:
    """Fetch a board by ID with eager-loaded columns and tasks."""
    return db.query(models.Board).filter(models.Board.id == board_id).first()


def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    """Create a new task from validated Pydantic schema data."""
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    with commit_or_rollback(db):
        pass
    db.refresh(db_task)
    return db_task


def update_task(
    db: Session, task_id: int, task_update: schemas.TaskUpdate
) -> Optional[models.Task]:
    """Update an existing task's title, description, or priority."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return None

    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)

    with commit_or_rollback(db):
        pass
    db.refresh(db_task)
    return db_task


def move_task(
    db: Session, task_id: int, task_move: schemas.TaskMove
) -> Optional[models.Task]:
    """Move a task to a different column (and optionally reorder)."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return None

    db_task.column_id = task_move.column_id
    if task_move.order is not None:
        db_task.order = task_move.order

    with commit_or_rollback(db):
        pass
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    """Delete a task by ID. Returns False if task not found."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return False

    with commit_or_rollback(db):
        db.delete(db_task)
    return True


def get_task_counts_per_column(
    db: Session, board_id: int
) -> list[schemas.TaskCountPerColumn]:
    """
    Returns the count of tasks per column on a specific board using raw SQL.
    Note: "order" is quoted because it is a reserved word in SQL/SQLite.
    """
    query = text("""
        SELECT c.id   AS column_id,
               c.title AS column_title,
               COUNT(t.id) AS task_count
        FROM   columns c
        LEFT JOIN tasks t ON c.id = t.column_id
        WHERE  c.board_id = :board_id
        GROUP BY c.id, c.title
        ORDER BY c."order"
    """)

    result = db.execute(query, {"board_id": board_id})
    return [
        schemas.TaskCountPerColumn(
            column_id=row.column_id,
            column_title=row.column_title,
            task_count=row.task_count,
        )
        for row in result
    ]


def get_tasks_by_priority(db: Session, priority: str) -> list[models.Task]:
    """
    Returns tasks filtered by a specific priority, ordered by created_at DESC
    using the SQLAlchemy query builder.
    """
    return (
        db.query(models.Task)
        .filter(models.Task.priority == priority)
        .order_by(models.Task.created_at.desc())
        .all()
    )
