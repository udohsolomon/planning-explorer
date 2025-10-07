# MCP Server Research & Configuration Guide

**Date**: 2025-10-04
**Purpose**: Research and document available MCP server options for enrichment agent

---

## 🎯 Overview

The enrichment agent requires 3 MCP servers:
1. **Playwright MCP** - Browser automation for JavaScript-rendered pages
2. **Firecrawl MCP** - Fast HTML scraping for static pages
3. **Context7 MCP** - LLM-powered semantic extraction

---

## 1. Playwright MCP Server

### Official Anthropic MCP Servers

**Repository**: `https://github.com/anthropics/mcp-servers`

**Available Playwright Options**:

#### Option A: @modelcontextprotocol/server-playwright
- **Status**: Official Anthropic implementation
- **Installation**:
  ```bash
  npm install -g @modelcontextprotocol/server-playwright
  ```
- **Usage**:
  ```bash
  npx @modelcontextprotocol/server-playwright
  ```
- **Features**:
  - Browser navigation
  - Screenshot capture
  - Element interaction
  - JavaScript execution
  - Wait for selectors

**Configuration**:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-playwright"],
      "env": {}
    }
  }
}
```

#### Option B: Puppeteer MCP (Alternative)
- **Status**: Community-maintained alternative
- **Pros**: More mature, widely used
- **Cons**: Not official MCP, requires custom wrapper

### Integration Approach

**Python Client Integration**:
```python
# app/services/mcp_clients/playwright_client.py
import subprocess
import json

class PlaywrightClient:
    def __init__(self):
        # Start MCP server process
        self.process = subprocess.Popen(
            ["npx", "-y", "@modelcontextprotocol/server-playwright"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    async def fetch(self, url: str) -> str:
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "playwright_navigate",
                "arguments": {
                    "url": url,
                    "wait_for": "networkidle"
                }
            }
        }

        # Send request to MCP server
        self.process.stdin.write(json.dumps(request).encode() + b'\n')
        self.process.stdin.flush()

        # Read response
        response = json.loads(self.process.stdout.readline())
        return response["result"]["content"]
```

**Estimated Cost**: $0 (self-hosted)
**Response Time**: 3-8 seconds
**Complexity**: Medium

---

## 2. Firecrawl MCP Server

### Available Options

#### Option A: Firecrawl API Service
- **Website**: https://firecrawl.dev
- **Status**: Production-ready SaaS
- **Pricing**:
  - Free tier: 500 scrapes/month
  - Starter: $29/month (5,000 scrapes)
  - Pro: $99/month (50,000 scrapes)

**API Integration**:
```python
# app/services/mcp_clients/firecrawl_client.py
import httpx

class FirecrawlClient:
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        self.base_url = "https://api.firecrawl.dev/v0"

    async def fetch(self, url: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/scrape",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"url": url, "formats": ["html"]}
            )
            return response.json()["html"]
```

**Pros**:
- No infrastructure to manage
- Fast and reliable
- API-based (no MCP complexity)

**Cons**:
- Monthly cost
- Rate limits
- External dependency

#### Option B: Self-Hosted Scraper
- **Library**: `playwright` + `beautifulsoup4`
- **Cost**: $0
- **Complexity**: Low (already have dependencies)

**Simple Implementation**:
```python
# app/services/mcp_clients/firecrawl_client.py
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

class FirecrawlClient:
    async def fetch(self, url: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)
            content = await page.content()
            await browser.close()
            return content
```

**Pros**:
- Free
- Full control
- No rate limits

**Cons**:
- Need to manage browser instances
- Slower than dedicated service

#### Option C: MCP Fetch Server
- **Repository**: `@modelcontextprotocol/server-fetch`
- **Status**: Official Anthropic implementation
- **Features**: Basic HTTP fetching

**Recommendation**: Use Option B (Self-hosted with Playwright) - we already have the dependencies and it's free.

**Estimated Cost**: $0-29/month
**Response Time**: 1-3 seconds
**Complexity**: Low

---

## 3. Context7 / LLM Extraction

### Available Options

#### Option A: OpenAI API
- **Models**: GPT-4, GPT-4-mini
- **Pricing**:
  - GPT-4-mini: $0.15/1M input tokens, $0.60/1M output tokens
  - GPT-4: $30/1M input tokens, $60/1M output tokens

**Cost Estimate**:
- Average extraction: ~2,000 input tokens, ~200 output tokens
- GPT-4-mini cost per extraction: $0.0003 + $0.00012 = $0.00042
- 1,000 extractions/month: $0.42
- 10,000 extractions/month: $4.20

**Implementation**:
```python
# app/services/mcp_clients/context7_client.py
from openai import AsyncOpenAI

class Context7Client:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    async def extract(self, content: str, prompt: str) -> Optional[Dict]:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a data extraction specialist."},
                {"role": "user", "content": f"{prompt}\n\n{content}"}
            ],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
