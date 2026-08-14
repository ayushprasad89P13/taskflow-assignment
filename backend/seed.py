import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://taskflow_user:taskflow_password@localhost:5432/taskflow_db")

def seed_db():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Check if database is already seeded
        cur.execute("SELECT count(*) FROM boards;")
        if cur.fetchone()['count'] > 0:
            print("Database already seeded. Skipping.")
            return

        print("Seeding database...")
        
        # Insert default board
        cur.execute("INSERT INTO boards (title) VALUES ('Main Workspace') RETURNING id;")
        board_id = cur.fetchone()['id']
        
        # Insert columns
        columns = ['To Do', 'In Progress', 'Done']
        col_ids = []
        for i, col_title in enumerate(columns):
            cur.execute(
                "INSERT INTO columns (board_id, title, \"order\") VALUES (%s, %s, %s) RETURNING id;",
                (board_id, col_title, i)
            )
            col_ids.append(cur.fetchone()['id'])
            
        # Insert 5 sample tasks
        tasks_data = [
            (col_ids[0], "Design DB schema", "Draft the database schema for boards, columns, and tasks.", "High", 0),
            (col_ids[0], "Setup Docker Compose", "Create docker-compose.yml for postgres and backend.", "Medium", 1),
            (col_ids[1], "Implement API endpoints", "Write FastAPI routes and CRUD operations.", "High", 0),
            (col_ids[1], "Build Frontend UI", "Create React components using Tailwind CSS.", "Medium", 1),
            (col_ids[2], "Project Planning", "Gather requirements and create an implementation plan.", "Low", 0)
        ]
        
        for task in tasks_data:
            cur.execute(
                "INSERT INTO tasks (column_id, title, description, priority, \"order\") VALUES (%s, %s, %s, %s, %s);",
                task
            )
            
        print("Database seeding completed successfully.")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    seed_db()
