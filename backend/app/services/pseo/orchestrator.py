"""
pSEO Orchestrator - Main Coordinator
Orchestrates all services to generate complete pSEO pages
"""

from typing import Dict, Optional
from datetime import datetime
from elasticsearch import AsyncElasticsearch
import json
import os

from .data_pipeline import DataPipeline
from .scraper_factory import ScraperFactory
from .context7_service import Context7Service
from .content_generator import ContentGenerator


class pSEOOrchestrator:
    """
    Main orchestrator that coordinates all pSEO services.
    Generates complete, SEO-optimized authority pages.
    """

    def __init__(self, es_client: AsyncElasticsearch):
        self.es = es_client
        self.scraper_factory = ScraperFactory()
        self.context7 = Context7Service()
        self.content_generator = ContentGenerator()

        # Configuration
        self.output_dir = os.getenv('PSEO_OUTPUT_DIR', './outputs/pseo')
        self.min_word_count = int(os.getenv('PSEO_MIN_WORD_COUNT', '2500'))
        self.max_word_count = int(os.getenv('PSEO_MAX_WORD_COUNT', '3500'))

    async def generate_page(
        self,
        authority: Dict,
        force_scraper: Optional[str] = None
    ) -> Dict:
        """
        Generate complete pSEO page for an authority.

        Args:
            authority: Authority metadata
            force_scraper: Force specific scraper ('playwright' or 'firecrawl')

        Returns:
            Complete page data with all sections
        """

        print(f"\n{'='*60}")
        print(f"Generating pSEO page for {authority['name']}")
        print(f"{'='*60}\n")

        page_data = {
            'authority_id': authority['id'],
            'authority_name': authority['name'],
            'url_slug': self._create_slug(authority),
            'generated_at': datetime.now().isoformat(),
            'generation_log': []
        }

        try:
            # Step 1: Extract data from Elasticsearch
            print("Step 1: Extracting planning data from Elasticsearch...")
            page_data['generation_log'].append({
                'step': 1,
                'action': 'Data extraction',
                'timestamp': datetime.now().isoformat()
            })

            data_pipeline = DataPipeline(self.es, authority['id'])
            planning_data = await data_pipeline.extract_all_data(authority)

            print(f"  ✓ Extracted core metrics: {bool(planning_data.get('core_metrics'))}")
            print(f"  ✓ Extracted trends: {bool(planning_data.get('trends'))}")
            print(f"  ✓ Extracted charts: {bool(planning_data.get('charts'))}")

            # Step 2: Scrape authority website
            print("\nStep 2: Scraping authority website...")
            page_data['generation_log'].append({
                'step': 2,
                'action': 'Web scraping',
                'timestamp': datetime.now().isoformat()
            })

            scraper = self.scraper_factory.create_scraper(authority, force_scraper)
            scraper_type = 'Firecrawl' if 'Firecrawl' in str(type(scraper)) else 'Playwright'
            print(f"  Using {scraper_type} scraper...")

            scraped_data = await scraper.scrape_authority()

            print(f"  ✓ Scraped news: {len(scraped_data.get('news', []))} items")
            print(f"  ✓ Scraped local plan: {bool(scraped_data.get('local_plan'))}")
            print(f"  ✓ Scraped policies: {len(scraped_data.get('policies', {}).get('spds', []))} SPDs")

            # Step 3: Enrich with Context7
            print("\nStep 3: Enriching with industry context...")
            page_data['generation_log'].append({
                'step': 3,
                'action': 'Context enrichment',
                'timestamp': datetime.now().isoformat()
            })

            enriched_context = await self.context7.enrich_authority_data(
                authority, scraped_data
            )

            print(f"  ✓ Added context for {len(enriched_context.get('contexts', {}))} areas")

            # Step 4: Generate AI content with Claude
            print("\nStep 4: Generating AI content with Claude...")
            page_data['generation_log'].append({
                'step': 4,
                'action': 'AI content generation',
                'timestamp': datetime.now().isoformat()
            })

            generated_content = await self.content_generator.generate_all_sections(
                authority=authority,
                metrics=planning_data['core_metrics'],
                trends=planning_data['trends'],
                scraped=scraped_data,
                external=enriched_context,
                comparative=planning_data.get('comparative')
            )

            print(f"  ✓ Generated introduction: {len(generated_content['introduction'].split())} words")
            print(f"  ✓ Generated data insights: {len(generated_content['data_insights'].split())} words")
            print(f"  ✓ Generated policy summary: {len(generated_content['policy_summary'].split())} words")
            print(f"  ✓ Generated FAQ: {len(generated_content['faq'].split())} words")

            # Step 5: Optimize for SEO
            print("\nStep 5: Optimizing for SEO...")
            page_data['generation_log'].append({
                'step': 5,
                'action': 'SEO optimization',
                'timestamp': datetime.now().isoformat()
            })

            seo_data = self._generate_seo_metadata(
                authority, planning_data['core_metrics']
            )

            print(f"  ✓ Generated meta tags")
            print(f"  ✓ Generated structured data")
            print(f"  ✓ Generated internal links")

            # Step 6: Assemble final page
            print("\nStep 6: Assembling final page...")
            page_data['generation_log'].append({
                'step': 6,
                'action': 'Page assembly',
                'timestamp': datetime.now().isoformat()
            })

            complete_page = self._assemble_page(
                authority=authority,
                planning_data=planning_data,
                scraped_data=scraped_data,
                generated_content=generated_content,
                seo_data=seo_data
            )

            # Add metadata
            word_count = self._count_total_words(generated_content)
            complete_page['metadata'] = {
                'total_words': word_count,
                'total_sections': len(complete_page['sections']),
                'total_visualizations': 8,  # We have 8 chart types
                'scraper_used': scraper_type,
                'generation_cost': generated_content.get('_metadata', {}).get('cost', 0),
                'meets_word_count': self.min_word_count <= word_count <= self.max_word_count
            }

            # Step 7: Save page
            print("\nStep 7: Saving page...")
            page_data['generation_log'].append({
                'step': 7,
                'action': 'Save page',
                'timestamp': datetime.now().isoformat()
            })

            await self._save_page(complete_page)

            print(f"\n✅ Page generated successfully!")
            print(f"   Words: {word_count}")
            print(f"   Cost: ${complete_page['metadata']['generation_cost']:.4f}")
            print(f"   Scraper: {scraper_type}")
            print(f"   URL: /planning-applications/{complete_page['url_slug']}/")

            return complete_page

        except Exception as e:
            import traceback
            print(f"\n❌ Error generating page: {e}")
            print("\nFull traceback:")
            traceback.print_exc()
            page_data['error'] = str(e)
            page_data['status'] = 'failed'
            return page_data

    def _assemble_page(
        self,
        authority: Dict,
        planning_data: Dict,
        scraped_data: Dict,
        generated_content: Dict,
        seo_data: Dict
    ) -> Dict:
        """Assemble all components into final page structure"""

        return {
            "authority_id": authority['id'],
            "authority_name": authority['name'],
            "url_slug": self._create_slug(authority),
            "generated_at": datetime.now().isoformat(),

            # SEO metadata
            "seo": seo_data,

            # Page sections
            "sections": {
                # Hero section
                "hero": {
                    "h1": f"{authority['name']} Planning Applications - Live Data & Insights",
                    "last_update": datetime.now().strftime("%B %d, %Y"),
                    "metrics": planning_data['core_metrics'],
                    "local_context": generated_content['introduction'][:300] + "..."
                },

                # Introduction
                "introduction": {
                    "h2": f"Planning Applications in {authority['name']}: Complete Guide",
                    "content": generated_content['introduction']
                },

                # Data dashboard with visualizations
                "data_dashboard": {
                    "h2": "Live Planning Data & Insights",
                    "charts": planning_data.get('charts', {}),
                    "insights": generated_content['data_insights']
                },

                # News section
                "news": {
                    "h2": f"Latest Planning News from {authority['name']}",
                    "items": scraped_data.get('news', [])[:10]
                },

                # Policy section
                "policy": {
                    "h2": "Planning Policies & Local Plan",
                    "content": generated_content.get('policy_summary', ''),
                    "local_plan": scraped_data.get('local_plan') if isinstance(scraped_data.get('local_plan'), dict) else {},
                    "documents": scraped_data.get('local_plan', {}).get('documents', []) if isinstance(scraped_data.get('local_plan'), dict) else []
                },

                # Application types
                "application_types": {
                    "h2": f"Planning Application Types in {authority['name']}",
                    "data": planning_data['core_metrics'].get('by_type', [])
                },

                # Comparative analysis
                "comparative": {
                    "h2": f"How {authority['name']} Compares",
                    "content": generated_content.get('comparative_analysis', ''),
                    "data": planning_data.get('comparative', {})
                },

                # Notable applications
                "notable_applications": {
                    "h2": "Major Recent Planning Decisions",
                    "applications": planning_data.get('notable_applications', [])[:10]
                },

                # Geographic insights
                "geographic": {
                    "h2": "Planning Hotspots & Development Zones",
                    "wards": planning_data.get('geographic', {}).get('wards', [])
                },

                # Developer/agent insights
                "developer_insights": {
                    "h2": f"Top Applicants & Agents in {authority['name']}",
                    "agents": planning_data.get('top_entities', {}).get('agents', [])[:10],
                    "developers": planning_data.get('top_entities', {}).get('developers', [])[:10]
                },

                # Future outlook
                "future_outlook": {
                    "h2": "Future Planning Landscape",
                    "content": generated_content['future_outlook']
                },

                # FAQ
                "faq": {
                    "h2": "Frequently Asked Questions",
                    "content": generated_content['faq']
                },

                # Resources
                "resources": {
                    "h2": "Useful Resources",
                    "links": self._compile_resources(authority, scraped_data)
                }
            },

            # Raw data for frontend use
            "raw_data": planning_data
        }

    def _generate_seo_metadata(self, authority: Dict, metrics: Dict) -> Dict:
        """Generate SEO metadata"""

        slug = self._create_slug(authority)

        return {
            "meta_tags": {
                "title": f"{authority['name']} Planning Applications - Live Data & Statistics | Planning Explorer",
                "description": f"Comprehensive planning data for {authority['name']}. Track {metrics.get('total_applications_ytd', 0)} applications, {metrics.get('approval_rate', 0):.0f}% approval rate, live statistics & insights. Updated daily.",
                "canonical": f"/planning-applications/{slug}/",
                "keywords": [
                    f"{authority['name']} planning applications",
                    f"planning permission {authority.get('area', authority['name'])}",
                    f"{authority.get('area', authority['name'])} development applications",
                    f"{authority['name']} planning data"
                ]
            },

            "og_tags": {
                "og:title": f"{authority['name']} Planning Applications - Live Data",
                "og:description": f"Track {metrics.get('total_applications_ytd', 0)} planning applications with {metrics.get('approval_rate', 0):.0f}% approval rate",
                "og:type": "website",
                "og:locale": "en_GB"
            },

            "structured_data": {
                "breadcrumb": {
                    "@context": "https://schema.org",
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": "/"},
                        {"@type": "ListItem", "position": 2, "name": "Planning Authorities", "item": "/planning-applications/"},
                        {"@type": "ListItem", "position": 3, "name": authority['name'], "item": f"/planning-applications/{slug}/"}
                    ]
                },
                "dataset": {
                    "@context": "https://schema.org",
                    "@type": "Dataset",
                    "name": f"{authority['name']} Planning Applications Dataset",
                    "description": f"Planning application data for {authority['name']}",
                    "url": f"/planning-applications/{slug}/"
                }
            },

            "internal_links": self._generate_internal_links(authority)
        }

    def _generate_internal_links(self, authority: Dict) -> Dict:
        """Generate internal linking structure"""

        return {
            "regional_hub": f"/planning-applications/regions/{authority.get('region', 'uk').lower().replace(' ', '-')}/",
            "national_overview": "/planning-applications/uk-overview/",
            "data_download": f"/api/reports/custom?authority={authority['id']}",
            "semantic_search": "/search/"
        }

    def _compile_resources(self, authority: Dict, scraped_data: Dict) -> list:
        """Compile resource links"""

        return [
            {"title": "Submit Planning Application", "url": f"{authority.get('website_url', '')}/planning/apply"},
            {"title": "Local Plan", "url": scraped_data.get('local_plan', {}).get('url', '')},
            {"title": "Planning Committee", "url": scraped_data.get('committee', {}).get('url', '')},
            {"title": "Download Custom Report", "url": f"/api/reports/custom?authority={authority['id']}"}
        ]

    def _create_slug(self, authority: Dict) -> str:
        """Create URL slug from authority name"""

        slug = authority.get('slug', '')
        if not slug:
            name = authority.get('name', '').lower()
            slug = name.replace(' council', '').replace(' city', '').replace(' borough', '')
            slug = slug.replace(' ', '-').replace('&', 'and')

        return slug.lower()

    def _count_total_words(self, content: Dict) -> int:
        """Count total words in generated content"""

        total = 0
        for key, value in content.items():
            if isinstance(value, str) and not key.startswith('_'):
                total += len(value.split())
        return total

    async def _save_page(self, page_data: Dict):
        """Save page to Elasticsearch and file system"""

        # Save to Elasticsearch for search (if available)
        if self.es is not None:
            try:
                await self.es.index(
                    index="pseo_pages",
                    id=page_data['authority_id'],
                    body=page_data
                )
                print(f"  ✓ Saved to Elasticsearch")
            except Exception as e:
                print(f"  ⚠ ES save failed (will save to file only): {e}")

        # Save to file system (always)
        os.makedirs(self.output_dir, exist_ok=True)
        filename = f"{self.output_dir}/{page_data['url_slug']}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Saved to file: {filename}")

    def get_generation_stats(self) -> Dict:
        """Get generation statistics"""

        return {
            "scraper_stats": self.scraper_factory.get_usage_stats(),
            "content_generator_stats": self.content_generator.get_usage_stats(),
            "context7_stats": self.context7.get_usage_stats()
        }


