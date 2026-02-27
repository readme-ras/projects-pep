from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.routers import llm, sheets, chat_log

app = FastAPI(
    title="HF LLM + Google Sheets",
    description="Full-stack: Hugging Face LLM with Google Sheets logging",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llm.router,      prefix="/api/llm",      tags=["LLM"])
app.include_router(sheets.router,   prefix="/api/sheets",   tags=["Sheets"])
app.include_router(chat_log.router, prefix="/api/chat-log", tags=["Chat Log"])

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))


@app.get("/health")
def health():
    return {"status": "ok"}
