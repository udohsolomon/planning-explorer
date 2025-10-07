"""
Extract Authorities from Planning Applications
Creates authority mapping from existing planning_applications data
"""

import asyncio
import json
import os
from datetime import datetime
from elasticsearch import AsyncElasticsearch
from dotenv import load_dotenv

load_dotenv()


class AuthorityExtractor:
    """Extract and map authorities from planning_applications index"""

    def __init__(self):
        self.es = None
        self.authorities = []

    async def setup(self):
        """Setup Elasticsearch connection"""
        es_node = os.getenv('ELASTICSEARCH_NODE', 'http://localhost:9200')
        es_username = os.getenv('ELASTICSEARCH_USERNAME', 'elastic')
        es_password = os.getenv('ELASTICSEARCH_PASSWORD', '')

        self.es = AsyncElasticsearch(
            [es_node],
            basic_auth=(es_username, es_password),
            verify_certs=False
        )

        # Test connection
        try:
            health = await self.es.cluster.health()
            print(f"✅ Connected to Elasticsearch: {health['cluster_name']} ({health['status']})")
        except Exception as e:
            print(f"❌ Elasticsearch connection failed: {e}")
            raise

    async def extract_authorities(self):
        """Extract unique authorities from planning_applications"""

        print(f"\n{'='*80}")
        print(f"EXTRACTING AUTHORITIES FROM PLANNING APPLICATIONS")
        print(f"{'='*80}\n")

        try:
            # Get unique authority_slug aggregation
            result = await self.es.search(
                index='planning_applications',
                body={
                    'size': 0,
                    'aggs': {
                        'authority_slugs': {
                            'terms': {
                                'field': 'authority_slug',
                                'size': 1000
                            }
                        }
                    }
                }
            )

            buckets = result['aggregations']['authority_slugs']['buckets']
            print(f"✅ Found {len(buckets)} unique authorities\n")

            # For each slug, get a sample document to extract metadata
            for i, bucket in enumerate(buckets, 1):
                slug = bucket['key']

                # Get one document for this authority to extract metadata
                doc_result = await self.es.search(
                    index='planning_applications',
                    body={
                        'size': 1,
                        'query': {
                            'term': {'authority_slug': slug}
                        },
                        'sort': [{'start_date': {'order': 'desc'}}]
                    }
                )

                if doc_result['hits']['hits']:
                    doc = doc_result['hits']['hits'][0]['_source']

                    authority = {
                        'id': slug,
                        'area_id': doc.get('area_id'),
                        'name': doc.get('area_name', slug.replace('-', ' ').title()),
                        'slug': slug,
                        'total_applications': bucket['doc_count'],
                        'latest_application': doc.get('start_date')
                    }
                else:
                    # Fallback if no document found
                    authority = {
                        'id': slug,
                        'area_id': None,
                        'name': slug.replace('-', ' ').title(),
                        'slug': slug,
                        'total_applications': bucket['doc_count'],
                        'latest_application': None
                    }

                # Infer authority type and region (basic heuristics)
                authority['type'] = self._infer_authority_type(authority['name'])
                authority['region'] = self._infer_region(authority['name'])
                authority['website_url'] = self._generate_website_url(authority['slug'])
                authority['population'] = None  # Unknown without external data

                self.authorities.append(authority)

                # Print sample
                if len(self.authorities) <= 10:
                    print(f"  {len(self.authorities)}. {authority['name']}")
                    print(f"     Slug: {authority['slug']}")
                    print(f"     Applications: {authority['total_applications']:,}")
                    print(f"     Type: {authority['type']}")
                    print()

            if len(self.authorities) > 10:
                print(f"  ... and {len(self.authorities) - 10} more authorities\n")

            return self.authorities

        except Exception as e:
            print(f"❌ Error extracting authorities: {e}")
            raise

    def _infer_authority_type(self, name: str) -> str:
        """Infer authority type from name"""
        name_lower = name.lower()

        if 'city' in name_lower:
            return 'City Council'
        elif 'borough' in name_lower:
            if 'london' in name_lower or name in self._london_boroughs():
                return 'London Borough'
            return 'Metropolitan Borough'
        elif 'county' in name_lower:
            return 'County Council'
        elif 'district' in name_lower:
            return 'District Council'
        else:
            return 'Unitary Authority'

    def _infer_region(self, name: str) -> str:
        """Infer region from authority name"""
        # London boroughs
        if name in self._london_boroughs():
            return 'London'

        # Simple mapping (would need more sophisticated mapping in production)
        name_lower = name.lower()

        regions = {
            'birmingham': 'West Midlands',
            'manchester': 'North West',
            'liverpool': 'North West',
            'leeds': 'Yorkshire',
            'sheffield': 'Yorkshire',
            'bristol': 'South West',
            'newcastle': 'North East',
            'nottingham': 'East Midlands',
            'reading': 'South East',
            'brighton': 'South East',
            'southampton': 'South East',
            'portsmouth': 'South East',
            'oxford': 'South East',
            'cambridge': 'East of England'
        }

        for keyword, region in regions.items():
            if keyword in name_lower:
                return region

        return 'UK'  # Default

    def _generate_website_url(self, slug: str) -> str:
        """Generate likely website URL"""
        return f"https://www.{slug}.gov.uk"

    def _london_boroughs(self) -> set:
        """List of London boroughs"""
        return {
            'Westminster', 'Camden', 'Islington', 'Hackney', 'Tower Hamlets',
            'Southwark', 'Lambeth', 'Wandsworth', 'Greenwich', 'Lewisham',
            'Brent', 'Ealing', 'Hounslow', 'Croydon', 'Bromley',
            'Barnet', 'Enfield', 'Haringey', 'Waltham Forest', 'Newham',
            'Redbridge', 'Havering', 'Hillingdon', 'Harrow', 'Richmond',
            'Kingston', 'Sutton', 'Merton', 'Hammersmith', 'Kensington'
        }

    async def save_authorities(self):
        """Save authorities to JSON file"""

        output_file = 'authorities.json'

        data = {
            'extracted_at': datetime.now().isoformat(),
            'total_authorities': len(self.authorities),
            'source': 'planning_applications index',
            'authorities': self.authorities
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n{'='*80}")
        print(f"✅ AUTHORITIES SAVED")
        print(f"{'='*80}")
        print(f"File: {output_file}")
        print(f"Total authorities: {len(self.authorities)}")
        print(f"\nTop 5 by application count:")

        # Sort by application count
        sorted_authorities = sorted(
            self.authorities,
            key=lambda x: x['total_applications'],
            reverse=True
        )

        for i, auth in enumerate(sorted_authorities[:5], 1):
            print(f"  {i}. {auth['name']}: {auth['total_applications']:,} applications")

        print(f"{'='*80}\n")

    async def create_es_index(self):
        """Optionally create local_authorities index in Elasticsearch"""

        print(f"\n{'='*80}")
        print(f"CREATE ELASTICSEARCH INDEX?")
        print(f"{'='*80}")
        print(f"This will create a 'local_authorities' index in Elasticsearch")
        print(f"with {len(self.authorities)} documents.\n")

        # For automated script, skip user input
        create_index = False

        if not create_index:
            print("⏭️  Skipping index creation (can be done manually later)\n")
            return

        try:
            # Create index
            await self.es.indices.create(
                index='local_authorities',
                body={
                    'mappings': {
                        'properties': {
                            'id': {'type': 'keyword'},
                            'area_id': {'type': 'long'},
                            'name': {'type': 'text', 'fields': {'keyword': {'type': 'keyword'}}},
                            'slug': {'type': 'keyword'},
                            'type': {'type': 'keyword'},
                            'region': {'type': 'keyword'},
                            'website_url': {'type': 'keyword'},
                            'population': {'type': 'long'},
                            'total_applications': {'type': 'long'},
                            'latest_application': {'type': 'date'}
                        }
                    }
                }
            )

            # Index authorities
            for authority in self.authorities:
                await self.es.index(
                    index='local_authorities',
                    id=authority['id'],
                    document=authority
                )

            print(f"✅ Created 'local_authorities' index with {len(self.authorities)} documents\n")

        except Exception as e:
            print(f"⚠️  Error creating index: {e}")
            print(f"   (Index may already exist or permissions issue)\n")

    async def cleanup(self):
        """Cleanup"""
        if self.es:
            await self.es.close()

    async def run(self):
        """Main execution"""

        try:
            await self.setup()
            await self.extract_authorities()
            await self.save_authorities()
            await self.create_es_index()

        finally:
            await self.cleanup()


async def main():
    """Entry point"""

    extractor = AuthorityExtractor()
    await extractor.run()


if __name__ == "__main__":
    asyncio.run(main())
