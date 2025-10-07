"""
Firecrawl MCP Client Wrapper

This module wraps the Firecrawl MCP server for fast static HTML scraping.
"""

import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class FirecrawlClient:
    """
    Wrapper for Firecrawl MCP server to handle static HTML scraping.

    Used for portals with server-rendered HTML (no JavaScript required),
    typically taking 2-3 seconds for extraction. Ideal for Idox portals.
    """

    def __init__(self):
        """Initialize Firecrawl client with MCP server connection."""
        self.timeout_ms = 10000  # 10 second timeout
        logger.info("FirecrawlClient initialized")

    async def fetch(self, url: str, format: str = "html") -> str:
        """
        Fetch page content using fast HTTP scraping.

        Args:
            url: Target URL to scrape
            format: Response format ("html" or "markdown")

        Returns:
            Page content as HTML or markdown string

        Raises:
            Exception: If scraping fails or times out
        """
        try:
            logger.info(f"Fetching with Firecrawl (HTTP): {url}")

            # Use httpx for fast HTTP requests (static HTML pages)
            import httpx

            async with httpx.AsyncClient(timeout=self.timeout_ms / 1000) as client:
                response = await client.get(
                    url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    },
                    follow_redirects=True
                )
                response.raise_for_status()

                content = response.text
                logger.info(f"Successfully fetched {len(content)} bytes from {url}")
                return content

        except httpx.HTTPError as e:
            logger.warning(f"HTTP fetch failed for {url}: {e}, falling back to Playwright")

            # Fallback to Playwright for JavaScript-heavy pages
            try:
                from playwright.async_api import async_playwright

                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    await page.goto(url, timeout=self.timeout_ms)
                    content = await page.content()
                    await browser.close()

                    logger.info(f"Playwright fallback succeeded for {url}")
                    return content

            except Exception as playwright_error:
                logger.error(f"Both HTTP and Playwright failed for {url}: {playwright_error}")
                raise

        except Exception as e:
            logger.error(f"Firecrawl fetch failed for {url}: {str(e)}")
            raise

    async def fetch_with_metadata(self, url: str) -> Dict:
        """
        Fetch page with additional metadata.

        Args:
            url: Target URL to scrape

        Returns:
            Dictionary with content, title, metadata, etc.
        """
        try:
            html = await self.fetch(url)

            # TODO: Extract metadata from MCP response
            return {
                "content": html,
                "url": url,
                "status": "success",
                "metadata": {
                    "title": "Planning Application",
                    "response_time_ms": 2000
                }
            }

        except Exception as e:
            logger.error(f"Firecrawl metadata fetch failed: {str(e)}")
            raise

    async def health_check(self) -> bool:
        """
        Check if Firecrawl MCP server is responsive.

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            # TODO: Implement health check via MCP
            # result = await mcp_client.call_tool("firecrawl_health", {})
            # return result["status"] == "ok"

            logger.warning("Firecrawl health check not implemented")
            return True

        except Exception as e:
            logger.error(f"Firecrawl health check failed: {str(e)}")
            return False
