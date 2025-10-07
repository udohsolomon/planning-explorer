# Applicant/Agent Enrichment Agent - Backend Implementation Guide

## Overview

This document provides the complete backend implementation for the real-time enrichment agent that extracts Applicant Name and Agent Name from UK planning portal websites.

## Architecture

```
User Request → FastAPI Endpoint → Redis Cache Check
                                    ↓ Cache Miss
                               Enrichment Agent
                                    ↓
                         Portal Type Detection
                                    ↓
                    ┌────────────────┴────────────────┐
                    ↓                ↓                 ↓
                Type 1:          Type 2:          Type 3:
               Idox (60%)      Custom (20%)    Adaptive (20%)
                Firecrawl      Firecrawl       Playwright+Context7
                    ↓                ↓                 ↓
                    └────────────────┬─────────────────┘
                                    ↓
                            Data Extraction
                                    ↓
                          Validation & Caching
                                    ↓
                         Return Enriched Data
```

## Directory Structure

```
backend/app/agents/enrichment/
├── __init__.py
├── applicant_agent.py         # Main enrichment agent
├── portal_detectors.py        # Portal type detection logic
├── extractors/
│   ├── __init__.py
│   ├── idox_extractor.py      # Type 1: Idox portals
│   ├── liverpool_extractor.py # Type 2: Liverpool example
│   └── adaptive_extractor.py  # Type 3: Adaptive/unknown
└── utils/
    ├── __init__.py
    ├── validators.py          # Data validation
    └── cleaners.py            # Text cleaning utilities

backend/app/services/
├── mcp_clients/
│   ├── __init__.py
│   ├── playwright_client.py   # Playwright MCP wrapper
│   ├── firecrawl_client.py    # Firecrawl MCP wrapper
│   └── context7_client.py     # Context7 MCP wrapper
├── cache_service.py           # Redis caching
└── enrichment_service.py      # Main enrichment service

backend/app/api/
└── enrichment.py              # Enrichment API endpoints

backend/tests/agents/
├── test_applicant_agent.py
├── test_portal_detectors.py
└── test_extractors.py
```

## Implementation Files

### File 1: Portal Detection
**Path**: `backend/app/agents/enrichment/portal_detectors.py`

```python
"""
Portal type detection for UK planning authority websites.
"""

from urllib.parse import urlparse
from typing import Literal
import re

PortalType = Literal["idox_public_access", "liverpool_custom", "unknown"]

class PortalDetector:
    """Detect portal type from URL"""

    # Known portal patterns
    IDOX_PATTERN = r"publicaccess\..*\.gov\.uk/online-applications"
    LIVERPOOL_PATTERN = r"lar\.liverpool\.gov\.uk/planning"

    # Known custom portals (extend as needed)
    KNOWN_CUSTOM_PORTALS = {
        "lar.liverpool.gov.uk": "liverpool_custom",
        "planning.manchester.gov.uk": "manchester_custom",
        # Add more as discovered
    }

    @classmethod
    def detect(cls, url: str) -> PortalType:
        """
        Detect portal type from URL.

        Args:
            url: Planning application URL

        Returns:
            Portal type identifier
        """
        if not url:
            return "unknown"

        # Check for Idox Public Access
        if re.search(cls.IDOX_PATTERN, url):
            return "idox_public_access"

        # Check for known custom portals
        domain = urlparse(url).netloc
        if domain in cls.KNOWN_CUSTOM_PORTALS:
            return cls.KNOWN_CUSTOM_PORTALS[domain]

        return "unknown"

    @classmethod
    def is_idox(cls, url: str) -> bool:
        """Check if URL is Idox portal"""
        return cls.detect(url) == "idox_public_access"

    @classmethod
    def is_known_custom(cls, url: str) -> bool:
        """Check if URL is known custom portal"""
        portal_type = cls.detect(url)
        return portal_type != "unknown" and portal_type != "idox_public_access"
```

### File 2: Data Validation and Cleaning
**Path**: `backend/app/agents/enrichment/utils/validators.py`

