# pSEO Agent - Complete Tools & Services Stack

## Overview
Comprehensive specification of all tools, APIs, services, and configurations needed for the Planning Explorer pSEO implementation.

---

## 1. AI & Content Generation

### **Anthropic Claude API** ⭐ PRIMARY
**Purpose:** AI content generation for all pSEO sections

**Configuration:**
```python
# .env
ANTHROPIC_API_KEY=sk-ant-api03-xxx

# backend/app/config.py
ANTHROPIC_CONFIG = {
    "api_key": os.environ["ANTHROPIC_API_KEY"],
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 4000,
    "temperature": 0.7
}
```

**Usage:**
```python
import anthropic

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=2000,
    temperature=0.7,
    messages=[{"role": "user", "content": prompt}]
)
```

**Cost:**
- Input: $3 per million tokens
- Output: $15 per million tokens
- **Estimated per page:** $0.15-0.25
- **Total for 425 pages:** ~$85

**Rate Limits:**
- Tier 1: 50 requests/min, 40K tokens/min
- Tier 2: 1000 requests/min, 80K tokens/min
- **Strategy:** Use semaphore to limit to 3 concurrent requests

---

## 2. Web Scraping & Content Extraction

### **Playwright MCP Server** ⭐ PRIMARY FOR JS-HEAVY SITES
**Purpose:** Scrape dynamic authority websites (planning portals, committee pages)

**Installation:**
```bash
# Install Playwright
pip install playwright
playwright install chromium

# MCP Server (if using)
npm install -g @playwright/mcp-server
```

**Configuration:**
```python
# backend/app/services/pseo/playwright_scraper.py

from playwright.async_api import async_playwright

class PlaywrightScraper:
    def __init__(self):
        self.browser_config = {
            "headless": True,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage"
            ]
        }

    async def scrape_page(self, url: str, selectors: dict):
        async with async_playwright() as p:
            browser = await p.chromium.launch(**self.browser_config)
            page = await browser.new_page()

            await page.goto(url, wait_until='networkidle', timeout=30000)

            results = {}
            for key, selector in selectors.items():
                elements = await page.query_selector_all(selector)
                results[key] = [await el.inner_text() for el in elements]

            await browser.close()
            return results
```

**Use Cases:**
- Planning committee pages with JavaScript
- Interactive authority portals
- Dynamic news feeds
- Committee meeting calendars

**Cost:** FREE (self-hosted)

---

### **Firecrawl API** ⭐ PRIMARY FOR BATCH SCRAPING
**Purpose:** Large-scale web scraping, content extraction, and crawling

**Setup:**
```bash
pip install firecrawl-py
```

**Configuration:**
```python
# .env
FIRECRAWL_API_KEY=fc-xxx

# backend/app/services/pseo/firecrawl_scraper.py

from firecrawl import FirecrawlApp

class FirecrawlScraper:
    def __init__(self):
        self.app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])

    async def scrape_authority_website(self, base_url: str):
        """Scrape multiple pages from authority website"""

        # Crawl multiple pages
        crawl_result = self.app.crawl_url(
            base_url,
            params={
                'crawlerOptions': {
                    'includes': [
                        '/planning/*',
                        '/news/*',
                        '/local-plan/*',
                        '/policy/*'
                    ],
                    'excludes': [
                        '/admin/*',
                        '/login/*'
                    ],
                    'maxDepth': 3,
                    'limit': 50
                },
                'pageOptions': {
                    'onlyMainContent': True,
                    'includeHtml': False,
                    'screenshot': False
                }
            }
        )

        return crawl_result

    async def scrape_single_page(self, url: str):
        """Scrape a single page with markdown conversion"""

        result = self.app.scrape_url(
            url,
            params={
                'formats': ['markdown', 'html'],
                'onlyMainContent': True,
                'waitFor': 2000
            }
        )

        return result
```

**Use Cases:**
- Batch crawl authority websites for policy docs
- Extract local plan PDFs and content
- Scrape news and press releases
- Extract planning committee minutes

**Pricing:**
- Scrape: $1 per 1000 pages
- Crawl: $3 per 1000 pages
- **Estimated:** $1-2 per authority (if crawling entire site)
- **Alternative:** Use for top 100 authorities only, Playwright for rest

---

### **BeautifulSoup4** (Fallback for Static Sites)
**Purpose:** Simple HTML parsing for static pages

```bash
pip install beautifulsoup4 aiohttp
```

```python
from bs4 import BeautifulSoup
import aiohttp

async def scrape_static_page(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            # Extract content
            content = soup.select_one('.main-content')
            return content.get_text(strip=True)
```

