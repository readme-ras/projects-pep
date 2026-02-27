"""
Task Manager REST API
─────────────────────
Deployed on Google Cloud Run.
Uses Cloud Firestore for persistence (falls back to in-memory for local dev).
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Task Manager API",
    description="CRUD REST API for tasks — deployed on Google Cloud Run",
    version="1.0.0",
)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas ────────────────────────────────────────────────────────────────────

class Priority(str):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"

class TaskCreate(BaseModel):
    title:       str            = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default="", max_length=1000)
    priority:    str            = Field(default="medium", pattern="^(low|medium|high)$")
    due_date:    Optional[str]  = Field(default=None)
    tags:        list[str]      = Field(default_factory=list)

    model_config = {"json_schema_extra": {"example": {
        "title":       "Deploy to Cloud Run",
        "description": "Set up CI/CD and deploy the API",
        "priority":    "high",
        "due_date":    "2025-03-01",
        "tags":        ["devops", "backend"],
    }}}

class TaskUpdate(BaseModel):
    title:       Optional[str]       = Field(default=None, min_length=1, max_length=200)
    description: Optional[str]       = Field(default=None, max_length=1000)
    priority:    Optional[str]       = Field(default=None, pattern="^(low|medium|high)$")
    completed:   Optional[bool]      = None
    due_date:    Optional[str]       = None
    tags:        Optional[list[str]] = None

class Task(BaseModel):
    id:          str
    title:       str
    description: str
    priority:    str
    completed:   bool
    due_date:    Optional[str]
    tags:        list[str]
    created_at:  str
    updated_at:  str

# ── Storage (Firestore or in-memory) ──────────────────────────────────────────

USE_FIRESTORE = os.getenv("USE_FIRESTORE", "false").lower() == "true"
PROJECT_ID    = os.getenv("GOOGLE_CLOUD_PROJECT", "")

_store: dict = {}   # in-memory fallback

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

# ── Firestore helpers ──────────────────────────────────────────────────────────

def _get_col():
    from google.cloud import firestore
    db = firestore.Client(project=PROJECT_ID)
    return db.collection("tasks")

def _fs_create(data: dict) -> dict:
    col = _get_col()
    col.document(data["id"]).set(data)
    return data

def _fs_get(task_id: str) -> dict | None:
    doc = _get_col().document(task_id).get()
    return doc.to_dict() if doc.exists else None

def _fs_list(completed: bool | None, priority: str | None, tag: str | None) -> list[dict]:
    q = _get_col()
    if completed is not None:
        q = q.where("completed", "==", completed)
    if priority:
        q = q.where("priority", "==", priority)
    docs = q.stream()
    tasks = [d.to_dict() for d in docs]
    if tag:
        tasks = [t for t in tasks if tag in t.get("tags", [])]
    return sorted(tasks, key=lambda t: t["created_at"], reverse=True)

def _fs_update(task_id: str, patch: dict) -> dict | None:
    ref = _get_col().document(task_id)
    if not ref.get().exists:
        return None
    ref.update(patch)
    return ref.get().to_dict()

def _fs_delete(task_id: str) -> bool:
    ref = _get_col().document(task_id)
    if not ref.get().exists:
        return False
    ref.delete()
    return True

# ── In-memory helpers ──────────────────────────────────────────────────────────

def _mem_list(completed: bool | None, priority: str | None, tag: str | None) -> list[dict]:
    tasks = list(_store.values())
    if completed is not None:
        tasks = [t for t in tasks if t["completed"] == completed]
    if priority:
        tasks = [t for t in tasks if t["priority"] == priority]
    if tag:
        tasks = [t for t in tasks if tag in t.get("tags", [])]
    return sorted(tasks, key=lambda t: t["created_at"], reverse=True)

# ── CRUD dispatch ──────────────────────────────────────────────────────────────

def db_create(data: dict) -> dict:
    if USE_FIRESTORE:
        return _fs_create(data)
    _store[data["id"]] = data
    return data

def db_get(task_id: str) -> dict | None:
    if USE_FIRESTORE:
        return _fs_get(task_id)
    return _store.get(task_id)

def db_list(completed=None, priority=None, tag=None) -> list[dict]:
    if USE_FIRESTORE:
        return _fs_list(completed, priority, tag)
    return _mem_list(completed, priority, tag)

def db_update(task_id: str, patch: dict) -> dict | None:
    if USE_FIRESTORE:
        return _fs_update(task_id, patch)
    if task_id not in _store:
        return None
    _store[task_id].update(patch)
    return _store[task_id]

def db_delete(task_id: str) -> bool:
    if USE_FIRESTORE:
        return _fs_delete(task_id)
    if task_id not in _store:
        return False
    del _store[task_id]
    return True

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "storage": "firestore" if USE_FIRESTORE else "memory"}

@app.get("/tasks", response_model=list[Task])
def list_tasks(
    completed: Optional[bool] = Query(default=None),
    priority:  Optional[str]  = Query(default=None),
    tag:       Optional[str]  = Query(default=None),
):
    """List all tasks. Filter by completed, priority, or tag."""
    return db_list(completed=completed, priority=priority, tag=tag)

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    task = db_get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(body: TaskCreate):
    now  = _now()
    task = {
        "id":          str(uuid.uuid4()),
        "title":       body.title,
        "description": body.description or "",
        "priority":    body.priority,
        "completed":   False,
        "due_date":    body.due_date,
        "tags":        body.tags,
        "created_at":  now,
        "updated_at":  now,
    }
    return db_create(task)

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, body: TaskUpdate):
    patch = {k: v for k, v in body.model_dump().items() if v is not None}
    patch["updated_at"] = _now()
    updated = db_update(task_id, patch)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.patch("/tasks/{task_id}/complete", response_model=Task)
def toggle_complete(task_id: str):
    task = db_get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    updated = db_update(task_id, {"completed": not task["completed"], "updated_at": _now()})
    return updated

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str):
    if not db_delete(task_id):
        raise HTTPException(status_code=404, detail="Task not found")

@app.get("/tasks/stats/summary")
def stats():
    all_tasks = db_list()
    total     = len(all_tasks)
    done      = sum(1 for t in all_tasks if t["completed"])
    by_prio   = {"low": 0, "medium": 0, "high": 0}
    for t in all_tasks:
        by_prio[t["priority"]] = by_prio.get(t["priority"], 0) + 1
    return {
        "total":      total,
        "completed":  done,
        "pending":    total - done,
        "by_priority": by_prio,
    }
