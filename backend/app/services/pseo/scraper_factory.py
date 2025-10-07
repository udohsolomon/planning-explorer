"""
Hybrid Scraper Factory - Intelligent Routing
Automatically chooses Playwright (FREE) or Firecrawl (PAID) based on authority complexity
"""

from typing import Dict, Optional
from .playwright_scraper import PlaywrightScraper
from .firecrawl_scraper import FirecrawlScraper


class ScraperFactory:
    """
    Factory to create appropriate scraper for each authority.
    Uses Playwright for 80% (simple sites) and Firecrawl for 20% (complex sites).
    Cost optimization: ~$2-5 total vs $100+ if using Firecrawl for all.
    """

    # Complex authorities that need Firecrawl (major cities, modern portals)
    FIRECRAWL_AUTHORITIES = {
        # Major cities with modern portals
        'birmingham', 'manchester', 'liverpool', 'leeds', 'sheffield',
        'bristol', 'newcastle', 'nottingham', 'leicester', 'coventry',
        'bradford', 'cardiff', 'edinburgh', 'glasgow', 'belfast',

        # London boroughs with complex systems
        'westminster', 'camden', 'islington', 'hackney', 'tower-hamlets',
        'southwark', 'lambeth', 'wandsworth', 'greenwich', 'lewisham',
        'brent', 'ealing', 'hounslow', 'croydon', 'bromley',

        # Known complex planning portals (React/Angular/Vue sites)
        'reading', 'milton-keynes', 'brighton-hove', 'southampton',
        'portsmouth', 'plymouth', 'derby', 'stoke-on-trent',

        # Authorities with Idox/Northgate complex systems
        'york', 'oxford', 'cambridge', 'exeter', 'norwich',
        'gloucester', 'cheltenham', 'bath-ne-somerset', 'swindon',

        # High-volume authorities with custom portals
        'barnet', 'enfield', 'haringey', 'waltham-forest', 'newham',
        'redbridge', 'havering', 'hillingdon', 'harrow', 'richmond',

        # Additional complex sites (total ~85 authorities = 20%)
        'wirral', 'sefton', 'st-helens', 'knowsley', 'salford',
        'trafford', 'stockport', 'tameside', 'oldham', 'rochdale',
        'bolton', 'bury', 'wigan', 'wolverhampton', 'walsall',
        'dudley', 'sandwell', 'solihull', 'worcester', 'warwick'
    }

    # Authority complexity characteristics
    COMPLEXITY_INDICATORS = {
        'has_react_portal': 10,
        'has_angular_portal': 10,
        'has_vue_portal': 10,
        'population_over_200k': 5,
        'population_over_500k': 8,
        'metropolitan_borough': 5,
        'london_borough': 6,
        'city_council': 4,
        'idox_system': 7,
        'northgate_system': 7,
        'custom_portal': 8,
        'js_heavy_site': 9,
        'pdf_heavy': 5,
        'frequent_updates': 4
    }

    def __init__(self):
        self.scraper_usage = {
            'playwright': 0,
            'firecrawl': 0
        }

    def create_scraper(
        self,
        authority: Dict,
        force_type: Optional[str] = None
    ):
        """
        Create appropriate scraper for authority.

        Args:
            authority: Authority metadata dict
            force_type: Force specific scraper type ('playwright' or 'firecrawl')

        Returns:
            PlaywrightScraper or FirecrawlScraper instance
        """

        if force_type:
            if force_type == 'firecrawl':
                self.scraper_usage['firecrawl'] += 1
                return FirecrawlScraper(authority)
            else:
                self.scraper_usage['playwright'] += 1
                return PlaywrightScraper(authority)

        # Intelligent routing
        if self._should_use_firecrawl(authority):
            self.scraper_usage['firecrawl'] += 1
            return FirecrawlScraper(authority)
        else:
            self.scraper_usage['playwright'] += 1
            return PlaywrightScraper(authority)

    def _should_use_firecrawl(self, authority: Dict) -> bool:
        """
        Decide whether to use Firecrawl based on authority characteristics.

        Decision factors:
        1. In predefined complex list
        2. Complexity score > threshold
        3. Known portal types
        4. Population size
        5. Authority type
        """

        # Check predefined list (fastest check)
        authority_slug = self._get_authority_slug(authority)
        if authority_slug in self.FIRECRAWL_AUTHORITIES:
            return True

        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(authority)

        # Use Firecrawl if complexity > 7 (out of 10)
        return complexity_score > 7

    def _calculate_complexity_score(self, authority: Dict) -> int:
        """Calculate complexity score (0-10) for authority"""

        score = 0

        # Check portal type
        portal_type = authority.get('portal_type', '').lower()
        if 'react' in portal_type:
            score += self.COMPLEXITY_INDICATORS['has_react_portal']
        elif 'angular' in portal_type:
            score += self.COMPLEXITY_INDICATORS['has_angular_portal']
        elif 'vue' in portal_type:
            score += self.COMPLEXITY_INDICATORS['has_vue_portal']

        # Check population
        population = authority.get('population') or 0
        if population > 500000:
            score += self.COMPLEXITY_INDICATORS['population_over_500k']
        elif population > 200000:
            score += self.COMPLEXITY_INDICATORS['population_over_200k']

        # Check authority type
        auth_type = authority.get('type', '').lower()
        if 'metropolitan' in auth_type:
            score += self.COMPLEXITY_INDICATORS['metropolitan_borough']
        elif 'london' in auth_type:
            score += self.COMPLEXITY_INDICATORS['london_borough']
        elif 'city' in auth_type:
            score += self.COMPLEXITY_INDICATORS['city_council']

        # Check planning system
        planning_system = authority.get('planning_system', '').lower()
        if 'idox' in planning_system:
            score += self.COMPLEXITY_INDICATORS['idox_system']
        elif 'northgate' in planning_system:
            score += self.COMPLEXITY_INDICATORS['northgate_system']
        elif planning_system and planning_system != 'standard':
            score += self.COMPLEXITY_INDICATORS['custom_portal']

        # Check website complexity
        if authority.get('js_heavy'):
            score += self.COMPLEXITY_INDICATORS['js_heavy_site']

        # Normalize to 0-10
        return min(score, 10)

    def _get_authority_slug(self, authority: Dict) -> str:
        """Get authority slug for lookup"""
        slug = authority.get('slug', '')
        if not slug:
            # Create slug from name
            name = authority.get('name', '').lower()
            slug = name.replace(' council', '').replace(' city', '').replace(' borough', '')
            slug = slug.replace(' ', '-').replace('&', 'and')

        return slug.lower()

    async def scrape_with_fallback(self, authority: Dict) -> Dict:
        """
        Scrape authority with automatic fallback.
        Try Playwright first, fallback to Firecrawl if it fails.
        """

        # Try Playwright first (FREE)
        try:
            playwright_scraper = PlaywrightScraper(authority)
            results = await playwright_scraper.scrape_authority()

            # Check if results are valid
            if self._validate_scrape_results(results):
                self.scraper_usage['playwright'] += 1
                return results

            # Results invalid, try Firecrawl
            print(f"Playwright results invalid for {authority['name']}, trying Firecrawl...")

        except Exception as e:
            print(f"Playwright failed for {authority['name']}: {e}, trying Firecrawl...")

        # Fallback to Firecrawl
        try:
            firecrawl_scraper = FirecrawlScraper(authority)
            results = await firecrawl_scraper.scrape_authority()
            self.scraper_usage['firecrawl'] += 1
            return results

        except Exception as e:
            print(f"Firecrawl also failed for {authority['name']}: {e}")
            return {'error': str(e)}

    def _validate_scrape_results(self, results: Dict) -> bool:
        """Validate scraped results have minimum required data"""

        if not results or 'error' in results:
            return False

        # Check for minimum content
        has_news = bool(results.get('news'))
        has_local_plan = bool(results.get('local_plan'))
        has_policies = bool(results.get('policies'))

        # At least 2 out of 3 should have data
        valid_sections = sum([has_news, has_local_plan, has_policies])

        return valid_sections >= 2

    def get_usage_stats(self) -> Dict:
        """Get scraper usage statistics"""

        total = self.scraper_usage['playwright'] + self.scraper_usage['firecrawl']

        return {
            'playwright_used': self.scraper_usage['playwright'],
            'firecrawl_used': self.scraper_usage['firecrawl'],
            'total_scraped': total,
            'playwright_percentage': round((self.scraper_usage['playwright'] / total * 100), 1) if total > 0 else 0,
            'firecrawl_percentage': round((self.scraper_usage['firecrawl'] / total * 100), 1) if total > 0 else 0,
            'estimated_cost': self._estimate_cost()
        }

    def _estimate_cost(self) -> float:
        """Estimate total scraping cost"""

        # Firecrawl pricing: ~$0.003 per crawl (50 pages)
        firecrawl_cost = self.scraper_usage['firecrawl'] * 0.003

        # Playwright is FREE
        playwright_cost = 0

        return round(firecrawl_cost, 4)

    def get_authority_scraper_recommendation(self, authority: Dict) -> Dict:
        """Get recommendation for which scraper to use"""

        complexity_score = self._calculate_complexity_score(authority)
        should_use_firecrawl = self._should_use_firecrawl(authority)
        slug = self._get_authority_slug(authority)

        return {
            'authority': authority['name'],
            'slug': slug,
            'recommended_scraper': 'firecrawl' if should_use_firecrawl else 'playwright',
            'complexity_score': complexity_score,
            'in_complex_list': slug in self.FIRECRAWL_AUTHORITIES,
            'estimated_cost': 0.003 if should_use_firecrawl else 0,
            'reason': self._get_recommendation_reason(authority, complexity_score, should_use_firecrawl)
        }

    def _get_recommendation_reason(
        self,
        authority: Dict,
        complexity_score: int,
        use_firecrawl: bool
    ) -> str:
        """Get human-readable reason for scraper choice"""

        if use_firecrawl:
            reasons = []

            slug = self._get_authority_slug(authority)
            if slug in self.FIRECRAWL_AUTHORITIES:
                reasons.append("in predefined complex authorities list")

            if complexity_score > 7:
                reasons.append(f"high complexity score ({complexity_score}/10)")

            if authority.get('portal_type'):
                reasons.append(f"modern portal ({authority['portal_type']})")

            if authority.get('population', 0) > 200000:
                reasons.append(f"large population ({authority['population']:,})")

            return "Firecrawl recommended: " + ", ".join(reasons)

        else:
            return f"Playwright suitable: simple site (complexity: {complexity_score}/10)"


