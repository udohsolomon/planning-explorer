# Enrichment Agent - Manual Deployment Steps

**Date**: 2025-10-04
**Status**: Step-by-step deployment guide

---

## 🚀 Quick Deployment (70 minutes)

### Step 1: Install Redis (10 min)

**Open WSL terminal and run**:
```bash
sudo apt update
sudo apt install redis-server

# Start Redis
sudo service redis-server start

# Verify Redis is running
redis-cli ping
# Should return: PONG

# Check Redis status
sudo service redis-server status
```

**Alternative (Docker)**:
```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine

# Verify
docker ps | grep redis
redis-cli ping
```

---

### Step 2: Install Playwright & Dependencies (15 min)

```bash
cd /mnt/c/Users/Solomon-PC/Documents/Planning\ Explorer/backend
source venv/bin/activate

# Install Python packages
pip install playwright openai

# Install Chromium browser
playwright install chromium

# Verify installation
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright ready')"
python -c "import openai; print('✅ OpenAI library ready')"
```

---

### Step 3: Get OpenAI API Key (5 min)

1. Visit: https://platform.openai.com/api-keys
2. Create new secret key
3. Copy the key (starts with `sk-...`)
4. Set environment variable:

```bash
# Option A: Export for current session
export OPENAI_API_KEY="sk-your-key-here"

# Option B: Add to .env file (recommended)
cd /mnt/c/Users/Solomon-PC/Documents/Planning\ Explorer/backend
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# Update requirements.txt
echo "python-dotenv>=1.0.0" >> requirements.txt
pip install python-dotenv
```

**Update settings.py**:
```python
# app/core/config.py
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    # ... existing settings ...
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
```

---

### Step 4: Update MCP Client Wrappers (30 min)

The client wrappers need to be updated with real implementations. I'll provide the updated code below.

---

### Step 5: Test Everything (20 min)

```bash
cd /mnt/c/Users/Solomon-PC/Documents/Planning\ Explorer/backend
source venv/bin/activate

# Test Redis connection
python -c "
import redis
r = redis.from_url('redis://localhost:6379/0')
r.ping()
print('✅ Redis connected')
"

# Test Playwright
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    print('✅ Playwright working')
    browser.close()
"

# Test OpenAI
python -c "
from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('✅ OpenAI configured')
"

# Test full enrichment with real URL
python -c "
from app.agents.enrichment.applicant_agent import enrich_applicant_data
import asyncio

async def test():
    result = await enrich_applicant_data(
        url='https://publicaccess.dover.gov.uk/online-applications/applicationDetails.do?activeTab=summary&keyVal=S4S7QCFZH0F00',
        application_id='DEPLOYMENT-TEST-001'
    )
    print(f'✅ Enrichment Success: {result[\"success\"]}')
    print(f'   Applicant: {result[\"data\"][\"applicant_name\"]}')
    print(f'   Agent: {result[\"data\"][\"agent_name\"]}')
    print(f'   Time: {result[\"metadata\"][\"processing_time_ms\"]}ms')

asyncio.run(test())
"
```

---

## 📝 Checklist

- [ ] Redis installed and running
- [ ] Playwright installed (with Chromium browser)
- [ ] OpenAI library installed
- [ ] OpenAI API key set in environment
- [ ] MCP client wrappers updated (see below)
- [ ] Dependencies in requirements.txt updated
- [ ] Full integration test passed

---

## 🔧 Configuration Files to Update

### 1. requirements.txt
```txt
# Add these lines:
playwright>=1.40.0
openai>=1.0.0
python-dotenv>=1.0.0
redis>=5.0.0  # Already added
```

### 2. .env file (create if doesn't exist)
```bash
# .env
OPENAI_API_KEY=sk-your-key-here
REDIS_URL=redis://localhost:6379/0
```

### 3. app/core/config.py
```python
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # ... existing settings ...
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

settings = Settings()
```

---

## 🎯 After Deployment

### Monitor Costs
```python
# Check OpenAI usage:
# Visit: https://platform.openai.com/usage

# Expected costs:
# - Per enrichment: ~$0.0005
# - 1,000 enrichments: ~$0.50
# - 10,000 enrichments: ~$5.00
```

### Monitor Performance
```bash
# Check Redis cache hit rate
redis-cli INFO stats | grep keyspace_hits

# Check Redis memory usage
redis-cli INFO memory | grep used_memory_human
```

### Test with More URLs
```bash
# Dover (Idox)
https://publicaccess.dover.gov.uk/online-applications/applicationDetails.do?activeTab=summary&keyVal=S4S7QCFZH0F00

# Liverpool (Custom)
https://lar.liverpool.gov.uk/planning/index.html?fa=getApplication&id=175224

# Southampton (Idox)
https://publicaccess.southampton.gov.uk/online-applications/applicationDetails.do?activeTab=summary&keyVal=...
```

---

**Estimated Total Time**: 70 minutes
**Estimated Monthly Cost**: $5-20
**Status**: Ready to proceed with automated update of client wrappers
