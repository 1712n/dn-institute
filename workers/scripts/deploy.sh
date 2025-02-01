#!/bin/bash

# Check if environment is provided
if [ -z "$1" ]; then
  echo "Usage: ./deploy.sh <environment>"
  echo "Environments: development, production"
  exit 1
fi

ENV=$1

# Function to check if command succeeded
check_error() {
  if [ $? -ne 0 ]; then
    echo "Error: $1"
    exit 1
  fi
}

# Validate environment
if [ "$ENV" != "development" ] && [ "$ENV" != "production" ]; then
  echo "Invalid environment. Must be either 'development' or 'production'"
  exit 1
fi

echo "Deploying to $ENV environment..."

# Function to set up secrets
setup_secrets() {
  local worker=$1
  echo "Setting up secrets for $worker..."
  
  # Check if .env.$ENV exists
  if [ ! -f ".env.$ENV" ]; then
    echo "Error: .env.$ENV file not found"
    exit 1
  fi
  
  # Read secrets from .env file and set them
  while IFS='=' read -r key value; do
    if [ ! -z "$key" ] && [ ! -z "$value" ]; then
      echo "Setting secret: $key"
      wrangler secret put "$key" --name "$worker" --env "$ENV" <<< "$value"
      check_error "Failed to set secret $key"
    fi
  done < ".env.$ENV"
}

# Create KV namespaces if they don't exist
echo "Creating KV namespaces..."
wrangler kv:namespace create "article-check-cache" --env $ENV || true
wrangler kv:namespace create "duplication-check-cache" --env $ENV || true
wrangler kv:namespace create "plagiarism-check-cache" --env $ENV || true

# Build the project
echo "Building project..."
npm run build
check_error "Build failed"

# Deploy each worker
echo "Deploying workers..."

WORKERS=(
  "article-check"
  "duplication-check"
  "market-health"
  "payout-calc"
  "plagiarism-check"
)

for worker in "${WORKERS[@]}"; do
  echo "Deploying dni-$worker..."
  setup_secrets "dni-$worker"
  wrangler deploy "src/$worker/index.ts" --env $ENV
  check_error "Failed to deploy dni-$worker"
done

echo "Verifying deployments..."
for worker in "${WORKERS[@]}"; do
  wrangler tail "dni-$worker" --env $ENV --status ok 2>/dev/null || echo "Warning: Could not verify dni-$worker deployment"
done

echo "Deployment complete!" 