# Utility function for testing
async def test_scraper_factory():
    """Test scraper factory"""

    factory = ScraperFactory()

    test_authorities = [
        {
            'name': 'Birmingham City Council',
            'slug': 'birmingham',
            'type': 'Metropolitan Borough',
            'population': 1141000,
            'portal_type': 'React',
            'website_url': 'https://www.birmingham.gov.uk'
        },
        {
            'name': 'Small District Council',
            'slug': 'small-district',
            'type': 'District Council',
            'population': 45000,
            'portal_type': 'Standard',
            'website_url': 'https://www.smalldistrict.gov.uk'
        },
        {
            'name': 'Westminster City Council',
            'slug': 'westminster',
            'type': 'London Borough',
            'population': 255000,
            'portal_type': 'Custom',
            'website_url': 'https://www.westminster.gov.uk'
        }
    ]

    for authority in test_authorities:
        recommendation = factory.get_authority_scraper_recommendation(authority)

        print(f"\n{authority['name']}:")
        print(f"  Recommended: {recommendation['recommended_scraper']}")
        print(f"  Complexity: {recommendation['complexity_score']}/10")
        print(f"  Cost: ${recommendation['estimated_cost']:.3f}")
        print(f"  Reason: {recommendation['reason']}")

    print(f"\nUsage stats: {factory.get_usage_stats()}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_scraper_factory())