# CLI for testing single authority
async def main():
    """CLI for generating single authority page"""

    import argparse
    from elasticsearch import AsyncElasticsearch
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(description='Generate pSEO page for authority')
    parser.add_argument('--authority', type=str, required=True, help='Authority ID or slug')
    parser.add_argument('--scraper', type=str, choices=['playwright', 'firecrawl'], help='Force specific scraper')

    args = parser.parse_args()

    # Connect to Elasticsearch using env vars
    es_node = os.getenv('ELASTICSEARCH_NODE', 'http://localhost:9200')
    es_username = os.getenv('ELASTICSEARCH_USERNAME', 'elastic')
    es_password = os.getenv('ELASTICSEARCH_PASSWORD', '')

    es = AsyncElasticsearch(
        [es_node],
        basic_auth=(es_username, es_password),
        verify_certs=False
    )

    # Get authority data (mock for now)
    authority = {
        'id': args.authority,
        'name': args.authority.replace('-', ' ').title() + ' Council',
        'slug': args.authority,
        'type': 'District Council',
        'region': 'UK',
        'website_url': f"https://www.{args.authority}.gov.uk"
    }

    # Generate page
    orchestrator = pSEOOrchestrator(es)
    page = await orchestrator.generate_page(authority, args.scraper)

    # Print stats
    stats = orchestrator.get_generation_stats()
    print(f"\n{'='*60}")
    print("GENERATION STATISTICS")
    print(f"{'='*60}")
    print(json.dumps(stats, indent=2))

    await es.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
