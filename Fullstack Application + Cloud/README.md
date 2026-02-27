# ⬡ NEXUS UMS — University Management System

A full-stack, production-ready University Management System with Node.js/Express backend, React frontend, and complete cloud deployment infrastructure.

---

## 🏗️ Architecture Overview

```
nexus-ums/
├── backend/                    # Node.js + Express + MongoDB API
│   ├── src/
│   │   ├── server.js           # Entry point
│   │   ├── controllers/        # Business logic
│   │   ├── models/             # Mongoose schemas
│   │   ├── routes/             # API routes
│   │   ├── middleware/         # Auth, validation
│   │   └── config/             # DB config, seed data
│   ├── Dockerfile
│   └── package.json
├── frontend/                   # React SPA
│   ├── src/
│   │   ├── App.js              # Main app + routing
│   │   ├── App.css             # Design system
│   │   └── services/api.js     # Axios API client
│   ├── Dockerfile
│   └── package.json
├── deploy/
│   ├── docker/
│   │   └── nginx.conf          # Reverse proxy config
│   └── k8s/
│       └── deployment.yaml     # Kubernetes manifests
├── .github/workflows/
│   └── ci-cd.yml               # GitHub Actions pipeline
└── docker-compose.yml          # Full stack orchestration
```

---

## ✨ Features

### Backend API
| Module | Endpoints | Description |
|--------|-----------|-------------|
| Auth | POST /login, /register, GET /me | JWT authentication |
| Students | CRUD /students | Student management |
| Faculty | CRUD /faculty | Faculty management |
| Courses | CRUD /courses | Course catalog |
| Departments | CRUD /departments | Department management |
| Enrollments | CRUD /enrollments | Course enrollment |
| Grades | CRUD /grades | Grade management with auto-calculation |
| Attendance | CRUD /attendance, GET /stats | Attendance tracking |
| Fees | CRUD /fees, PUT /:id/pay | Fee management |
| Notices | CRUD /notices | Announcements |
| Dashboard | GET /stats | Analytics & overview |

### Frontend
- 🔐 JWT-based authentication with role-based access
- 📊 Analytics dashboard with charts and statistics
- 👥 Students, Faculty, Courses, Department management
- 📱 Responsive dark theme design
- ⚡ Real-time data with pagination and search

---

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- MongoDB 7.0+
- Docker (for containerized deployment)

### 1. Local Development

```bash
# Clone the repo
git clone https://github.com/yourorg/nexus-ums.git
cd nexus-ums

# Backend setup
cd backend
cp .env.example .env          # Edit with your config
npm install
npm run seed                  # Seed demo data
npm run dev                   # Runs on http://localhost:5000

# Frontend setup (new terminal)
cd frontend
npm install
npm start                     # Runs on http://localhost:3000
```

**Demo credentials** (after seeding):
- Admin: `admin@university.edu` / `Admin@123`
- Faculty: `priya@university.edu` / `Faculty@123`
- Student: `arjun.singh@student.edu` / `Student@123`

---

## 🐳 Docker Deployment

### Start everything with Docker Compose
```bash
# Copy and configure env
cp .env.example .env

# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Seed the database
docker-compose exec backend node src/config/seed.js

# Stop
docker-compose down
```

**Services started:**
| Service | Port | Description |
|---------|------|-------------|
| nginx | 80, 443 | Reverse proxy |
| frontend | 3000 | React app |
| backend | 5000 | REST API |
| mongodb | 27017 | Database |
| redis | 6379 | Cache |

---

## ☁️ Cloud Deployment

### Option 1: AWS (ECS + DocumentDB)

```bash
# 1. Build and push to ECR
aws ecr create-repository --repository-name ums-backend
docker build -t ums-backend ./backend
docker tag ums-backend:latest <AWS_ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/ums-backend:latest
docker push <AWS_ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/ums-backend:latest

# 2. Deploy using AWS ECS (Fargate)
# Create task definition pointing to ECR image
# Create ECS service in your VPC

# 3. Set environment variables in ECS task definition:
# - MONGODB_URI → DocumentDB connection string
# - JWT_SECRET → Strong random secret
# - NODE_ENV → production
```

