import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app
import crud
import models
import schemas

# Setup in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # Seed data for tests
    board = models.Board(title="Test Board")
    db.add(board)
    db.commit()
    db.refresh(board)
    
    col1 = models.ColumnModel(board_id=board.id, title="To Do", order=0)
    col2 = models.ColumnModel(board_id=board.id, title="Done", order=1)
    db.add_all([col1, col2])
    db.commit()
    db.refresh(col1)
    db.refresh(col2)
    
    task1 = models.Task(column_id=col1.id, title="Task 1", priority="High")
    task2 = models.Task(column_id=col1.id, title="Task 2", priority="Medium")
    db.add_all([task1, task2])
    db.commit()
    
    yield db
    
    # Teardown
    Base.metadata.drop_all(bind=engine)
    db.close()

def test_create_task_empty_title_fails(setup_database):
    db = setup_database
    # Get a valid column_id
    col = db.query(models.ColumnModel).first()
    
    response = client.post(
        "/tasks",
        json={"title": "", "column_id": col.id, "priority": "Low"}
    )
    
    assert response.status_code == 422
    data = response.json()
    # Pydantic handles validation, so detail might be a string (custom error) or array (pydantic default)
    # The requirement is just that it returns 400/422.
    assert "detail" in data

def test_move_task_updates_status(setup_database):
    db = setup_database
    col_to_do = db.query(models.ColumnModel).filter(models.ColumnModel.title == "To Do").first()
    col_done = db.query(models.ColumnModel).filter(models.ColumnModel.title == "Done").first()
    task = db.query(models.Task).filter(models.Task.column_id == col_to_do.id).first()
    
    response = client.patch(
        f"/tasks/{task.id}/move",
        json={"column_id": col_done.id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["column_id"] == col_done.id
    
    # Verify in DB
    updated_task = db.query(models.Task).filter(models.Task.id == task.id).first()
    assert updated_task.column_id == col_done.id

def test_db_query_tasks_per_column(setup_database):
    db = setup_database
    board = db.query(models.Board).first()
    
    # Using the direct DB repository function as requested
    counts = crud.get_task_counts_per_column(db, board.id)
    
    assert len(counts) == 2
    
    # We started with 2 tasks in 'To Do' and 0 in 'Done'.
    # In the previous test, we moved 1 task from 'To Do' to 'Done'.
    # So we expect 1 in 'To Do' and 1 in 'Done'.
    for count in counts:
        if count.column_title == "To Do":
            assert count.task_count == 1
        elif count.column_title == "Done":
            assert count.task_count == 1
