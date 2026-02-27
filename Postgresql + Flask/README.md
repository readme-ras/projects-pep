# FastAPI + PostgreSQL + Flask

Simple full-stack CRUD app.

- **FastAPI** — REST API + PostgreSQL via SQLAlchemy
- **Flask** — frontend that calls the FastAPI backend

## Structure

```
├── fastapi_app/
│   ├── main.py       # Routes
│   ├── database.py   # SQLAlchemy setup
│   ├── models.py     # DB model
│   ├── schemas.py    # Pydantic schemas
│   └── crud.py       # DB operations
├── flask_app/
│   ├── app.py        # Flask routes
│   └── templates/    # HTML templates
├── requirements.txt
└── .env.example
```

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit DATABASE_URL with your PostgreSQL credentials

# 3. Create the database
createdb appdb   # or use psql / pgAdmin

# 4. Start FastAPI (terminal 1)
uvicorn fastapi_app.main:app --reload --port 8000

# 5. Start Flask (terminal 2)
python flask_app/app.py
```

- Flask UI → http://localhost:5000
- FastAPI docs → http://localhost:8000/docs

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET    | /items | List all items |
| GET    | /items/{id} | Get one item |
| POST   | /items | Create item |
| PUT    | /items/{id} | Update item |
| DELETE | /items/{id} | Delete item |
