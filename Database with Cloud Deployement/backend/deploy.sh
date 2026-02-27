#!/bin/bash
# deploy.sh — Build, push, and deploy backend to Google Cloud Run
# Usage: ./deploy.sh YOUR_PROJECT_ID [REGION]

set -e

PROJECT_ID="${1:?Usage: ./deploy.sh PROJECT_ID [REGION]}"
REGION="${2:-us-central1}"
SERVICE_NAME="crud-api"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Deploying $SERVICE_NAME to Cloud Run..."
echo "   Project : $PROJECT_ID"
echo "   Region  : $REGION"
echo "   Image   : $IMAGE"
echo ""

# 1. Configure Docker for GCR
gcloud auth configure-docker --quiet

# 2. Build & push image
echo "🔨 Building Docker image..."
docker build -t "$IMAGE:latest" .
docker push "$IMAGE:latest"

# 3. Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE:latest" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "PORT=8080" \
  --project "$PROJECT_ID"

# 4. Get the service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --format "value(status.url)")

echo ""
echo "✅ Deployed successfully!"
echo "   URL: $SERVICE_URL"
echo ""
echo "📝 Update frontend/.env.production:"
echo "   VITE_API_URL=$SERVICE_URL"
