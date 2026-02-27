import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import hf_service, sheets_service

router = APIRouter()


class GenerateRequest(BaseModel):
    prompt: str
    system_prompt: str | None = None
    session_id: str | None = None
    log_to_sheets: bool = True

    model_config = {"json_schema_extra": {"example": {
        "prompt": "Explain transformers in one paragraph.",
        "system_prompt": "You are a helpful AI assistant.",
        "log_to_sheets": True,
    }}}


class GenerateResponse(BaseModel):
    response: str
    session_id: str
    model: str


@router.post("/generate", response_model=GenerateResponse)
def generate(body: GenerateRequest):
    session_id = body.session_id or str(uuid.uuid4())

    try:
        result = hf_service.generate(body.prompt, body.system_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    model_info = hf_service.get_model_info()

    if body.log_to_sheets:
        try:
            sheets_service.ensure_chat_log_headers()
            sheets_service.log_message(session_id, "user", body.prompt, model_info["model_id"])
            sheets_service.log_message(session_id, "assistant", result, model_info["model_id"])
        except Exception as e:
            # Don't fail the request if logging fails
            print(f"[WARNING] Could not log to sheets: {e}")

    return GenerateResponse(
        response=result,
        session_id=session_id,
        model=model_info["model_id"],
    )


@router.get("/model-info")
def model_info():
    return hf_service.get_model_info()
