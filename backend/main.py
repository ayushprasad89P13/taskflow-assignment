from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import database
import models
import schemas
import crud
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure tables are created (though we have schema.sql, this ensures SQLAlchemy metadata is synced if used without Docker first)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="TaskFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Global exception handler for generic database/server errors
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "type": str(type(exc).__name__)}
    )

@app.get("/boards/{board_id}", response_model=schemas.Board)
def read_board(board_id: int, db: Session = Depends(get_db)):
    try:
        board = crud.get_board(db, board_id=board_id)
        if board is None:
            raise HTTPException(status_code=404, detail="Board not found")
        return board
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error reading board: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed")

@app.post("/tasks", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_task(db=db, task=task)
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Database error creating task: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed")

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    try:
        db_task = crud.update_task(db=db, task_id=task_id, task_update=task)
        if db_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return db_task
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error updating task: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed")

@app.patch("/tasks/{task_id}/move", response_model=schemas.Task)
def move_task(task_id: int, task_move: schemas.TaskMove, db: Session = Depends(get_db)):
    try:
        db_task = crud.move_task(db=db, task_id=task_id, task_move=task_move)
        if db_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return db_task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error moving task: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed")

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    try:
        success = crud.delete_task(db=db, task_id=task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error deleting task: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed")

@app.get("/tasks", response_model=List[schemas.Task])
def read_tasks(priority: str = None, db: Session = Depends(get_db)):
    try:
        if priority:
            return crud.get_tasks_by_priority(db=db, priority=priority)
        else:
            return db.query(models.Task).all()
    except Exception as e:
        logger.error(f"Database error reading tasks: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed")

@app.get("/boards/{board_id}/task-counts", response_model=List[schemas.TaskCountPerColumn])
def get_task_counts(board_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_task_counts_per_column(db=db, board_id=board_id)
    except Exception as e:
        logger.error(f"Database error reading task counts: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed")
