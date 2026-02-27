from typing import Any
from pydantic import BaseModel


class AppendRowRequest(BaseModel):
    sheet_name: str
    values: list[Any]
    spreadsheet_id: str | None = None

    model_config = {"json_schema_extra": {"example": {
        "sheet_name": "Sheet1",
        "values": ["Alice", 30, "alice@example.com"],
    }}}


class UpdateRowRequest(BaseModel):
    sheet_name: str
    row_index: int
    values: list[Any]
    spreadsheet_id: str | None = None

    model_config = {"json_schema_extra": {"example": {
        "sheet_name": "Sheet1",
        "row_index": 2,
        "values": ["Alice Updated", 31, "alice_new@example.com"],
    }}}


class UpdateCellRequest(BaseModel):
    sheet_name: str
    row: int
    col: int
    value: Any
    spreadsheet_id: str | None = None
