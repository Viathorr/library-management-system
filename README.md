# Library Management System

This is a **full-stack Library Management System** with:

* **Backend**: FastAPI + SQLAlchemy + PostgreSQL, managed with Conda
* **Frontend**: React.js
* **Database**: PostgreSQL
* **Containerization**: Docker & Docker Compose

This setup allows you to run both backend and frontend with a single command.

---

## Prerequisites

* Docker ≥ 20.x
* Docker Compose ≥ 2.x
* (Optional) Miniconda / Anaconda if you want to run backend locally without Docker

---

## Backend Setup (FastAPI + PostgreSQL)

### Environment Variables

Create or update `backend/.env` with your database credentials:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_pwd
POSTGRES_DB=lib_management_system
DATABASE_URL=postgresql://postgres:postgres_pwd@database:5432/lib_management_system
```

> **Important:** Inside Docker, the database hostname must be `database` (the service name in Docker Compose).

---

## Docker Compose Setup

Docker Compose manages backend, frontend, and database:

* Backend: `http://localhost:8000`
* Frontend: `http://localhost:3000`
* PostgreSQL: `localhost:5435` on host machine

---

## Running the System

From the root folder:

```bash
docker-compose up --build
```

* Backend: [http://localhost:8000](http://localhost:8000)

  * Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
* Frontend: [http://localhost:3000](http://localhost:3000)

Stop everything:

```bash
docker-compose down
```

---

## Database Initialization

* `backend/db/init.sql` contains schema creation and sample books.

---
