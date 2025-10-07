"""
Playwright Web Scraper for Simple Authority Websites
FREE, self-hosted scraping for 80% of authorities
"""

from typing import Dict, List, Optional
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import asyncio
from datetime import datetime
import os


class PlaywrightScraper:
    """
    Scrape authority websites using Playwright browser automation.
    Used for simple, static websites where we can define selectors.
    """

    def __init__(self, authority: Dict):
        self.authority = authority
        self.base_url = authority.get('website_url', '')
        self.scraped_content: Dict = {}

        # Browser configuration
        self.browser_config = {
            "headless": os.getenv('PSEO_PLAYWRIGHT_HEADLESS', 'true').lower() == 'true',
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        }

        # Default selectors (will try multiple)
        self.default_selectors = {
            'news': [
                'article.news-item',
                '.news-article',
                '.press-release',
                '[class*="news"]',
                'article',
                '.content-item'
            ],
            'news_title': ['h2', 'h3', '.title', '.headline', 'header'],
            'news_date': ['time', '.date', '.published', '[datetime]'],
            'news_summary': ['p', '.summary', '.excerpt', '.description'],
            'news_link': ['a'],
            'local_plan': ['.plan-summary', '#local-plan', '.local-plan-content'],
            'policy': ['.policy-document', '.spd', '.policy-area'],
            'committee': ['.committee-meeting', '.meeting', '.agenda-item']
        }

        self.timeout = int(os.getenv('PSEO_SCRAPING_TIMEOUT', '30000'))

    async def scrape_authority(self) -> Dict:
        """Main entry point - scrape all relevant pages"""

        async with async_playwright() as p:
            browser = await p.chromium.launch(**self.browser_config)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            try:
                # Scrape different sections in parallel
                results = await asyncio.gather(
                    self._scrape_news(context),
                    self._scrape_local_plan(context),
                    self._scrape_policies(context),
                    self._scrape_committee(context),
                    return_exceptions=True
                )

                self.scraped_content = {
                    'news': results[0] if not isinstance(results[0], Exception) else [],
                    'local_plan': results[1] if not isinstance(results[1], Exception) else {},
                    'policies': results[2] if not isinstance(results[2], Exception) else {},
                    'committee': results[3] if not isinstance(results[3], Exception) else {}
                }

            except Exception as e:
                print(f"Error scraping {self.authority['name']}: {e}")
                self.scraped_content = {'error': str(e)}

            finally:
                await browser.close()

        return self.scraped_content

    async def _scrape_news(self, context) -> List[Dict]:
        """Scrape planning news and press releases"""

        news_paths = [
            '/planning/news',
            '/news/planning',
            '/planning-applications/news',
            '/services/planning/latest-news',
            '/press-releases',
            '/news'
        ]

        news_items = []
        page = await context.new_page()

        for path in news_paths:
            try:
                url = f"{self.base_url}{path}"
                response = await page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')

                if response and response.status == 200:
                    # Wait for content to load
                    await page.wait_for_load_state('networkidle', timeout=5000)

                    # Try different news selectors
                    for selector in self.default_selectors['news']:
                        try:
                            items = await page.query_selector_all(selector)

                            if items and len(items) >= 3:  # Found valid news container
                                for item in items[:15]:  # Limit to 15 items
                                    news_item = await self._extract_news_item(item)
                                    if news_item and news_item.get('title'):
                                        news_items.append(news_item)

                                if news_items:
                                    break  # Found news, stop trying selectors

                        except Exception as e:
                            continue

                    if news_items:
                        break  # Found news page, stop trying paths

            except PlaywrightTimeout:
                continue
            except Exception as e:
                print(f"Error scraping news from {url}: {e}")
                continue

        await page.close()

        # Deduplicate by title
        seen_titles = set()
        unique_news = []
        for item in news_items:
            if item['title'] not in seen_titles:
                seen_titles.add(item['title'])
                unique_news.append(item)

        return unique_news[:10]  # Return top 10

    async def _extract_news_item(self, element) -> Optional[Dict]:
        """Extract news item details from DOM element"""

        try:
            # Extract title
            title = ''
            for selector in self.default_selectors['news_title']:
                title_elem = await element.query_selector(selector)
                if title_elem:
                    title = (await title_elem.inner_text()).strip()
                    if title:
                        break

            # Extract date
            date = ''
            for selector in self.default_selectors['news_date']:
                date_elem = await element.query_selector(selector)
                if date_elem:
                    date = (await date_elem.inner_text()).strip()
                    if date:
                        break

            # Extract summary
            summary = ''
            for selector in self.default_selectors['news_summary']:
                summary_elem = await element.query_selector(selector)
                if summary_elem:
                    summary = (await summary_elem.inner_text()).strip()[:300]
                    if summary:
                        break

            # Extract link
            url = ''
            link_elem = await element.query_selector('a')
            if link_elem:
                href = await link_elem.get_attribute('href')
                if href:
                    url = href if href.startswith('http') else f"{self.base_url}{href}"

            return {
                'title': title,
                'date': date,
                'summary': summary,
                'url': url,
                'source': 'authority_website',
                'scraped_at': datetime.now().isoformat()
            }

        except Exception as e:
            return None

    async def _scrape_local_plan(self, context) -> Dict:
        """Scrape local plan information"""

        plan_paths = [
            '/planning/local-plan',
            '/planning-policy/local-plan',
            '/local-development-plan',
            '/planning/policy-and-guidance/local-plan',
            '/local-plan'
        ]

        local_plan_data = {}
        page = await context.new_page()

        for path in plan_paths:
            try:
                url = f"{self.base_url}{path}"
                response = await page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')

                if response and response.status == 200:
                    await page.wait_for_load_state('networkidle', timeout=5000)

                    # Get page content
                    html = await page.content()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Extract summary
                    summary = ''
                    for selector in self.default_selectors['local_plan']:
                        elem = soup.select_one(selector)
                        if elem:
                            summary = elem.get_text(strip=True)[:1000]
                            break

                    # If no specific selector worked, try main content
                    if not summary:
                        main_content = soup.select_one('main, .main-content, #content, article')
                        if main_content:
                            paragraphs = main_content.find_all('p', limit=5)
                            summary = ' '.join([p.get_text(strip=True) for p in paragraphs])[:1000]

                    # Extract PDF documents
                    pdf_links = []
                    for link in soup.select('a[href*=".pdf"]'):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        if any(keyword in text.lower() or keyword in href.lower()
                               for keyword in ['local-plan', 'development-plan', 'adopted', 'core-strategy']):
                            pdf_links.append({
                                "title": text,
                                "url": href if href.startswith('http') else f"{self.base_url}{href}"
                            })

                    if summary or pdf_links:
                        local_plan_data = {
                            "summary": summary,
                            "url": url,
                            "documents": pdf_links[:10],
                            "scraped_at": datetime.now().isoformat()
                        }
                        break

            except PlaywrightTimeout:
                continue
            except Exception as e:
                print(f"Error scraping local plan from {url}: {e}")
                continue

        await page.close()
        return local_plan_data

    async def _scrape_policies(self, context) -> Dict:
        """Scrape planning policies and SPDs"""

        policy_paths = [
            '/planning/planning-policy',
            '/planning-policy',
            '/planning/supplementary-planning-documents',
            '/planning/policy',
            '/spd'
        ]

        policy_data = {"spds": [], "policy_areas": []}
        page = await context.new_page()

        for path in policy_paths:
            try:
                url = f"{self.base_url}{path}"
                response = await page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')

                if response and response.status == 200:
                    await page.wait_for_load_state('networkidle', timeout=5000)

                    html = await page.content()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Extract SPDs
                    for link in soup.select('a'):
                        link_text = link.get_text(strip=True).lower()
                        href = link.get('href', '')

                        if any(term in link_text for term in ['spd', 'supplementary', 'guidance', 'policy document']):
                            policy_data['spds'].append({
                                "title": link.get_text(strip=True),
                                "url": href if href.startswith('http') else f"{self.base_url}{href}"
                            })

                    # Extract policy areas
                    for heading in soup.select('h2, h3'):
                        heading_text = heading.get_text(strip=True)
                        if any(term in heading_text.lower()
                               for term in ['policy', 'housing', 'design', 'heritage', 'environment', 'transport']):
                            next_p = heading.find_next('p')
                            description = next_p.get_text(strip=True)[:250] if next_p else ''

                            policy_data['policy_areas'].append({
                                "name": heading_text,
                                "description": description
                            })

                    if policy_data['spds'] or policy_data['policy_areas']:
                        break

            except PlaywrightTimeout:
                continue
            except Exception as e:
                print(f"Error scraping policies from {url}: {e}")
                continue

        await page.close()

        # Deduplicate
        policy_data['spds'] = list({spd['title']: spd for spd in policy_data['spds']}.values())[:15]
        policy_data['policy_areas'] = list({p['name']: p for p in policy_data['policy_areas']}.values())[:15]

        return policy_data

    async def _scrape_committee(self, context) -> Dict:
        """Scrape planning committee information"""

        committee_paths = [
            '/planning/planning-committee',
            '/committees/planning',
            '/planning-committee',
            '/planning/committee-meetings'
        ]

        committee_data = {}
        page = await context.new_page()

        for path in committee_paths:
            try:
                url = f"{self.base_url}{path}"
                response = await page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')

                if response and response.status == 200:
                    await page.wait_for_load_state('networkidle', timeout=5000)

                    # Extract meeting dates
                    dates = []
                    for selector in ['.meeting-date', '.date', 'time', '[class*="date"]']:
                        date_elements = await page.query_selector_all(selector)
                        for elem in date_elements[:10]:
                            date_text = await elem.inner_text()
                            if date_text:
                                dates.append(date_text.strip())

                    # Extract agenda links
                    agenda_links = []
                    links = await page.query_selector_all('a')
                    for link in links[:20]:
                        text = await link.inner_text()
                        href = await link.get_attribute('href')
                        if text and href and ('agenda' in text.lower() or 'agenda' in href.lower()):
                            agenda_links.append({
                                "text": text.strip(),
                                "url": href if href.startswith('http') else f"{self.base_url}{href}"
                            })

                    if dates or agenda_links:
                        committee_data = {
                            "next_meeting": dates[0] if dates else '',
                            "recent_meetings": dates[:5],
                            "agenda_links": agenda_links[:5],
                            "url": url,
                            "scraped_at": datetime.now().isoformat()
                        }
                        break

            except PlaywrightTimeout:
                continue
            except Exception as e:
                print(f"Error scraping committee from {url}: {e}")
                continue

        await page.close()
        return committee_data


# Utility function for testing
async def test_playwright_scraper():
    """Test scraper on a sample authority"""

    test_authority = {
        'id': 'test-001',
        'name': 'Test Council',
        'website_url': 'https://www.testcouncil.gov.uk'
    }

    scraper = PlaywrightScraper(test_authority)
    results = await scraper.scrape_authority()

    print(f"Scraped {len(results.get('news', []))} news items")
    print(f"Local plan: {bool(results.get('local_plan'))}")
    print(f"Policies: {len(results.get('policies', {}).get('spds', []))} SPDs")
    print(f"Committee: {bool(results.get('committee'))}")

    return results


if __name__ == "__main__":
    # Test the scraper
    asyncio.run(test_playwright_scraper())
