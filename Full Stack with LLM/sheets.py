from typing import Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services import sheets_service

router = APIRouter()


class AppendRequest(BaseModel):
    sheet_name: str
    values: list[Any]
    spreadsheet_id: str | None = None


class UpdateRequest(BaseModel):
    sheet_name: str
    row_index: int
    values: list[Any]
    spreadsheet_id: str | None = None


@router.get("/list")
def list_sheets(spreadsheet_id: str | None = Query(default=None)):
    try:
        return {"sheets": sheets_service.list_sheets(spreadsheet_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sheet_name}/rows")
def get_rows(sheet_name: str, spreadsheet_id: str | None = Query(default=None)):
    try:
        return {"rows": sheets_service.read_all(sheet_name, spreadsheet_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rows")
def append_row(body: AppendRequest):
    try:
        sheets_service.append_row(body.sheet_name, body.values, body.spreadsheet_id)
        return {"message": "Row appended"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rows/{row_index}")
def update_row(row_index: int, body: UpdateRequest):
    try:
        sheets_service.update_row(body.sheet_name, row_index, body.values, body.spreadsheet_id)
        return {"message": f"Row {row_index} updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{sheet_name}/rows/{row_index}")
def delete_row(
    sheet_name: str,
    row_index: int,
    spreadsheet_id: str | None = Query(default=None),
):
    try:
        sheets_service.delete_row(sheet_name, row_index, spreadsheet_id)
        return {"message": f"Row {row_index} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