### Option 2: GCP (Cloud Run)

```bash
# Build and push to Artifact Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/ums-backend ./backend
gcloud builds submit --tag gcr.io/PROJECT_ID/ums-frontend ./frontend

# Deploy to Cloud Run
gcloud run deploy ums-backend \
  --image gcr.io/PROJECT_ID/ums-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MONGODB_URI=<ATLAS_URI>,JWT_SECRET=<SECRET>

gcloud run deploy ums-frontend \
  --image gcr.io/PROJECT_ID/ums-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 3: Kubernetes (GKE/EKS/AKS)

```bash
# 1. Build and push images to your registry
docker build -t your-registry/ums-backend:latest ./backend
docker build -t your-registry/ums-frontend:latest ./frontend
docker push your-registry/ums-backend:latest
docker push your-registry/ums-frontend:latest

# 2. Update image references in deploy/k8s/deployment.yaml

# 3. Create secrets (IMPORTANT: never commit real secrets)
kubectl create secret generic ums-secret \
  --from-literal=JWT_SECRET=<your-jwt-secret> \
  --from-literal=MONGODB_URI=<your-mongodb-uri> \
  -n ums

kubectl create secret generic mongodb-secret \
  --from-literal=username=admin \
  --from-literal=password=<your-mongo-password> \
  -n ums

# 4. Apply manifests
kubectl apply -f deploy/k8s/deployment.yaml

# 5. Check deployment status
kubectl get pods -n ums
kubectl get services -n ums
kubectl get ingress -n ums
```

### Option 4: DigitalOcean App Platform (Easiest)

1. Push code to GitHub
2. Go to DigitalOcean App Platform → Create App
3. Connect your GitHub repo
4. Add a MongoDB database component
5. Set environment variables
6. Deploy — App Platform handles everything automatically!

---

## 🔒 Security Features

- **JWT Authentication** with expiring tokens
- **bcrypt** password hashing (12 rounds)
- **Role-based access control** (admin/faculty/student)
- **Rate limiting** (100 req/15min per IP)
- **Helmet.js** security headers
- **CORS** configuration
- **Input validation** with express-validator
- **Non-root Docker user**
- **Health check endpoints**

---

## 📊 API Reference

### Authentication
```http
POST /api/auth/login
Content-Type: application/json

{ "email": "admin@university.edu", "password": "Admin@123" }
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": { "id": "...", "name": "Admin User", "role": "admin" }
}
```

### Authenticated Requests
```http
GET /api/students?page=1&limit=10&search=arjun
Authorization: Bearer <token>
```

---

## 🧪 Running Tests

```bash
cd backend
npm test
npm test -- --coverage
```

---

## 🔄 CI/CD Pipeline

The GitHub Actions pipeline (`.github/workflows/ci-cd.yml`) automatically:
1. Runs tests on every push/PR
2. Builds Docker images on `main` branch
3. Pushes to GitHub Container Registry (GHCR)
4. Deploys to Kubernetes cluster

**Required GitHub Secrets:**
```
JWT_SECRET              # Strong JWT secret
REACT_APP_API_URL       # Backend URL
KUBE_CONFIG             # Base64-encoded kubeconfig
```

---

## 📈 Scaling

The system is designed for horizontal scaling:
- **Stateless API** — any number of backend pods
- **HPA** auto-scales backend 2→10 pods based on CPU
- **Redis** for session/cache (add to backend if needed)
- **MongoDB** Atlas / DocumentDB for managed database scaling
- **CDN** for frontend static assets (CloudFront/Cloud CDN)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Node.js, Express.js |
| Database | MongoDB + Mongoose |
| Authentication | JWT + bcryptjs |
| Frontend | React 18, React Router v6 |
| Containerization | Docker, Docker Compose |
| Orchestration | Kubernetes |
| Reverse Proxy | Nginx |
| Cache | Redis |
| CI/CD | GitHub Actions |
| Cloud | AWS ECS / GCP Cloud Run / K8s |

---

## 📄 License

MIT © University Management System
