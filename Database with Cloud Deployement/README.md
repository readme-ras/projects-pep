# TaskFlow — FastAPI + React on Google Cloud Run

Full-stack CRUD app deployed on Google Cloud:
- **Backend**: FastAPI on **Google Cloud Run** (serverless, auto-scales to zero)
- **Database**: **Cloud Firestore** (NoSQL, serverless)
- **Frontend**: React (Vite) on **Firebase Hosting**
- **CI/CD**: GitHub Actions

## Structure
```
cloudrun-crud/
├── backend/
│   ├── main.py          # FastAPI CRUD + stats endpoints
│   ├── Dockerfile       # Cloud Run container
│   ├── cloudrun.yaml    # Service definition
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx      # React task manager UI
│   │   ├── api.js       # API client
│   │   └── index.css
│   ├── firebase.json    # Firebase Hosting config
│   └── .env.example
└── .github/workflows/
    ├── deploy-backend.yml
    └── deploy-frontend.yml
```

## Local Dev
```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn main:app --reload --port 8080
# Docs → http://localhost:8080/docs

# Frontend
cd frontend && npm install
echo "VITE_API_URL=http://localhost:8080" > .env
npm run dev
# UI → http://localhost:5173
```

## Deploy to Google Cloud

### 1. Enable APIs
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com firestore.googleapis.com cloudbuild.googleapis.com
gcloud firestore databases create --region=us-central1
```

### 2. Deploy Backend (Cloud Run)
```bash
cd backend
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/taskmanager-api
gcloud run deploy taskmanager-api \
  --image gcr.io/YOUR_PROJECT_ID/taskmanager-api \
  --region us-central1 --allow-unauthenticated \
  --set-env-vars USE_FIRESTORE=true,GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID \
  --memory 512Mi --min-instances 0 --max-instances 10
```

### 3. Deploy Frontend (Firebase Hosting)
```bash
npm install -g firebase-tools && firebase login
cd frontend
echo "VITE_API_URL=https://YOUR-CLOUD-RUN-URL.run.app" > .env
npm install && npm run build
firebase init hosting   # public dir = dist
firebase deploy --only hosting
```

## GitHub Actions CI/CD Secrets
| Secret | Description |
|--------|-------------|
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_SA_KEY` | Service account JSON (base64) |
| `FIREBASE_SERVICE_ACCOUNT` | Firebase SA JSON |
| `VITE_API_URL` | Cloud Run URL |
| `ALLOWED_ORIGINS` | Firebase Hosting URL |

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/tasks` | List tasks (`?completed=`, `?priority=`, `?tag=`) |
| POST | `/tasks` | Create task |
| PUT | `/tasks/{id}` | Update task |
| PATCH | `/tasks/{id}/complete` | Toggle complete |
| DELETE | `/tasks/{id}` | Delete task |
| GET | `/tasks/stats/summary` | Stats |
| GET | `/health` | Health check |

## Cost (hobby scale)
Cloud Run + Firestore + Firebase Hosting = **~$0/month** on free tiers.
