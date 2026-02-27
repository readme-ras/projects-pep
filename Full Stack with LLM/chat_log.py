from fastapi import APIRouter, HTTPException, Query
from app.services import sheets_service

router = APIRouter()


@router.get("/")
def get_all_logs(spreadsheet_id: str | None = Query(default=None)):
    """Return all chat log entries from the sheet."""
    try:
        return {"logs": sheets_service.get_all_logs(spreadsheet_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}")
def get_session_logs(session_id: str, spreadsheet_id: str | None = Query(default=None)):
    """Return all messages for a specific session."""
    try:
        return {"session_id": session_id, "messages": sheets_service.get_chat_history(session_id, spreadsheet_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/init")
def init_chat_log(spreadsheet_id: str | None = Query(default=None)):
    """Create the ChatLog sheet with headers if it doesn't exist."""
    try:
        sheets_service.ensure_chat_log_headers(spreadsheet_id)
        return {"message": "ChatLog sheet ready"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
