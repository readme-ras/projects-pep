"""
Google Sheets service using gspread + google-auth.

Setup:
  1. Create a Google Cloud project and enable the Google Sheets API & Drive API.
  2. Create a Service Account and download the JSON key file.
  3. Share your spreadsheet with the service account email.
  4. Set GOOGLE_CREDENTIALS_FILE (path to key file) and SPREADSHEET_ID in .env.
"""

import os
import json
from typing import Any

import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_client() -> gspread.Client:
    """Return an authenticated gspread client."""
    creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")  # alternative: inline JSON

    if creds_json:
        info = json.loads(creds_json)
        credentials = Credentials.from_service_account_info(info, scopes=SCOPES)
    elif creds_file:
        credentials = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    else:
        raise EnvironmentError(
            "Set GOOGLE_CREDENTIALS_FILE or GOOGLE_CREDENTIALS_JSON in your .env"
        )

    return gspread.authorize(credentials)


def get_spreadsheet(spreadsheet_id: str | None = None) -> gspread.Spreadsheet:
    client = get_client()
    sid = spreadsheet_id or os.getenv("SPREADSHEET_ID")
    if not sid:
        raise EnvironmentError("Set SPREADSHEET_ID in your .env")
    return client.open_by_key(sid)


# ── Worksheet helpers ─────────────────────────────────────────────────────────

def get_worksheet(sheet_name: str, spreadsheet_id: str | None = None) -> gspread.Worksheet:
    return get_spreadsheet(spreadsheet_id).worksheet(sheet_name)


def read_all_rows(sheet_name: str, spreadsheet_id: str | None = None) -> list[dict]:
    """Return all rows as a list of dicts (uses first row as headers)."""
    ws = get_worksheet(sheet_name, spreadsheet_id)
    return ws.get_all_records()


def read_row(sheet_name: str, row_index: int, spreadsheet_id: str | None = None) -> list:
    """Return a single row by 1-based index."""
    ws = get_worksheet(sheet_name, spreadsheet_id)
    return ws.row_values(row_index)


def append_row(sheet_name: str, values: list[Any], spreadsheet_id: str | None = None) -> dict:
    """Append a row to the bottom of the sheet."""
    ws = get_worksheet(sheet_name, spreadsheet_id)
    result = ws.append_row(values, value_input_option="USER_ENTERED")
    return result


def update_row(
    sheet_name: str,
    row_index: int,
    values: list[Any],
    spreadsheet_id: str | None = None,
) -> dict:
    """Overwrite an entire row at a 1-based row index."""
    ws = get_worksheet(sheet_name, spreadsheet_id)
    col_count = len(values)
    range_notation = f"A{row_index}:{_col_letter(col_count)}{row_index}"
    result = ws.update(range_notation, [values], value_input_option="USER_ENTERED")
    return result


def delete_row(sheet_name: str, row_index: int, spreadsheet_id: str | None = None) -> None:
    """Delete a row at a 1-based row index."""
    ws = get_worksheet(sheet_name, spreadsheet_id)
    ws.delete_rows(row_index)


def update_cell(
    sheet_name: str,
    row: int,
    col: int,
    value: Any,
    spreadsheet_id: str | None = None,
) -> None:
    """Update a single cell."""
    ws = get_worksheet(sheet_name, spreadsheet_id)
    ws.update_cell(row, col, value)


def list_sheets(spreadsheet_id: str | None = None) -> list[str]:
    """Return all worksheet titles in a spreadsheet."""
    spreadsheet = get_spreadsheet(spreadsheet_id)
    return [ws.title for ws in spreadsheet.worksheets()]


# ── Utilities ─────────────────────────────────────────────────────────────────

def _col_letter(n: int) -> str:
    """Convert a 1-based column number to a letter (1→A, 26→Z, 27→AA)."""
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result