**Cost:** FREE

---

## 3. SEO Research & Keyword Tools

### **DataForSEO API** ⭐ PRIMARY FOR SEO INTELLIGENCE
**Purpose:** Keyword research, SERP analysis, competitor intelligence

**Setup:**
```bash
pip install dataforseo-client
```

**Configuration:**
```python
# .env
DATAFORSEO_LOGIN=your_email@domain.com
DATAFORSEO_PASSWORD=your_password

# backend/app/services/pseo/dataforseo_service.py

from dataforseo_client import RestClient

class DataForSEOService:
    def __init__(self):
        self.client = RestClient(
            os.environ["DATAFORSEO_LOGIN"],
            os.environ["DATAFORSEO_PASSWORD"]
        )

    async def get_keyword_data(self, authority_name: str):
        """Get keyword data for authority-specific terms"""

        keywords = [
            f"{authority_name} planning applications",
            f"planning permission {authority_name}",
            f"{authority_name} planning portal",
            f"submit planning application {authority_name}"
        ]

        post_data = [{
            "location_code": 2826,  # UK
            "language_code": "en",
            "keywords": keywords
        }]

        response = self.client.post("/v3/keywords_data/google_ads/search_volume/live", post_data)

        return response["tasks"][0]["result"]

    async def get_serp_competitors(self, keyword: str):
        """Analyze SERP for keyword to understand competition"""

        post_data = [{
            "location_code": 2826,
            "language_code": "en",
            "keyword": keyword,
            "depth": 100
        }]

        response = self.client.post("/v3/serp/google/organic/live/regular", post_data)

        # Extract competitors
        competitors = []
        for item in response["tasks"][0]["result"][0]["items"]:
            competitors.append({
                "url": item["url"],
                "title": item["title"],
                "description": item["description"],
                "position": item["rank_absolute"]
            })

        return competitors

    async def get_keyword_difficulty(self, keywords: list):
        """Get keyword difficulty scores"""

        post_data = [{
            "location_code": 2826,
            "language_code": "en",
            "keywords": keywords
        }]

        response = self.client.post("/v3/keywords_data/google_ads/keywords_for_keywords/live", post_data)

        return response["tasks"][0]["result"]
```

**Use Cases:**
- Keyword research for each authority
- Search volume analysis
- SERP competitor analysis
- Keyword difficulty scoring
- Related keyword discovery

**Pricing:**
- SERP API: $0.60 per 1000 results
- Keyword Data: $6 per 1000 keywords
- **Estimated:** $5-10 for all 425 authorities

---

### **Keywords Everywhere API** (Alternative/Supplementary)
**Purpose:** Quick keyword metrics and search volume

**Setup:**
```python
# .env
KEYWORDS_EVERYWHERE_API_KEY=xxx

import requests

def get_keyword_metrics(keyword: str):
    url = "https://api.keywordseverywhere.com/v1/get_keyword_data"

    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {KEYWORDS_EVERYWHERE_API_KEY}"},
        json={
            "country": "uk",
            "currency": "GBP",
            "dataSource": "gkp",
            "kw": [keyword]
        }
    )

    return response.json()
```

**Pricing:**
- $10 for 100,000 credits
- 1 keyword = 1 credit
- **Estimated:** $5 for all authorities

---

### **Context7 API** ⭐ FOR INDUSTRY CONTEXT
**Purpose:** Industry-specific content intelligence and context

**Setup:**
```python
# .env
CONTEXT7_API_KEY=xxx

import requests

class Context7Service:
    def __init__(self):
        self.api_key = os.environ["CONTEXT7_API_KEY"]
        self.base_url = "https://api.context7.com/v1"

    async def get_planning_context(self, authority_name: str, topic: str):
        """Get industry context for planning topics"""

        response = requests.post(
            f"{self.base_url}/context",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "query": f"{authority_name} {topic}",
                "industry": "real_estate_planning",
                "location": "uk",
                "depth": "comprehensive"
            }
        )

        return response.json()
```

**Use Cases:**
- Industry-specific context for planning terms
- Planning policy background
- Development trends context
- Planning law and regulation context

**Pricing:** Contact for pricing (typically $50-200/month)

---

## 4. News & Content Intelligence

### **Perplexity API** ⭐ FOR NEWS & RECENT DEVELOPMENTS
**Purpose:** Real-time web search and recent news aggregation

