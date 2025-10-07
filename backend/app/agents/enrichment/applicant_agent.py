"""
Main enrichment agent for applicant and agent name extraction.

This module implements the core enrichment logic that extracts applicant
and agent names from UK planning portal websites using multiple strategies.
"""

import asyncio
import time
import logging
from typing import Dict, Optional
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup

from .portal_detectors import PortalDetector
from .utils.validators import ApplicantDataValidator

# MCP clients will be imported when available
try:
    from app.services.mcp_clients.firecrawl_client import FirecrawlClient
    from app.services.mcp_clients.playwright_client import PlaywrightClient
    from app.services.mcp_clients.context7_client import Context7Client
    CLIENTS_AVAILABLE = True
except ImportError:
    CLIENTS_AVAILABLE = False
    logging.warning("MCP clients not available, using mock implementations")

logger = logging.getLogger(__name__)


class ApplicantEnrichmentAgent:
    """
    Real-time enrichment agent for extracting applicant and agent names
    from UK planning authority websites.

    Supports three extraction strategies:
    1. Idox Public Access (60% of UK authorities)
    2. Known custom portals (20%)
    3. Adaptive/unknown portals (20%)
    """

    def __init__(self):
        """Initialize the enrichment agent with MCP clients or mocks."""
        if CLIENTS_AVAILABLE:
            self.firecrawl = FirecrawlClient()
            self.playwright = PlaywrightClient()
            self.context7 = Context7Client()
        else:
            # Mock clients for testing without MCP servers
            self.firecrawl = self._create_mock_client("firecrawl")
            self.playwright = self._create_mock_client("playwright")
            self.context7 = self._create_mock_client("context7")

        # Portal pattern cache (in-memory)
        self.portal_patterns = {}

    def _create_mock_client(self, client_type: str):
        """Create mock client for testing without MCP servers."""
        class MockClient:
            async def fetch(self, url: str) -> str:
                logger.warning(f"Using mock {client_type} client for {url}")
                return "<html><body>Mock HTML - MCP clients not available</body></html>"

            async def extract(self, content: str, prompt: str) -> Optional[Dict]:
                logger.warning(f"Using mock {client_type} extraction")
                return None

        return MockClient()

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
                    "agent_name": str|None,
                    "ward_name": str|None,
                    "decided_date": str|None,
                    "n_documents": int|None,
                    "n_statutory_days": int|None,
                    "docs_url": str|None
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
                    "agent_name": validated["agent_name"],
                    "ward_name": result.get("ward_name") if result else None,
                    "decided_date": result.get("decided_date") if result else None,
                    "n_documents": result.get("n_documents") if result else None,
                    "n_statutory_days": result.get("n_statutory_days") if result else None,
                    "docs_url": result.get("docs_url") if result else None
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
                "data": {
                    "applicant_name": None,
                    "agent_name": None,
                    "ward_name": None,
                    "decided_date": None,
                    "n_documents": None,
                    "n_statutory_days": None,
                    "docs_url": None
                },
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
            ward_name = self._extract_table_value(html_content, "Ward")
            decided_date = self._extract_table_value(html_content, "Decision Date")

            # Extract number of documents from the documents tab
            n_documents = self._extract_document_count(html_content, url)

            # Extract statutory days or target date
            n_statutory_days = self._extract_statutory_days(html_content)

            # Build docs URL
            docs_url = self._build_docs_url(url)

            return {
                "applicant_name": applicant_name,
                "agent_name": agent_name,
                "ward_name": ward_name,
                "decided_date": decided_date,
                "n_documents": n_documents,
                "n_statutory_days": n_statutory_days,
                "docs_url": docs_url
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
        soup = BeautifulSoup(html, 'html.parser')

        # Try th + td in same row (Dover Idox pattern)
        for row in soup.find_all('tr'):
            th = row.find('th')
            td = row.find('td')

            if th and td and label.lower() in th.get_text().lower():
                value = td.get_text().strip()
                return ApplicantDataValidator.clean(value)

            # Also try td/td pairs (other portals)
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
        soup = BeautifulSoup(html, 'html.parser')
        elem = soup.select_one(selector)

        if elem:
            value = elem.get_text().strip()
            return ApplicantDataValidator.clean(value)

        return None

    def _extract_document_count(self, html: str, base_url: str) -> Optional[int]:
        """
        Extract number of documents from the summary page or documents tab.

        For Idox portals, this is typically shown on the summary tab.
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Look for "Documents" link/button with count
        # Common patterns: "Documents (38)", "38 Documents", etc.
        import re

        # Try to find documents tab or link
        docs_tab = soup.find(string=re.compile(r'Documents?\s*\(?\d+\)?', re.IGNORECASE))
        if docs_tab:
            match = re.search(r'(\d+)', docs_tab)
            if match:
                return int(match.group(1))

        # Try to find in table with label "Number of Documents" or similar
        doc_count = self._extract_table_value(html, "Number of Documents")
        if doc_count and doc_count.isdigit():
            return int(doc_count)

        return None

    def _extract_statutory_days(self, html: str) -> Optional[int]:
        """Extract statutory days or calculate from target determination date."""
        soup = BeautifulSoup(html, 'html.parser')

        # Try to find statutory period directly
        statutory = self._extract_table_value(html, "Statutory Period")
        if statutory and statutory.replace(' days', '').isdigit():
            return int(statutory.replace(' days', ''))

        # Try target determination date
        target_date = self._extract_table_value(html, "Target Determination Date")
        if target_date:
            # Could calculate days from submission to target, but for now just return standard 56
            return 56  # Standard for most applications

        return None

    def _build_docs_url(self, base_url: str) -> Optional[str]:
        """Build documents tab URL from base application URL."""
        try:
            parsed = urlparse(base_url)
            query_params = parse_qs(parsed.query)

            # Change activeTab to documents
            query_params['activeTab'] = ['documents']

            new_query = urlencode(query_params, doseq=True)
            docs_url = urlunparse((
                parsed.scheme, parsed.netloc, parsed.path,
                parsed.params, new_query, parsed.fragment
            ))

            return docs_url
        except Exception as e:
            logger.warning(f"Failed to build docs URL: {e}")
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
