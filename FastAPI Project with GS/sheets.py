from fastapi import APIRouter, HTTPException, Query
from app.schemas import AppendRowRequest, UpdateRowRequest, UpdateCellRequest
from app.services import sheets_service

router = APIRouter()


@router.get("/list")
def list_sheets(spreadsheet_id: str | None = Query(default=None)):
    """List all worksheets in the spreadsheet."""
    try:
        return {"sheets": sheets_service.list_sheets(spreadsheet_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sheet_name}/rows")
def get_all_rows(sheet_name: str, spreadsheet_id: str | None = Query(default=None)):
    """Return all rows as a list of dicts (first row = headers)."""
    try:
        return {"rows": sheets_service.read_all_rows(sheet_name, spreadsheet_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sheet_name}/rows/{row_index}")
def get_row(
    sheet_name: str,
    row_index: int,
    spreadsheet_id: str | None = Query(default=None),
):
    """Return a single row by 1-based index."""
    try:
        return {"row": sheets_service.read_row(sheet_name, row_index, spreadsheet_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{sheet_name}/rows")
def append_row(sheet_name: str, body: AppendRowRequest):
    """Append a new row to the sheet."""
    try:
        result = sheets_service.append_row(sheet_name, body.values, body.spreadsheet_id)
        return {"message": "Row appended successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{sheet_name}/rows/{row_index}")
def update_row(sheet_name: str, row_index: int, body: UpdateRowRequest):
    """Overwrite an entire row by 1-based index."""
    try:
        result = sheets_service.update_row(
            sheet_name, row_index, body.values, body.spreadsheet_id
        )
        return {"message": "Row updated successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{sheet_name}/rows/{row_index}")
def delete_row(
    sheet_name: str,
    row_index: int,
    spreadsheet_id: str | None = Query(default=None),
):
    """Delete a row by 1-based index."""
    try:
        sheets_service.delete_row(sheet_name, row_index, spreadsheet_id)
        return {"message": f"Row {row_index} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{sheet_name}/cell")
def update_cell(sheet_name: str, body: UpdateCellRequest):
    """Update a single cell."""
    try:
        sheets_service.update_cell(
            sheet_name, body.row, body.col, body.value, body.spreadsheet_id
        )
        return {"message": f"Cell ({body.row}, {body.col}) updated to '{body.value}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