**Setup:**
```python
# .env
PERPLEXITY_API_KEY=pplx-xxx

import requests

class PerplexityService:
    def __init__(self):
        self.api_key = os.environ["PERPLEXITY_API_KEY"]
        self.base_url = "https://api.perplexity.ai"

    async def search_planning_news(self, authority_name: str):
        """Search for recent planning news"""

        query = f"{authority_name} planning applications news 2025"

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a planning news aggregator. Extract recent planning application news, major developments, and policy updates."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.2,
                "return_citations": True,
                "search_recency_filter": "month"
            }
        )

        return response.json()

    async def get_authority_updates(self, authority_name: str):
        """Get recent authority updates and announcements"""

        query = f"{authority_name} council planning committee decisions latest 2025"

        # Similar API call with different query
        response = requests.post(...)

        return response.json()
```

**Use Cases:**
- Recent planning news aggregation
- Authority announcements and updates
- Major development news
- Policy change detection

**Pricing:**
- Sonar Small: $0.20 per million tokens
- Sonar Large: $1 per million tokens
- **Estimated:** $5-10 for all authorities

---

### **Google News RSS** (Free Alternative)
```python
import feedparser

def get_google_news_feed(authority_name: str):
    url = f"https://news.google.com/rss/search?q={authority_name}+planning+applications&hl=en-GB&gl=GB&ceid=GB:en"

    feed = feedparser.parse(url)

    news_items = []
    for entry in feed.entries[:10]:
        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "summary": entry.summary
        })

    return news_items
```

**Cost:** FREE

---

## 5. Government & Official Data APIs

### **Planning Portal API** (If Available)
```python
# Note: UK Planning Portal doesn't have official public API
# Use web scraping instead
```

### **ONS API (Office for National Statistics)** - FREE
**Purpose:** Demographic and economic context data

```python
import requests

class ONSService:
    def __init__(self):
        self.base_url = "https://api.beta.ons.gov.uk/v1"

    async def get_population_data(self, area_code: str):
        """Get population statistics"""

        response = requests.get(
            f"{self.base_url}/population/search",
            params={"geography": area_code}
        )

        return response.json()

    async def get_housing_stats(self, area_code: str):
        """Get housing statistics"""

        # ONS housing data
        response = requests.get(
            f"{self.base_url}/datasets/housing-stats/editions/2024/versions/1",
            params={"geography": area_code}
        )

        return response.json()
```

**Cost:** FREE

---

### **Land Registry Data** - FREE
**Purpose:** Property price context

```python
async def get_land_registry_data(postcode: str):
    """Get property price data from Land Registry"""

    # Land Registry Price Paid Data
    url = "http://landregistry.data.gov.uk/data/ppi/transaction-record.json"

    response = requests.get(url, params={
        "propertyAddress.postcode": postcode,
        "_limit": 100
    })

    return response.json()
```

**Cost:** FREE

---

### **Planning Inspectorate Data** - FREE (if available)
```python
async def get_appeals_data(lpa_code: str):
    """Get planning appeals data"""

    # Note: May require web scraping if no API
    url = "https://acp.planninginspectorate.gov.uk/api/appeals"

    response = requests.get(url, params={"lpa": lpa_code})

    return response.json()
```

**Cost:** FREE (or scraping cost if no API)

---

## 6. Elasticsearch Configuration

### **Planning Explorer ES Setup**
```python
# backend/app/services/elasticsearch_service.py

from elasticsearch import AsyncElasticsearch

ES_CONFIG = {
    "hosts": [os.environ.get("ELASTICSEARCH_HOST", "localhost:9200")],
    "basic_auth": (
        os.environ.get("ES_USERNAME"),
        os.environ.get("ES_PASSWORD")
    ) if os.environ.get("ES_USERNAME") else None,
    "verify_certs": True,
    "ssl_show_warn": False
}

class ElasticsearchService:
    def __init__(self):
        self.client = AsyncElasticsearch(**ES_CONFIG)

    async def create_pseo_index(self):
        """Create index for pSEO pages"""

        mapping = {
            "mappings": {
                "properties": {
                    "authority_id": {"type": "keyword"},
                    "authority_name": {"type": "text"},
                    "url_slug": {"type": "keyword"},
                    "generated_date": {"type": "date"},
                    "meta": {
                        "properties": {
                            "title": {"type": "text"},
                            "description": {"type": "text"},
                            "keywords": {"type": "keyword"}
                        }
                    },
                    "sections": {
                        "type": "object",
                        "enabled": False  # Store as-is, don't index
                    },
                    "raw_data": {
                        "type": "object",
                        "enabled": False
                    }
                }
            }
        }

        await self.client.indices.create(index="pseo_pages", body=mapping)
```

**Cost:** Already included in your infrastructure

---

## 7. Complete Environment Variables

