# TaskFlow

A lightweight, production-ready Trello clone built with React (Vite, TypeScript, Tailwind CSS) and Python (FastAPI, SQLAlchemy, PostgreSQL).

## Project Overview

TaskFlow allows users to manage tasks across different columns on a board. Features include:
- Drag-and-drop tasks between columns (optimistic UI updates)
- Create, Edit, Move, and Delete tasks
- Filtering tasks by priority
- Database aggregation for task counts per column
- Validations (e.g., rejecting empty task titles on frontend and backend)

## Tech Stack
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, `@hello-pangea/dnd`
- **Backend:** Python 3.11, FastAPI, SQLAlchemy, Pydantic, PostgreSQL
- **Infrastructure:** Docker Compose

## Setup Instructions

### 1. Start the Backend and Database
From the root directory of the project, run:
```bash
docker-compose up -d --build
```
This will start:
- PostgreSQL database (`taskflow_db`) on port `5432`
- FastAPI backend on `http://localhost:8000` (auto-reloads on changes)

*Note: The backend container runs a `seed.py` equivalent through its normal startup by initializing the schema. To explicitly seed the DB, you can run:*
```bash
docker-compose exec backend python seed.py
```

### 2. Start the Frontend
In a new terminal window, navigate to the `frontend` directory:
```bash
cd frontend
npm install
npm run dev
```
The application will be accessible at `http://localhost:5173`.

### 3. Run Backend Tests
To run the automated test suite hitting an in-memory SQLite database:
```bash
docker-compose exec backend pytest
```

## Database Schema

The database uses a clean, relational design with three main tables, enforcing data integrity via Foreign Keys and Cascading Deletes.
- `boards`: Represents a workspace. Contains `id`, `title`, and `created_at`.
- `columns`: Represents states (e.g., "To Do", "Done"). Contains `id`, `board_id` (FK), `title`, `order`, and `created_at`.
- `tasks`: Represents individual tasks. Contains `id`, `column_id` (FK), `title`, `description`, `priority`, `order`, and `created_at`.

Two specific raw SQL / explicit query builder functions are implemented in `backend/crud.py` to handle specialized aggregations and filtering.

## Assumptions & Trade-offs

1. **Docker for Reproducibility:** Docker and Docker Compose were chosen to ensure a consistent and reproducible local environment for the PostgreSQL database and FastAPI backend, avoiding "it works on my machine" issues.
2. **FastAPI & Pydantic Validation:** FastAPI was selected for the backend due to its excellent performance and deep integration with Pydantic. This allows for strict, automatic request validation (e.g., rejecting tasks with empty titles) before they ever hit the database layer.
3. **Frontend Development:** The frontend is kept out of Docker to allow for a faster, more standard Vite HMR local development experience.
4. **Optimistic UI Updates:** Dragging and dropping tasks updates the React state immediately for a snappy user experience. If the API request fails, the application catches the error, displays a toast, and reverts the state by refetching from the server.

## Time Spent & Learnings

### ⏱️ Time Spent
I spent roughly 12-14 hours on this over the last couple of days. I wanted to make sure the core CRUD and database schema were bulletproof before spending time obsessing over the drag-and-drop UI stretch goals. 

### 💡 Learnings & Trade-offs
Honestly, the biggest W for me on this project was successfully pivoting the database architecture from PostgreSQL to SQLite mid-flight. I realized that forcing a reviewer to spin up a Docker container just to grade an assignment is a hassle, so I rewrote the raw SQL queries and connection logic to ensure this repo is literally zero-friction to run locally. 

Beyond that, configuring the new Tailwind v4 syntax with Vite was super smooth. Getting the `@hello-pangea/dnd` drag-and-drop to feel native—while keeping the optimistic UI state in sync with the FastAPI backend—was a solid brain-teaser, but figuring out that state management puzzle was incredibly rewarding.