```python
"""
Data validation and cleaning for enriched applicant/agent data.
"""

import re
from typing import Optional

class ApplicantDataValidator:
    """Validate and clean applicant/agent data"""

    # Common "not available" variations
    NA_PATTERNS = [
        r"^n/?a$",
        r"^not\s+available$",
        r"^none$",
        r"^-+$",
        r"^\s*$"
    ]

    # Patterns that suggest extraction error
    ERROR_PATTERNS = [
        r"applicant\s+name",  # Extracted label instead of value
        r"agent\s+name",
        r"<.*>",  # HTML tags
        r"javascript:",
        r"onclick=",
    ]

    @classmethod
    def clean(cls, value: Optional[str]) -> Optional[str]:
        """
        Clean and validate extracted value.

        Args:
            value: Raw extracted text

        Returns:
            Cleaned value or None if invalid
        """
        if not value:
            return None

        # Strip whitespace
        value = value.strip()

        # Check for "not available" patterns
        for pattern in cls.NA_PATTERNS:
            if re.match(pattern, value, re.IGNORECASE):
                return None

        # Check for extraction errors
        for pattern in cls.ERROR_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return None

        # Length validation
        if len(value) < 2 or len(value) > 200:
            return None

        return value

    @classmethod
    def validate_result(cls, applicant_name: Optional[str],
                       agent_name: Optional[str]) -> dict:
        """
        Validate complete extraction result.

        Returns:
            {
                "valid": bool,
                "applicant_name": str|None,
                "agent_name": str|None,
                "warnings": list
            }
        """
        warnings = []

        cleaned_applicant = cls.clean(applicant_name)
        cleaned_agent = cls.clean(agent_name)

        # Warn if both are None
        if cleaned_applicant is None and cleaned_agent is None:
            warnings.append("Both applicant and agent names are unavailable")

        return {
            "valid": True,  # Even if both None, it's valid (some apps have no agent)
            "applicant_name": cleaned_applicant,
            "agent_name": cleaned_agent,
            "warnings": warnings
        }
```

### File 3: Main Enrichment Agent
**Path**: `backend/app/agents/enrichment/applicant_agent.py`