```bash
# .env (Complete Configuration)

# AI & Content Generation
ANTHROPIC_API_KEY=sk-ant-api03-xxx

# Web Scraping
FIRECRAWL_API_KEY=fc-xxx
PLAYWRIGHT_HEADLESS=true

# SEO Tools
DATAFORSEO_LOGIN=your_email@domain.com
DATAFORSEO_PASSWORD=your_password
KEYWORDS_EVERYWHERE_API_KEY=xxx
CONTEXT7_API_KEY=xxx

# News & Intelligence
PERPLEXITY_API_KEY=pplx-xxx

# Database & Storage
ELASTICSEARCH_HOST=localhost:9200
ES_USERNAME=elastic
ES_PASSWORD=xxx
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx

# Optional APIs
OPENAI_API_KEY=sk-xxx  # Backup for Claude
SERPER_API_KEY=xxx  # Google SERP alternative

# Configuration
MAX_CONCURRENT_REQUESTS=3
SCRAPING_TIMEOUT=30000
RATE_LIMIT_PER_MINUTE=50
```

---

## 8. Complete Requirements.txt

```txt
# Core Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.6.0
python-dotenv==1.0.0

# AI & LLM
anthropic==0.18.1
openai==1.12.0  # Backup

# Web Scraping
playwright==1.41.0
firecrawl-py==0.0.8
beautifulsoup4==4.12.3
aiohttp==3.9.3
lxml==5.1.0

# SEO Tools
dataforseo-client==1.0.27
requests==2.31.0

# Database
elasticsearch[async]==8.12.0
asyncpg==0.29.0

# Data Processing
pandas==2.2.0
numpy==1.26.3

# Utilities
feedparser==6.0.11  # RSS feeds
python-slugify==8.0.2
markdownify==0.11.6

# Testing
pytest==8.0.0
pytest-asyncio==0.23.4
```

---

## 9. Installation & Setup Script

```bash
#!/bin/bash
# setup_pseo_stack.sh

echo "Setting up pSEO Tool Stack..."

# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install Node.js tools (if using MCP)
npm install -g @playwright/mcp-server

# Create directories
mkdir -p backend/app/services/pseo
mkdir -p backend/outputs/pseo
mkdir -p backend/logs/pseo

# Validate environment variables
python -c "
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = [
    'ANTHROPIC_API_KEY',
    'ELASTICSEARCH_HOST'
]

missing = [var for var in required_vars if not os.getenv(var)]

if missing:
    print(f'Missing required env vars: {missing}')
    exit(1)
else:
    print('✓ All required environment variables set')
"

echo "✓ pSEO Stack setup complete!"
```

---

## 10. Tool Selection Strategy by Use Case

### **Scenario 1: Maximum Quality (Recommended)**
```yaml
Content Generation: Anthropic Claude Sonnet 4.5
Web Scraping: Firecrawl (top 100 authorities) + Playwright (rest)
SEO Research: DataForSEO
News Intelligence: Perplexity API
Government Data: Free APIs (ONS, Land Registry)

Estimated Cost: $150-200 for all 425 pages
```

### **Scenario 2: Budget-Friendly**
```yaml
Content Generation: Anthropic Claude Sonnet 4.5
Web Scraping: Playwright only (free)
SEO Research: Keywords Everywhere (cheap)
News Intelligence: Google News RSS (free)
Government Data: Free APIs

Estimated Cost: $85-100 for all 425 pages
```

### **Scenario 3: Premium Intelligence**
```yaml
Content Generation: Anthropic Claude Sonnet 4.5
Web Scraping: Firecrawl (all authorities)
SEO Research: DataForSEO + Context7
News Intelligence: Perplexity API
Government Data: Free APIs + Proprietary sources

Estimated Cost: $300-400 for all 425 pages
```

---

## 11. Rate Limiting & Concurrency Management

```python
# backend/app/services/pseo/rate_limiter.py

import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests_per_minute: int):
        self.max_requests = max_requests_per_minute
        self.requests = []

    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""

        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)

        # Remove requests older than 1 minute
        self.requests = [r for r in self.requests if r > one_minute_ago]

        if len(self.requests) >= self.max_requests:
            # Calculate wait time
            oldest_request = min(self.requests)
            wait_until = oldest_request + timedelta(minutes=1)
            wait_seconds = (wait_until - now).total_seconds()

            if wait_seconds > 0:
                print(f"Rate limit: waiting {wait_seconds:.1f}s")
                await asyncio.sleep(wait_seconds)

        self.requests.append(datetime.now())

# Usage
anthropic_limiter = RateLimiter(max_requests_per_minute=50)
firecrawl_limiter = RateLimiter(max_requests_per_minute=60)

async def generate_content(prompt):
    await anthropic_limiter.wait_if_needed()
    # Make API call
    pass
```

