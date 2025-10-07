#!/bin/bash
# Copy API keys from root .env to backend .env

ROOT_ENV="../.env"
BACKEND_ENV=".env"

# Extract keys from root .env
CONTEXT7_KEY=$(grep "CONTEXT7_API_KEY=" "$ROOT_ENV" | cut -d '=' -f2)
FIRECRAWL_KEY=$(grep "FIRECRAWL_API_KEY=" "$ROOT_ENV" | cut -d '=' -f2)
ANTHROPIC_URL=$(grep "ANTHROPIC_BASE_URL=" "$ROOT_ENV" | cut -d '=' -f2)
ANTHROPIC_TOKEN=$(grep "ANTHROPIC_AUTH_TOKEN=" "$ROOT_ENV" | cut -d '=' -f2)

# Add to backend .env if not already present
echo "" >> "$BACKEND_ENV"
echo "# pSEO API Keys" >> "$BACKEND_ENV"
echo "CONTEXT7_API_KEY=$CONTEXT7_KEY" >> "$BACKEND_ENV"
echo "FIRECRAWL_API_KEY=$FIRECRAWL_KEY" >> "$BACKEND_ENV"
echo "" >> "$BACKEND_ENV"
echo "# Anthropic via z.ai proxy" >> "$BACKEND_ENV"
echo "ANTHROPIC_BASE_URL=$ANTHROPIC_URL" >> "$BACKEND_ENV"
echo "ANTHROPIC_AUTH_TOKEN=$ANTHROPIC_TOKEN" >> "$BACKEND_ENV"
echo "" >> "$BACKEND_ENV"
echo "# pSEO Configuration" >> "$BACKEND_ENV"
echo "PSEO_MAX_CONCURRENT=3" >> "$BACKEND_ENV"
echo "PSEO_BATCH_SIZE=10" >> "$BACKEND_ENV"
echo "PSEO_OUTPUT_DIR=./outputs/pseo" >> "$BACKEND_ENV"
echo "PSEO_MIN_WORD_COUNT=2500" >> "$BACKEND_ENV"
echo "PSEO_MAX_WORD_COUNT=3500" >> "$BACKEND_ENV"

echo "✅ API keys copied to backend/.env"
