#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID='a2a-lab-nhonoka'
REGION='us-central1'
SERVICE='echo-a2a-agent'
REPO='a2a-lab'
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE}:latest"

# 1. Create Artifact Registry repo (idempotent)
gcloud artifacts repositories create ${REPO} \
  --repository-format=docker \
  --location=${REGION} \
  --project=${PROJECT_ID} \
  --quiet 2>/dev/null || true

# 2. Authenticate Docker to Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# 3. Build & push the container (linux/amd64 for Cloud Run)
docker build --platform linux/amd64 -t ${IMAGE} ./server
docker push ${IMAGE}

# 4. Deploy to Cloud Run
gcloud run deploy ${SERVICE} \
  --image=${IMAGE} \
  --platform=managed \
  --region=${REGION} \
  --allow-unauthenticated \
  --port=8080 \
  --project=${PROJECT_ID}

# 5. Print service URL
gcloud run services describe ${SERVICE} \
  --platform=managed \
  --region=${REGION} \
  --format='value(status.url)' \
  --project=${PROJECT_ID}