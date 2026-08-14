from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

# Shared properties
class TaskBase(BaseModel):
    title: str = Field(..., description="The title of the task")
    description: Optional[str] = None
    priority: str = Field(default="Medium")
    order: int = 0
    
    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Title must not be empty')
        return v

class TaskCreate(TaskBase):
    column_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    
    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Title must not be empty')
        return v

class TaskMove(BaseModel):
    column_id: int
    order: Optional[int] = None

class Task(TaskBase):
    id: int
    column_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class ColumnBase(BaseModel):
    title: str
    order: int = 0

class ColumnCreate(ColumnBase):
    board_id: int

class Column(ColumnBase):
    id: int
    board_id: int
    created_at: datetime
    tasks: List[Task] = []

    model_config = {"from_attributes": True}

class BoardBase(BaseModel):
    title: str

class BoardCreate(BoardBase):
    pass

class Board(BoardBase):
    id: int
    created_at: datetime
    columns: List[Column] = []

    model_config = {"from_attributes": True}

# Response models for custom queries
class TaskCountPerColumn(BaseModel):
    column_id: int
    column_title: str
    task_count: int
