from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import models
import schemas
import logging

logger = logging.getLogger(__name__)

def get_board(db: Session, board_id: int) -> Optional[models.Board]:
    return db.query(models.Board).filter(models.Board.id == board_id).first()

def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    try:
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating task: {e}")
        raise

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate) -> Optional[models.Task]:
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return None
    
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
        
    try:
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating task: {e}")
        raise

def move_task(db: Session, task_id: int, task_move: schemas.TaskMove) -> Optional[models.Task]:
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return None
        
    db_task.column_id = task_move.column_id
    if task_move.order is not None:
        db_task.order = task_move.order
        
    try:
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        logger.error(f"Error moving task: {e}")
        raise

def delete_task(db: Session, task_id: int) -> bool:
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return False
        
    try:
        db.delete(db_task)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting task: {e}")
        raise

# Specific database repository functions using raw SQL

def get_task_counts_per_column(db: Session, board_id: int) -> List[schemas.TaskCountPerColumn]:
    """
    Returns the count of tasks per column on a specific board using raw SQL.
    """
    query = text(\"\"\"
        SELECT c.id AS column_id, c.title AS column_title, COUNT(t.id) AS task_count
        FROM columns c
        LEFT JOIN tasks t ON c.id = t.column_id
        WHERE c.board_id = :board_id
        GROUP BY c.id, c.title
        ORDER BY c.order
    \"\"\")
    
    try:
        result = db.execute(query, {"board_id": board_id})
        counts = []
        for row in result:
            counts.append(schemas.TaskCountPerColumn(
                column_id=row.column_id,
                column_title=row.column_title,
                task_count=row.task_count
            ))
        return counts
    except Exception as e:
        logger.error(f"Error in get_task_counts_per_column: {e}")
        raise

def get_tasks_by_priority(db: Session, priority: str) -> List[models.Task]:
    """
    Returns tasks filtered by a specific priority, ordered by created_at DESC using query builder.
    """
    try:
        # Using explicit query builder code
        return db.query(models.Task).filter(
            models.Task.priority == priority
        ).order_by(
            models.Task.created_at.desc()
        ).all()
    except Exception as e:
        logger.error(f"Error in get_tasks_by_priority: {e}")
        raise
