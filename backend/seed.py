"""
seed.py — Populates the SQLite database with initial sample data using SQLAlchemy ORM.
Run: python seed.py
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal, Base
from models import Board, ColumnModel, Task

def seed_db():
    """Create tables and insert 1 board, 3 columns, and 5 sample tasks."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(Board).count() > 0:
            print("Database already seeded. Skipping.")
            return

        print("Seeding database...")

        board = Board(title="Main Workspace")
        db.add(board)
        db.commit()
        db.refresh(board)

        columns_data = ["To Do", "In Progress", "Done"]
        cols = []
        for i, title in enumerate(columns_data):
            col = ColumnModel(board_id=board.id, title=title, order=i)
            db.add(col)
            cols.append(col)
        db.commit()
        for col in cols:
            db.refresh(col)

        tasks_data = [
            (cols[0].id, "Design DB schema",
             "Draft the database schema for boards, columns, and tasks.", "High", 0),
            (cols[0].id, "Setup Docker Compose",
             "Create docker-compose.yml for postgres and backend.", "Medium", 1),
            (cols[1].id, "Implement API endpoints",
             "Write FastAPI routes and CRUD operations.", "High", 0),
            (cols[1].id, "Build Frontend UI",
             "Create React components using Tailwind CSS.", "Medium", 1),
            (cols[2].id, "Project Planning",
             "Gather requirements and create an implementation plan.", "Low", 0),
        ]

        for col_id, title, desc, priority, order in tasks_data:
            task = Task(
                column_id=col_id,
                title=title,
                description=desc,
                priority=priority,
                order=order,
            )
            db.add(task)

        db.commit()
        print("Database seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
