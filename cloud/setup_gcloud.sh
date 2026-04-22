#!/usr/bin/env bash
# setup_gcloud.sh
# Run this ONCE to set up Google Cloud resources for the pipeline.
# Usage: bash cloud/setup_gcloud.sh YOUR_PROJECT_ID YOUR_BUCKET_NAME

set -euo pipefail

PROJECT_ID="${1:?Usage: $0 PROJECT_ID BUCKET_NAME}"
BUCKET_NAME="${2:?Usage: $0 PROJECT_ID BUCKET_NAME}"
SA_NAME="ad-automation-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="service-account-key.json"

echo "🔧 Setting project to $PROJECT_ID …"
gcloud config set project "$PROJECT_ID"

echo "📦 Enabling required APIs …"
gcloud services enable storage.googleapis.com \
                        iam.googleapis.com \
                        run.googleapis.com

echo "🪣 Creating GCS bucket gs://$BUCKET_NAME …"
gcloud storage buckets create "gs://$BUCKET_NAME" \
  --location=asia-south1 \
  --uniform-bucket-level-access || echo "Bucket may already exist."

echo "👤 Creating service account $SA_NAME …"
gcloud iam service-accounts create "$SA_NAME" \
  --display-name="Ad Automation Service Account" || echo "SA may already exist."

echo "🔑 Granting Storage Object Admin role …"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.objectAdmin"

echo "📄 Generating JSON key → $KEY_FILE …"
gcloud iam service-accounts keys create "$KEY_FILE" \
  --iam-account="$SA_EMAIL"

echo ""
echo "✅ Done! Now:"
echo "   1. Copy the contents of '$KEY_FILE' into GitHub Secret: GCLOUD_SERVICE_ACCOUNT_KEY"
echo "   2. Add GCS_BUCKET_NAME=$BUCKET_NAME to GitHub Secrets"
echo "   3. DELETE the $KEY_FILE from your machine after adding to GitHub!"