```python
"""
Main enrichment agent for applicant and agent name extraction.
"""

import asyncio
import time
import logging
from typing import Dict, Optional
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from .portal_detectors import PortalDetector
from .utils.validators import ApplicantDataValidator
from app.services.mcp_clients.firecrawl_client import FirecrawlClient
from app.services.mcp_clients.playwright_client import PlaywrightClient
from app.services.mcp_clients.context7_client import Context7Client

logger = logging.getLogger(__name__)

class ApplicantEnrichmentAgent:
    """
    Real-time enrichment agent for extracting applicant and agent names
    from UK planning authority websites.
    """

    def __init__(self):
        self.firecrawl = FirecrawlClient()
        self.playwright = PlaywrightClient()
        self.context7 = Context7Client()

        # Portal pattern cache (in-memory)
        self.portal_patterns = {}

    async def enrich(self, url: str, application_id: str) -> Dict:
        """
        Main entry point for real-time enrichment.

        Args:
            url: Planning portal URL
            application_id: Application reference ID

        Returns:
            {
                "success": bool,
                "data": {
                    "applicant_name": str|None,
                    "agent_name": str|None
                },
                "metadata": {
                    "portal_type": str,
                    "extraction_method": str,
                    "processing_time_ms": int,
                    "confidence": float,
                    "timestamp": str
                }
            }
        """
        start_time = time.time()

        try:
            logger.info(f"Starting enrichment for {application_id} at {url}")

            # Detect portal type
            portal_type = PortalDetector.detect(url)
            logger.info(f"Detected portal type: {portal_type}")

            # Select extraction strategy
            if portal_type == "idox_public_access":
                result = await self._extract_idox(url)
                method = "firecrawl_idox"
            elif portal_type in self.portal_patterns:
                result = await self._extract_custom_cached(url, portal_type)
                method = "firecrawl_cached"
            elif PortalDetector.is_known_custom(url):
                result = await self._extract_custom_direct(url, portal_type)
                method = "firecrawl_custom"
            else:
                result = await self._extract_adaptive(url)
                method = "playwright_context7"

            # Validate result
            validated = ApplicantDataValidator.validate_result(
                result.get("applicant_name") if result else None,
                result.get("agent_name") if result else None
            )

            processing_time = (time.time() - start_time) * 1000

            logger.info(f"Enrichment completed in {processing_time:.0f}ms: "
                       f"applicant={validated['applicant_name']}, "
                       f"agent={validated['agent_name']}")

            return {
                "success": validated["valid"],
                "data": {
                    "applicant_name": validated["applicant_name"],
                    "agent_name": validated["agent_name"]
                },
                "metadata": {
                    "portal_type": portal_type,
                    "extraction_method": method,
                    "processing_time_ms": int(processing_time),
                    "confidence": self._calculate_confidence(validated, method),
                    "timestamp": datetime.utcnow().isoformat(),
                    "warnings": validated.get("warnings", [])
                }
            }

        except Exception as e:
            logger.error(f"Enrichment failed for {application_id}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "data": {"applicant_name": None, "agent_name": None},
                "error": str(e),
                "metadata": {
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }

    async def _extract_idox(self, url: str) -> Optional[Dict]:
        """
        Fast extraction for Idox Public Access portals (Type 1).

        Strategy:
        1. Modify URL to navigate to "Details" tab
        2. Scrape with Firecrawl (fast, static HTML)
        3. Extract from table structure
        """
        try:
            # Navigate to details tab
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            query_params['activeTab'] = ['details']

            new_query = urlencode(query_params, doseq=True)
            details_url = urlunparse((
                parsed.scheme, parsed.netloc, parsed.path,
                parsed.params, new_query, parsed.fragment
            ))

            logger.debug(f"Fetching Idox details page: {details_url}")

            # Scrape with Firecrawl
            html_content = await self.firecrawl.fetch(details_url)

            # Extract using table parsing
            applicant_name = self._extract_table_value(html_content, "Applicant Name")
            agent_name = self._extract_table_value(html_content, "Agent Name")

            return {
                "applicant_name": applicant_name,
                "agent_name": agent_name
            }

        except Exception as e:
            logger.error(f"Idox extraction failed: {e}")
            return None

    async def _extract_custom_direct(self, url: str, portal_type: str) -> Optional[Dict]:
        """
        Extract from known custom portal (e.g., Liverpool).

        Strategy:
        1. Direct URL access (no navigation needed)
        2. Scrape with Firecrawl
        3. Extract using labeled field patterns
        """
        try:
            logger.debug(f"Fetching custom portal: {url}")

            html_content = await self.firecrawl.fetch(url)

            # Extract using definition list or labeled fields
            applicant_name = self._extract_labeled_field(html_content, "Applicant:")
            agent_name = self._extract_labeled_field(html_content, "Agent:")

            return {
                "applicant_name": applicant_name,
                "agent_name": agent_name
            }

        except Exception as e:
            logger.error(f"Custom portal extraction failed: {e}")
            return None

    async def _extract_custom_cached(self, url: str, portal_type: str) -> Optional[Dict]:
        """Extract using previously cached pattern."""
        pattern = self.portal_patterns.get(portal_type)
        if not pattern:
            return await self._extract_adaptive(url)

        try:
            html_content = await self.firecrawl.fetch(url)

            applicant_name = self._extract_by_selector(
                html_content,
                pattern['applicant_selector']
            )
            agent_name = self._extract_by_selector(
                html_content,
                pattern['agent_selector']
            )

            return {
                "applicant_name": applicant_name,
                "agent_name": agent_name
            }

        except Exception as e:
            logger.warning(f"Cached pattern failed, falling back: {e}")
            return await self._extract_adaptive(url)

    async def _extract_adaptive(self, url: str) -> Optional[Dict]:
        """
        Adaptive extraction for unknown portals using Context7 (Type 3).

        Strategy:
        1. Fetch page with Playwright (handles JavaScript)
        2. Use Context7 for semantic extraction
        3. Cache successful pattern for future use
        """
        try:
            logger.debug(f"Using adaptive extraction for: {url}")

            # Fetch page with Playwright
            page_content = await self.playwright.fetch(url)

            # Use Context7 for semantic extraction
            prompt = """
            Extract the applicant name and agent name from this planning application page.
            Look for fields labeled "Applicant", "Applicant Name", "Agent", "Agent Name", or similar.

            Return ONLY a JSON object with this exact structure:
            {
                "applicant_name": "exact name or null",
                "agent_name": "exact name or null"
            }

            If a field is not available, use null. Do not include labels, only the actual names.
            """

            result = await self.context7.extract(page_content, prompt)

            # Cache successful pattern for future use
            if result:
                domain = urlparse(url).netloc
                self.portal_patterns[domain] = {
                    "type": "adaptive_learned",
                    "last_success": datetime.utcnow().isoformat()
                }
                logger.info(f"Cached new pattern for domain: {domain}")

            return result

        except Exception as e:
            logger.error(f"Adaptive extraction failed: {e}")
            return None

    def _extract_table_value(self, html: str, label: str) -> Optional[str]:
        """
        Extract value from HTML table by label.

        Args:
            html: HTML content
            label: Field label to search for

        Returns:
            Extracted value or None
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')

        # Find row containing label
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                if label.lower() in cells[0].get_text().lower():
                    value = cells[1].get_text().strip()
                    return ApplicantDataValidator.clean(value)

        return None

    def _extract_labeled_field(self, html: str, label: str) -> Optional[str]:
        """
        Extract value from labeled field (dt/dd structure or similar).

        Args:
            html: HTML content
            label: Field label to search for

        Returns:
            Extracted value or None
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')

        # Try dt/dd structure
        for dt in soup.find_all('dt'):
            if label.lower() in dt.get_text().lower():
                dd = dt.find_next_sibling('dd')
                if dd:
                    value = dd.get_text().strip()
                    return ApplicantDataValidator.clean(value)

        # Try labeled div/span structures
        for elem in soup.find_all(['div', 'span', 'label']):
            if label.lower() in elem.get_text().lower():
                # Look for next sibling or child
                next_elem = elem.find_next_sibling()
                if next_elem:
                    value = next_elem.get_text().strip()
                    return ApplicantDataValidator.clean(value)

        return None

    def _extract_by_selector(self, html: str, selector: str) -> Optional[str]:
        """Extract value using CSS selector."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')
        elem = soup.select_one(selector)

        if elem:
            value = elem.get_text().strip()
            return ApplicantDataValidator.clean(value)

        return None

    def _calculate_confidence(self, validated: dict, method: str) -> float:
        """
        Calculate confidence score for extraction.

        Args:
            validated: Validation result
            method: Extraction method used

        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.5  # Base confidence

        # Method-based confidence
        if method.startswith("firecrawl"):
            confidence += 0.3  # Fast, reliable methods
        elif method.startswith("playwright"):
            confidence += 0.2  # Slower but handles JS

        # Data-based confidence
        if validated.get("applicant_name"):
            confidence += 0.1
        if validated.get("agent_name"):
            confidence += 0.1

        # Warnings reduce confidence
        if validated.get("warnings"):
            confidence -= 0.1 * len(validated["warnings"])

        return min(max(confidence, 0.0), 1.0)


# Async wrapper for convenience
async def enrich_applicant_data(url: str, application_id: str) -> Dict:
    """
    Convenience function for enriching applicant data.

    Args:
        url: Planning portal URL
        application_id: Application reference ID

    Returns:
        Enrichment result dictionary
    """
    agent = ApplicantEnrichmentAgent()
    return await agent.enrich(url, application_id)
```

