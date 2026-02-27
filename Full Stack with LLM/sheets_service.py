"""
Google Sheets service — handles authentication and CRUD operations.
"""

import os
import json
from datetime import datetime
from typing import Any

import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

_client: gspread.Client | None = None


def get_client() -> gspread.Client:
    global _client
    if _client is not None:
        return _client

    creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if creds_json:
        info = json.loads(creds_json)
        credentials = Credentials.from_service_account_info(info, scopes=SCOPES)
    elif creds_file:
        credentials = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    else:
        raise EnvironmentError(
            "Set GOOGLE_CREDENTIALS_FILE or GOOGLE_CREDENTIALS_JSON in your .env"
        )

    _client = gspread.authorize(credentials)
    return _client


def get_spreadsheet(spreadsheet_id: str | None = None) -> gspread.Spreadsheet:
    sid = spreadsheet_id or os.getenv("SPREADSHEET_ID")
    if not sid:
        raise EnvironmentError("Set SPREADSHEET_ID in your .env")
    return get_client().open_by_key(sid)


def get_worksheet(sheet_name: str, spreadsheet_id: str | None = None) -> gspread.Worksheet:
    return get_spreadsheet(spreadsheet_id).worksheet(sheet_name)


# ── Chat log helpers ───────────────────────────────────────────────────────────

CHAT_LOG_SHEET = os.getenv("CHAT_LOG_SHEET", "ChatLog")

def ensure_chat_log_headers(spreadsheet_id: str | None = None):
    """Create the ChatLog sheet with headers if it doesn't exist."""
    spreadsheet = get_spreadsheet(spreadsheet_id)
    titles = [ws.title for ws in spreadsheet.worksheets()]

    if CHAT_LOG_SHEET not in titles:
        ws = spreadsheet.add_worksheet(title=CHAT_LOG_SHEET, rows=1000, cols=6)
    else:
        ws = spreadsheet.worksheet(CHAT_LOG_SHEET)

    # Write headers if first row is empty
    existing = ws.row_values(1)
    if not existing:
        ws.append_row(
            ["Timestamp", "Session ID", "Role", "Message", "Model", "Tokens"],
            value_input_option="USER_ENTERED",
        )


def log_message(
    session_id: str,
    role: str,
    message: str,
    model: str = "",
    tokens: int = 0,
    spreadsheet_id: str | None = None,
):
    """Append a single chat message to the ChatLog sheet."""
    ws = get_worksheet(CHAT_LOG_SHEET, spreadsheet_id)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row(
        [timestamp, session_id, role, message, model, tokens],
        value_input_option="USER_ENTERED",
    )


def get_chat_history(session_id: str, spreadsheet_id: str | None = None) -> list[dict]:
    """Fetch all log rows for a specific session."""
    ws = get_worksheet(CHAT_LOG_SHEET, spreadsheet_id)
    rows = ws.get_all_records()
    return [r for r in rows if str(r.get("Session ID")) == session_id]


def get_all_logs(spreadsheet_id: str | None = None) -> list[dict]:
    ws = get_worksheet(CHAT_LOG_SHEET, spreadsheet_id)
    return ws.get_all_records()


# ── Generic sheet CRUD ─────────────────────────────────────────────────────────

def read_all(sheet_name: str, spreadsheet_id: str | None = None) -> list[dict]:
    return get_worksheet(sheet_name, spreadsheet_id).get_all_records()


def append_row(sheet_name: str, values: list[Any], spreadsheet_id: str | None = None):
    return get_worksheet(sheet_name, spreadsheet_id).append_row(
        values, value_input_option="USER_ENTERED"
    )


def update_row(sheet_name: str, row_index: int, values: list[Any], spreadsheet_id: str | None = None):
    ws = get_worksheet(sheet_name, spreadsheet_id)
    end_col = _col_letter(len(values))
    ws.update(f"A{row_index}:{end_col}{row_index}", [values], value_input_option="USER_ENTERED")


def delete_row(sheet_name: str, row_index: int, spreadsheet_id: str | None = None):
    get_worksheet(sheet_name, spreadsheet_id).delete_rows(row_index)


def list_sheets(spreadsheet_id: str | None = None) -> list[str]:
    return [ws.title for ws in get_spreadsheet(spreadsheet_id).worksheets()]


def _col_letter(n: int) -> str:
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result
