# FastAPI + Google Sheets Integration

Full CRUD REST API for Google Sheets using FastAPI, gspread, and google-auth.

## Project Structure

```
fastapi-gsheets/
├── app/
│   ├── main.py                  # FastAPI app & middleware
│   ├── schemas.py               # Pydantic request models
│   ├── routers/
│   │   └── sheets.py            # All /sheets endpoints
│   └── services/
│       └── sheets_service.py    # Google Sheets business logic
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### 1. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Enable **Google Sheets API** and **Google Drive API**
4. Go to **IAM & Admin → Service Accounts** → Create a service account
5. Create a JSON key for the service account and download it as `credentials.json`
6. **Share your Google Sheet** with the service account email (e.g. `myapp@project.iam.gserviceaccount.com`) — give it Editor access

### 2. Local Setup

```bash
# Clone / copy the project
cd fastapi-gsheets

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your GOOGLE_CREDENTIALS_FILE path and SPREADSHEET_ID
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs for the interactive Swagger UI.

## API Endpoints

| Method   | Endpoint                                   | Description                  |
|----------|--------------------------------------------|------------------------------|
| GET      | `/sheets/list`                             | List all worksheets          |
| GET      | `/sheets/{sheet_name}/rows`                | Get all rows (as dicts)      |
| GET      | `/sheets/{sheet_name}/rows/{row_index}`    | Get a single row             |
| POST     | `/sheets/{sheet_name}/rows`                | Append a new row             |
| PUT      | `/sheets/{sheet_name}/rows/{row_index}`    | Overwrite a row              |
| DELETE   | `/sheets/{sheet_name}/rows/{row_index}`    | Delete a row                 |
| PATCH    | `/sheets/{sheet_name}/cell`                | Update a single cell         |

> **Note:** Row indices are **1-based**. Row 1 is typically your header row.

## Example Requests

### Append a row
```bash
curl -X POST http://localhost:8000/sheets/Sheet1/rows \
  -H "Content-Type: application/json" \
  -d '{"sheet_name": "Sheet1", "values": ["Alice", 30, "alice@example.com"]}'
```

### Get all rows
```bash
curl http://localhost:8000/sheets/Sheet1/rows
```

### Update a cell
```bash
curl -X PATCH http://localhost:8000/sheets/Sheet1/cell \
  -H "Content-Type: application/json" \
  -d '{"sheet_name": "Sheet1", "row": 2, "col": 1, "value": "Bob"}'
```

## Passing a Different Spreadsheet ID

All GET endpoints accept an optional `?spreadsheet_id=` query parameter to target a spreadsheet other than the default one in `.env`.

## Deployment Tips

- For cloud deployments (Railway, Render, Fly.io, etc.) set `GOOGLE_CREDENTIALS_JSON` to the entire JSON key contents as an environment variable instead of using a file.
- Add authentication (API keys, OAuth) before exposing this publicly.