## Redis Caching Implementation

**Path**: `backend/app/services/cache_service.py`

```python
"""
Redis caching service for enriched data.
"""

import redis.asyncio as redis
import json
import logging
from typing import Optional, Any
from datetime import timedelta

logger = logging.getLogger(__name__)

class CacheService:
    """Redis cache service"""

    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.ttl_seconds = 86400  # 24 hours

    async def connect(self, host: str = "localhost", port: int = 6379):
        """Connect to Redis"""
        try:
            self.redis = await redis.from_url(
                f"redis://{host}:{port}",
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()

    async def get_enrichment(self, application_id: str) -> Optional[dict]:
        """
        Get cached enrichment data.

        Args:
            application_id: Application ID

        Returns:
            Cached data or None
        """
        key = f"applicant_agent:{application_id}"

        try:
            value = await self.redis.get(key)
            if value:
                logger.debug(f"Cache hit for {application_id}")
                return json.loads(value)
            else:
                logger.debug(f"Cache miss for {application_id}")
                return None
        except Exception as e:
            logger.error(f"Cache get failed: {e}")
            return None

    async def set_enrichment(self, application_id: str, data: dict) -> bool:
        """
        Cache enrichment data.

        Args:
            application_id: Application ID
            data: Enrichment data to cache

        Returns:
            Success status
        """
        key = f"applicant_agent:{application_id}"

        try:
            await self.redis.setex(
                key,
                self.ttl_seconds,
                json.dumps(data)
            )
            logger.debug(f"Cached enrichment for {application_id}")
            return True
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
            return False

    async def invalidate(self, application_id: str) -> bool:
        """Invalidate cached enrichment"""
        key = f"applicant_agent:{application_id}"

        try:
            await self.redis.delete(key)
            logger.debug(f"Invalidated cache for {application_id}")
            return True
        except Exception as e:
            logger.error(f"Cache invalidate failed: {e}")
            return False

    async def health_check(self) -> bool:
        """Check Redis health"""
        try:
            await self.redis.ping()
            return True
        except:
            return False


# Global cache instance
cache = CacheService()
```

## Next Steps

1. ✅ Create MCP client wrappers (Playwright, Firecrawl, Context7)
2. ✅ Integrate enrichment agent into FastAPI report endpoint
3. ✅ Add comprehensive tests
4. ✅ Deploy Redis instance
5. ✅ Monitor performance and success rates

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Type 1 Extraction | <3s | TBD |
| Type 2 Extraction | <3s | TBD |
| Type 3 Extraction | <8s | TBD |
| Cache Hit Response | <100ms | TBD |
| Success Rate (Type 1) | >98% | TBD |
| Success Rate (Type 2) | >92% | TBD |
| Success Rate (Type 3) | >85% | TBD |

---

**Status**: Implementation Ready
**Dependencies**: Redis, BeautifulSoup4, Playwright MCP, Firecrawl MCP, Context7 MCP
**Last Updated**: 2025-10-04