```

#### Option B: Anthropic Claude API
- **Models**: Claude 3.5 Sonnet, Claude 3 Haiku
- **Pricing**:
  - Haiku: $0.25/1M input tokens, $1.25/1M output tokens
  - Sonnet: $3/1M input tokens, $15/1M output tokens

**Cost Estimate**:
- Haiku cost per extraction: $0.0005 + $0.00025 = $0.00075
- 1,000 extractions/month: $0.75
- 10,000 extractions/month: $7.50

#### Option C: MCP Claude Server
- **Repository**: `@modelcontextprotocol/server-anthropic`
- **Requires**: Anthropic API key
- **Integration**: Through MCP protocol

**Recommendation**: Use Option A (OpenAI GPT-4-mini) - best price/performance ratio.

**Estimated Cost**: $5-50/month (depends on volume)
**Response Time**: 2-5 seconds
**Complexity**: Low

---

## 📊 Cost Analysis Summary

| Component | Option | Monthly Cost | Setup Time | Complexity |
|-----------|--------|-------------|------------|------------|
| Playwright | Self-hosted MCP | $0 | 30 min | Medium |
| Firecrawl | Self-hosted | $0 | 15 min | Low |
| Context7 | OpenAI GPT-4-mini | $5-50 | 15 min | Low |
| Redis | WSL/Docker | $0 | 10 min | Low |
| **Total** | | **$5-50/month** | **70 min** | |

**Estimated Monthly Cost at Scale**:
- 1,000 enrichments/month: ~$5
- 10,000 enrichments/month: ~$50
- 100,000 enrichments/month: ~$500

---

## 🚀 Recommended Configuration

### Development Environment

**Playwright**: Self-hosted with Playwright library
```bash
pip install playwright
playwright install chromium
```

**Firecrawl**: Direct Playwright usage (no separate server)
```python
# Use playwright directly in firecrawl_client.py
```

**Context7**: OpenAI API with GPT-4-mini
```bash
export OPENAI_API_KEY="sk-..."
```

**Redis**: WSL installation
```bash
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

### Production Environment

**Playwright**: Containerized Playwright
```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy
```

**Firecrawl**: Firecrawl API (if budget allows)
```bash
export FIRECRAWL_API_KEY="fc-..."
```

**Context7**: OpenAI API with rate limiting
```python
# Add rate limiting to prevent cost overruns
```

**Redis**: Docker Redis
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

---

## 📝 Implementation Steps

### Step 1: Install Playwright (15 min)

```bash
cd /mnt/c/Users/Solomon-PC/Documents/Planning\ Explorer/backend
source venv/bin/activate

# Install Playwright
pip install playwright

# Install Chromium browser
playwright install chromium

# Test installation
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright installed')"
```

### Step 2: Configure OpenAI API (5 min)

```bash
# Set environment variable
export OPENAI_API_KEY="your-api-key-here"

# Or add to .env file
echo "OPENAI_API_KEY=your-api-key-here" >> .env

# Install OpenAI library
pip install openai
```

### Step 3: Update Client Wrappers (30 min)

Replace mock implementations with real code (see implementation examples above).

### Step 4: Test with Real URLs (20 min)

```python
# Test script
from app.agents.enrichment.applicant_agent import enrich_applicant_data
import asyncio

async def test_real_extraction():
    result = await enrich_applicant_data(
        url="https://publicaccess.dover.gov.uk/online-applications/applicationDetails.do?activeTab=summary&keyVal=S4S7QCFZH0F00",
        application_id="REAL-TEST-001"
    )
    print(f"Success: {result['success']}")
    print(f"Applicant: {result['data']['applicant_name']}")
    print(f"Agent: {result['data']['agent_name']}")

asyncio.run(test_real_extraction())
```

---

## 🔒 Security Considerations

### API Key Management
- ✅ Use environment variables, never commit keys
- ✅ Rotate keys regularly
- ✅ Use separate keys for dev/staging/production
- ✅ Implement rate limiting to prevent abuse

### Browser Security
- ✅ Run Playwright in sandboxed container
- ✅ Disable unnecessary browser features
- ✅ Set timeout limits
- ✅ Validate URLs before navigation

### Data Privacy
- ✅ Don't log sensitive extracted data
- ✅ Clear browser cache after each session
- ✅ Use HTTPS for all API calls
- ✅ Comply with GDPR/data protection laws

---

## 📈 Performance Optimization

### Caching Strategy
1. **Redis Cache** (24h TTL)
   - Reduces API calls by 70-80%
   - Saves costs on LLM usage
   - Improves response times

2. **Result Validation**
   - Cache successful extractions longer
   - Retry failed extractions sooner
   - Invalidate on portal structure changes

### Cost Optimization
1. **Use GPT-4-mini** instead of GPT-4 (90% cost savings)
2. **Implement caching** (70% API call reduction)
3. **Batch requests** where possible
4. **Monitor usage** and set budget alerts
5. **Optimize prompts** to reduce token usage

### Speed Optimization
1. **Parallel processing** for multiple applications
2. **Connection pooling** for HTTP requests
3. **Browser instance reuse** (Playwright)
4. **Async/await** throughout (already implemented)

---

## 🎯 Next Actions

1. ✅ Research complete - documented all options
2. ⏳ Install Playwright
3. ⏳ Install Redis (WSL)
4. ⏳ Get OpenAI API key
5. ⏳ Update client wrappers
6. ⏳ Test with real URLs
7. ⏳ Monitor costs and performance

---

**Status**: Research Complete ✅
**Recommended Stack**: Playwright (self-hosted) + OpenAI GPT-4-mini + Redis (WSL/Docker)
**Estimated Cost**: $5-50/month
**Setup Time**: 70 minutes
