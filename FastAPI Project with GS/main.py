from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import sheets

app = FastAPI(
    title="FastAPI + Google Sheets",
    description="CRUD operations on Google Sheets via FastAPI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sheets.router, prefix="/sheets", tags=["sheets"])


@app.get("/")
def root():
    return {"message": "FastAPI Google Sheets integration is running!"}
