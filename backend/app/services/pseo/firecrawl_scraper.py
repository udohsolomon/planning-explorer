"""
Firecrawl API Scraper for Complex Authority Websites
AI-powered scraping for 20% of complex authorities
"""

from typing import Dict, List, Optional
from firecrawl import FirecrawlApp
import os
from datetime import datetime
import asyncio


class FirecrawlScraper:
    """
    Scrape complex authority websites using Firecrawl AI.
    Used for JavaScript-heavy portals, React apps, and complex sites.
    Cost: ~$0.001 per page scrape, ~$0.003 per crawl
    """

    def __init__(self, authority: Dict):
        self.authority = authority
        self.base_url = authority.get('website_url', '')

        # Initialize Firecrawl
        api_key = os.getenv('FIRECRAWL_API_KEY')
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY not set in environment")

        self.app = FirecrawlApp(api_key=api_key)
        self.scraped_content: Dict = {}

    async def scrape_authority(self) -> Dict:
        """Main entry point - scrape all relevant pages"""

        try:
            # Use crawl mode for comprehensive scraping
            results = await self._crawl_authority_site()

            # Process and structure the results
            self.scraped_content = {
                'news': self._extract_news_from_crawl(results),
                'local_plan': self._extract_local_plan_from_crawl(results),
                'policies': self._extract_policies_from_crawl(results),
                'committee': self._extract_committee_from_crawl(results)
            }

        except Exception as e:
            print(f"Firecrawl error for {self.authority['name']}: {e}")
            # Fallback to single page scraping
            self.scraped_content = await self._scrape_individual_pages()

        return self.scraped_content

    async def _crawl_authority_site(self) -> Dict:
        """Crawl entire authority website for planning content"""

        try:
            crawl_result = self.app.crawl_url(
                self.base_url,
                params={
                    'crawlerOptions': {
                        'includes': [
                            '/planning/*',
                            '/news/*',
                            '/local-plan/*',
                            '/policy/*',
                            '/committee/*',
                            '/spd/*'
                        ],
                        'excludes': [
                            '/admin/*',
                            '/login/*',
                            '/search/*',
                            '/images/*',
                            '/css/*',
                            '/js/*'
                        ],
                        'maxDepth': 3,
                        'limit': 50,  # Limit to 50 pages to control cost
                        'allowBackwardCrawling': False
                    },
                    'pageOptions': {
                        'onlyMainContent': True,
                        'includeHtml': False,
                        'screenshot': False,  # Save cost
                        'waitFor': 2000
                    }
                }
            )

            return crawl_result

        except Exception as e:
            print(f"Crawl failed: {e}")
            return {}

    async def _scrape_individual_pages(self) -> Dict:
        """Fallback: Scrape specific pages individually"""

        pages_to_scrape = {
            'news': f"{self.base_url}/planning/news",
            'local_plan': f"{self.base_url}/planning/local-plan",
            'policies': f"{self.base_url}/planning/policy",
            'committee': f"{self.base_url}/planning/committee"
        }

        results = {}

        for key, url in pages_to_scrape.items():
            try:
                result = self.app.scrape_url(
                    url,
                    params={
                        'formats': ['markdown', 'html'],
                        'onlyMainContent': True,
                        'waitFor': 2000
                    }
                )

                results[key] = {
                    'markdown': result.get('markdown', ''),
                    'html': result.get('html', ''),
                    'links': result.get('links', []),
                    'metadata': result.get('metadata', {})
                }

            except Exception as e:
                print(f"Error scraping {url}: {e}")
                results[key] = None

        # Extract structured data from markdown
        return {
            'news': self._parse_news_from_markdown(results.get('news', {})),
            'local_plan': self._parse_local_plan_from_markdown(results.get('local_plan', {})),
            'policies': self._parse_policies_from_markdown(results.get('policies', {})),
            'committee': self._parse_committee_from_markdown(results.get('committee', {}))
        }

    def _extract_news_from_crawl(self, crawl_result: Dict) -> List[Dict]:
        """Extract news items from crawl results"""

        news_items = []

        if not crawl_result or 'data' not in crawl_result:
            return news_items

        for page in crawl_result.get('data', []):
            url = page.get('url', '')
            markdown = page.get('markdown', '')
            metadata = page.get('metadata', {})

            # Check if this is a news page
            if any(keyword in url.lower() for keyword in ['news', 'press-release', 'announcement']):
                # Extract news from markdown using AI-identified structure
                title = metadata.get('title', '')
                description = metadata.get('description', '')

                # Parse date from markdown or metadata
                date = ''
                if 'date' in metadata:
                    date = metadata['date']
                elif 'published' in metadata:
                    date = metadata['published']

                news_items.append({
                    'title': title,
                    'summary': description[:300] if description else '',
                    'url': url,
                    'date': date,
                    'source': 'firecrawl',
                    'scraped_at': datetime.now().isoformat()
                })

        return news_items[:10]

    def _extract_local_plan_from_crawl(self, crawl_result: Dict) -> Dict:
        """Extract local plan from crawl results"""

        local_plan_data = {}

        if not crawl_result or 'data' not in crawl_result:
            return local_plan_data

        for page in crawl_result.get('data', []):
            url = page.get('url', '')
            markdown = page.get('markdown', '')
            metadata = page.get('metadata', {})

            if any(keyword in url.lower() for keyword in ['local-plan', 'development-plan', 'core-strategy']):
                # Extract PDF links from markdown
                pdf_links = []
                links = page.get('links', [])
                for link in links:
                    if link.endswith('.pdf') and any(k in link.lower() for k in ['plan', 'strategy', 'policy']):
                        pdf_links.append({
                            'title': link.split('/')[-1].replace('.pdf', '').replace('-', ' ').title(),
                            'url': link
                        })

                local_plan_data = {
                    'summary': markdown[:1000] if markdown else metadata.get('description', ''),
                    'url': url,
                    'documents': pdf_links[:10],
                    'scraped_at': datetime.now().isoformat()
                }
                break

        return local_plan_data

    def _extract_policies_from_crawl(self, crawl_result: Dict) -> Dict:
        """Extract policies from crawl results"""

        policy_data = {'spds': [], 'policy_areas': []}

        if not crawl_result or 'data' not in crawl_result:
            return policy_data

        for page in crawl_result.get('data', []):
            url = page.get('url', '')
            markdown = page.get('markdown', '')
            metadata = page.get('metadata', {})

            if any(keyword in url.lower() for keyword in ['spd', 'supplementary', 'policy']):
                # Extract SPDs from links
                links = page.get('links', [])
                for link in links:
                    if any(k in link.lower() for k in ['spd', 'supplementary', 'guidance']):
                        policy_data['spds'].append({
                            'title': metadata.get('title', link.split('/')[-1]),
                            'url': link
                        })

        return policy_data

    def _extract_committee_from_crawl(self, crawl_result: Dict) -> Dict:
        """Extract committee info from crawl results"""

        committee_data = {}

        if not crawl_result or 'data' not in crawl_result:
            return committee_data

        for page in crawl_result.get('data', []):
            url = page.get('url', '')
            markdown = page.get('markdown', '')
            metadata = page.get('metadata', {})

            if any(keyword in url.lower() for keyword in ['committee', 'meeting', 'agenda']):
                committee_data = {
                    'url': url,
                    'content': markdown[:500],
                    'scraped_at': datetime.now().isoformat()
                }
                break

        return committee_data

    def _parse_news_from_markdown(self, news_page: Optional[Dict]) -> List[Dict]:
        """Parse news items from markdown content"""

        if not news_page or not news_page.get('markdown'):
            return []

        markdown = news_page['markdown']
        news_items = []

        # Simple markdown parsing - Firecrawl provides clean markdown
        lines = markdown.split('\n')
        current_item = {}

        for line in lines:
            line = line.strip()

            # Detect headings as news titles
            if line.startswith('##') or line.startswith('###'):
                if current_item and current_item.get('title'):
                    news_items.append(current_item)
                current_item = {
                    'title': line.lstrip('#').strip(),
                    'summary': '',
                    'url': news_page.get('url', ''),
                    'source': 'firecrawl'
                }

            # Collect paragraph text as summary
            elif line and not line.startswith('#') and current_item:
                if 'summary' in current_item:
                    current_item['summary'] += ' ' + line

        if current_item and current_item.get('title'):
            news_items.append(current_item)

        # Clean up summaries
        for item in news_items:
            if 'summary' in item:
                item['summary'] = item['summary'][:300].strip()

        return news_items[:10]

    def _parse_local_plan_from_markdown(self, plan_page: Optional[Dict]) -> Dict:
        """Parse local plan from markdown"""

        if not plan_page or not plan_page.get('markdown'):
            return {}

        return {
            'summary': plan_page['markdown'][:1000],
            'url': plan_page.get('url', ''),
            'documents': [],  # Would need to extract from links
            'scraped_at': datetime.now().isoformat()
        }

    def _parse_policies_from_markdown(self, policy_page: Optional[Dict]) -> Dict:
        """Parse policies from markdown"""

        if not policy_page or not policy_page.get('markdown'):
            return {'spds': [], 'policy_areas': []}

        # Extract links for SPDs
        spds = []
        for link in policy_page.get('links', []):
            if any(k in link.lower() for k in ['spd', 'supplementary', 'policy']):
                spds.append({
                    'title': link.split('/')[-1],
                    'url': link
                })

        return {
            'spds': spds[:15],
            'policy_areas': []
        }

    def _parse_committee_from_markdown(self, committee_page: Optional[Dict]) -> Dict:
        """Parse committee info from markdown"""

        if not committee_page or not committee_page.get('markdown'):
            return {}

        return {
            'content': committee_page['markdown'][:500],
            'url': committee_page.get('url', ''),
            'scraped_at': datetime.now().isoformat()
        }

    def estimate_cost(self, num_pages: int = 50) -> float:
        """Estimate scraping cost"""

        # Firecrawl pricing (approximate)
        scrape_cost_per_1000 = 1.0  # $1 per 1000 pages
        crawl_cost_per_1000 = 3.0   # $3 per 1000 pages

        # We use crawl mode
        cost = (num_pages / 1000) * crawl_cost_per_1000

        return cost


# Utility function for testing
async def test_firecrawl_scraper():
    """Test Firecrawl scraper"""

    test_authority = {
        'id': 'birmingham',
        'name': 'Birmingham City Council',
        'website_url': 'https://www.birmingham.gov.uk'
    }

    scraper = FirecrawlScraper(test_authority)

    print(f"Estimated cost: ${scraper.estimate_cost(50):.4f}")

    results = await scraper.scrape_authority()

    print(f"\nScraped {len(results.get('news', []))} news items")
    print(f"Local plan: {bool(results.get('local_plan'))}")
    print(f"Policies: {len(results.get('policies', {}).get('spds', []))} SPDs")
    print(f"Committee: {bool(results.get('committee'))}")

    return results


if __name__ == "__main__":
    asyncio.run(test_firecrawl_scraper())