---

## 12. Complete Tool Integration Example

```python
# backend/app/services/pseo/orchestrator.py

from .playwright_scraper import PlaywrightScraper
from .firecrawl_scraper import FirecrawlScraper
from .dataforseo_service import DataForSEOService
from .perplexity_service import PerplexityService
from .content_generator import pSEOContentGenerator
from .rate_limiter import RateLimiter

class pSEOOrchestrator:
    def __init__(self):
        self.playwright = PlaywrightScraper()
        self.firecrawl = FirecrawlScraper()
        self.seo_intel = DataForSEOService()
        self.news_intel = PerplexityService()
        self.content_gen = pSEOContentGenerator()

        # Rate limiters
        self.anthropic_limiter = RateLimiter(50)
        self.firecrawl_limiter = RateLimiter(60)
        self.perplexity_limiter = RateLimiter(20)

    async def build_page(self, authority: dict) -> dict:
        """Orchestrate all tools to build pSEO page"""

        # 1. SEO Research
        await self.seo_intel.get_keyword_data(authority['name'])

        # 2. Web Scraping (choose based on site)
        if authority.get('has_js_portal'):
            scraped = await self.playwright.scrape_authority(authority['website'])
        else:
            await self.firecrawl_limiter.wait_if_needed()
            scraped = await self.firecrawl.scrape_authority_website(authority['website'])

        # 3. News Intelligence
        await self.perplexity_limiter.wait_if_needed()
        news = await self.news_intel.search_planning_news(authority['name'])

        # 4. Content Generation
        await self.anthropic_limiter.wait_if_needed()
        content = await self.content_gen.generate_all_sections(
            authority=authority,
            scraped=scraped,
            news=news
        )

        return content
```

---

## 13. Monitoring & Logging

```python
# backend/app/services/pseo/logger.py

import logging
from datetime import datetime

class pSEOLogger:
    def __init__(self):
        self.logger = logging.getLogger("pseo")
        self.logger.setLevel(logging.INFO)

        # File handler
        handler = logging.FileHandler(f"logs/pseo/pseo_{datetime.now().strftime('%Y%m%d')}.log")
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)

    def log_api_call(self, service: str, cost: float):
        self.logger.info(f"API Call - {service} - Cost: ${cost:.4f}")

    def log_page_complete(self, authority: str, word_count: int, total_cost: float):
        self.logger.info(f"Page Complete - {authority} - {word_count} words - ${total_cost:.2f}")

    def log_error(self, authority: str, error: str):
        self.logger.error(f"Error - {authority} - {error}")
```

---

## 14. Cost Tracking Dashboard

```python
# backend/app/services/pseo/cost_tracker.py

class CostTracker:
    def __init__(self):
        self.costs = {
            "anthropic": 0,
            "firecrawl": 0,
            "dataforseo": 0,
            "perplexity": 0,
            "total": 0
        }

    def add_cost(self, service: str, amount: float):
        self.costs[service] += amount
        self.costs["total"] += amount

    def estimate_remaining_cost(self, pages_remaining: int, avg_cost_per_page: float):
        return pages_remaining * avg_cost_per_page

    def get_summary(self):
        return {
            **self.costs,
            "avg_per_page": self.costs["total"] / max(1, self.pages_completed)
        }
```

---

## Summary: Recommended Tool Stack

### **Core Tools (Required)**
1. ✅ **Anthropic Claude API** - $85 for all pages
2. ✅ **Playwright** - FREE (primary scraper)
3. ✅ **Elasticsearch** - Already have
4. ✅ **ONS/Land Registry APIs** - FREE

**Minimum Total Cost: ~$85**

### **Enhanced Tools (Recommended)**
5. ⭐ **Firecrawl** - $50-100 (for top 100 authorities)
6. ⭐ **DataForSEO** - $10-20 (keyword research)
7. ⭐ **Perplexity** - $10-20 (news intelligence)

**Recommended Total Cost: ~$150-200**

### **Premium Tools (Optional)**
8. 💎 **Context7** - $50-200/month (industry context)
9. 💎 **Keywords Everywhere** - $10 (backup SEO)

**Premium Total Cost: ~$300-400**

---

## Next Steps

1. ✅ Set up environment variables
2. ✅ Install required packages
3. ✅ Test each API integration
4. ✅ Run on 5 sample authorities
5. ✅ Optimize based on results
6. ✅ Scale to all 425 authorities

Would you like me to create the implementation code with all these tools integrated?
