"""
Elasticsearch Data Extraction Pipeline for pSEO
Extracts all metrics, trends, and chart data for authority pages
"""

from typing import Dict, List, Optional
from elasticsearch import AsyncElasticsearch
from datetime import datetime, timedelta
import numpy as np
import asyncio


class DataPipeline:
    """
    Extract comprehensive planning data from Elasticsearch.
    Generates all metrics, trends, and visualization data for pSEO pages.
    """

    def __init__(self, es_client: AsyncElasticsearch, authority_id: str):
        self.es = es_client
        self.authority_id = authority_id
        self.data: Dict = {}

    async def extract_all_data(self, authority: Dict) -> Dict:
        """
        Extract all data needed for pSEO page.
        Runs all extractions in parallel for efficiency.
        """

        # Run all extractions in parallel
        results = await asyncio.gather(
            self.extract_core_metrics(),
            self.extract_time_series_trends(),
            self.extract_top_agents_developers(),
            self.extract_geographic_distribution(),
            self.extract_notable_applications(),
            self.extract_comparative_data(authority.get('region', 'UK')),
            self.extract_chart_data(),
            return_exceptions=True
        )

        # Combine results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error in extraction {i}: {result}")

        return self.data

    async def extract_core_metrics(self) -> Dict:
        """Extract key performance metrics"""

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"local_authority_id": self.authority_id}},
                        {"range": {"date_received": {"gte": f"{datetime.now().year}-01-01"}}}
                    ]
                }
            },
            "aggs": {
                "total_apps": {"value_count": {"field": "application_id.keyword"}},
                "decisions": {
                    "filters": {
                        "filters": {
                            "approved": {"term": {"decision": "approved"}},
                            "refused": {"term": {"decision": "refused"}},
                            "withdrawn": {"term": {"decision": "withdrawn"}}
                        }
                    }
                },
                "avg_decision_days": {"avg": {"field": "decision_days"}},
                "median_decision_days": {
                    "percentiles": {"field": "decision_days", "percents": [50]}
                },
                "active_applications": {
                    "filter": {"term": {"status": "pending"}}
                },
                "by_type": {
                    "terms": {"field": "application_type.keyword", "size": 20},
                    "aggs": {
                        "approved": {"filter": {"term": {"decision": "approved"}}},
                        "avg_days": {"avg": {"field": "decision_days"}}
                    }
                }
            },
            "size": 0
        }

        result = await self.es.search(index="planning_applications", body=query)
        aggs = result['aggregations']

        total = aggs['total_apps']['value']
        decisions = aggs['decisions']['buckets']

        self.data['core_metrics'] = {
            "total_applications_ytd": int(total),
            "total_approved": decisions['approved']['doc_count'],
            "total_refused": decisions['refused']['doc_count'],
            "total_withdrawn": decisions['withdrawn']['doc_count'],
            "approval_rate": (decisions['approved']['doc_count'] / total * 100) if total > 0 else 0,
            "refusal_rate": (decisions['refused']['doc_count'] / total * 100) if total > 0 else 0,
            "avg_decision_days": round(aggs['avg_decision_days']['value'], 1) if aggs['avg_decision_days']['value'] else 0,
            "median_decision_days": round(aggs['median_decision_days']['values']['50.0'], 1),
            "active_applications": aggs['active_applications']['doc_count'],
            "by_type": [
                {
                    "type": bucket['key'],
                    "count": bucket['doc_count'],
                    "approval_rate": (bucket['approved']['doc_count'] / bucket['doc_count'] * 100) if bucket['doc_count'] > 0 else 0,
                    "avg_decision_days": round(bucket['avg_days']['value'], 1) if bucket['avg_days']['value'] else 0
                }
                for bucket in aggs['by_type']['buckets']
            ]
        }

        return self.data['core_metrics']

    async def extract_time_series_trends(self) -> Dict:
        """Extract monthly trends for 24-month period"""

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"local_authority_id": self.authority_id}},
                        {"range": {"date_received": {"gte": "now-24M/M"}}}
                    ]
                }
            },
            "aggs": {
                "monthly_trends": {
                    "date_histogram": {
                        "field": "date_received",
                        "calendar_interval": "month",
                        "format": "yyyy-MM"
                    },
                    "aggs": {
                        "approved": {"filter": {"term": {"decision": "approved"}}},
                        "refused": {"filter": {"term": {"decision": "refused"}}},
                        "avg_decision_days": {"avg": {"field": "decision_days"}},
                        "major_apps": {"filter": {"term": {"application_type.keyword": "major"}}}
                    }
                }
            },
            "size": 0
        }

        result = await self.es.search(index="planning_applications", body=query)
        buckets = result['aggregations']['monthly_trends']['buckets']

        # Calculate YoY change
        current_year_volume = sum(b['doc_count'] for b in buckets[-12:])
        previous_year_volume = sum(b['doc_count'] for b in buckets[-24:-12]) if len(buckets) >= 24 else current_year_volume
        yoy_change = ((current_year_volume - previous_year_volume) / previous_year_volume * 100) if previous_year_volume > 0 else 0

        self.data['trends'] = {
            "monthly_data": [
                {
                    "month": bucket['key_as_string'],
                    "total_applications": bucket['doc_count'],
                    "approved": bucket['approved']['doc_count'],
                    "refused": bucket['refused']['doc_count'],
                    "approval_rate": (bucket['approved']['doc_count'] / bucket['doc_count'] * 100) if bucket['doc_count'] > 0 else 0,
                    "avg_decision_days": round(bucket['avg_decision_days']['value'], 1) if bucket['avg_decision_days']['value'] else 0,
                    "major_applications": bucket['major_apps']['doc_count']
                }
                for bucket in buckets
            ],
            "yoy_change": round(yoy_change, 1),
            "trend_direction": "increasing" if yoy_change > 5 else "decreasing" if yoy_change < -5 else "stable"
        }

        return self.data['trends']

    async def extract_top_agents_developers(self) -> Dict:
        """Extract performance data for top agents and developers"""

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"local_authority_id": self.authority_id}},
                        {"range": {"date_received": {"gte": "now-12M"}}}
                    ]
                }
            },
            "aggs": {
                "top_agents": {
                    "terms": {"field": "agent_name.keyword", "size": 25},
                    "aggs": {
                        "approved": {"filter": {"term": {"decision": "approved"}}},
                        "avg_decision_days": {"avg": {"field": "decision_days"}},
                        "major_apps": {"filter": {"term": {"application_type.keyword": "major"}}},
                        "application_types": {
                            "terms": {"field": "application_type.keyword", "size": 5}
                        }
                    }
                },
                "top_applicants": {
                    "terms": {"field": "applicant_name.keyword", "size": 25},
                    "aggs": {
                        "approved": {"filter": {"term": {"decision": "approved"}}},
                        "total_dwellings": {"sum": {"field": "num_dwellings"}},
                        "total_floorspace": {"sum": {"field": "floorspace_sqm"}}
                    }
                }
            },
            "size": 0
        }

        result = await self.es.search(index="planning_applications", body=query)

        self.data['top_entities'] = {
            "agents": [
                {
                    "name": bucket['key'],
                    "applications": bucket['doc_count'],
                    "approval_rate": round((bucket['approved']['doc_count'] / bucket['doc_count'] * 100), 1),
                    "avg_decision_days": round(bucket['avg_decision_days']['value'], 1) if bucket['avg_decision_days']['value'] else 0,
                    "major_applications": bucket['major_apps']['doc_count'],
                    "specializations": [t['key'] for t in bucket['application_types']['buckets'][:3]]
                }
                for bucket in result['aggregations']['top_agents']['buckets']
                if bucket['doc_count'] >= 3
            ][:15],

            "developers": [
                {
                    "name": bucket['key'],
                    "applications": bucket['doc_count'],
                    "approval_rate": round((bucket['approved']['doc_count'] / bucket['doc_count'] * 100), 1),
                    "total_dwellings": int(bucket['total_dwellings']['value']) if bucket['total_dwellings']['value'] else 0,
                    "total_floorspace": int(bucket['total_floorspace']['value']) if bucket['total_floorspace']['value'] else 0
                }
                for bucket in result['aggregations']['top_applicants']['buckets']
                if bucket['doc_count'] >= 2
            ][:15]
        }

        return self.data['top_entities']

    async def extract_geographic_distribution(self) -> Dict:
        """Extract ward/geographic analysis"""

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"local_authority_id": self.authority_id}},
                        {"range": {"date_received": {"gte": "now-12M"}}},
                        {"exists": {"field": "ward"}}
                    ]
                }
            },
            "aggs": {
                "by_ward": {
                    "terms": {"field": "ward.keyword", "size": 100},
                    "aggs": {
                        "approved": {"filter": {"term": {"decision": "approved"}}},
                        "major_apps": {"filter": {"term": {"application_type.keyword": "major"}}},
                        "avg_decision_days": {"avg": {"field": "decision_days"}},
                        "dwellings": {"sum": {"field": "num_dwellings"}},
                        "centroid": {
                            "geo_centroid": {"field": "location"}
                        }
                    }
                }
            },
            "size": 0
        }

        result = await self.es.search(index="planning_applications", body=query)
        ward_buckets = result['aggregations']['by_ward']['buckets']

        # Identify hotspots (top 25% activity)
        volumes = [b['doc_count'] for b in ward_buckets]
        hotspot_threshold = np.percentile(volumes, 75) if volumes else 0

        self.data['geographic'] = {
            "wards": [
                {
                    "ward": bucket['key'],
                    "applications": bucket['doc_count'],
                    "approved": bucket['approved']['doc_count'],
                    "approval_rate": round((bucket['approved']['doc_count'] / bucket['doc_count'] * 100), 1),
                    "major_applications": bucket['major_apps']['doc_count'],
                    "avg_decision_days": round(bucket['avg_decision_days']['value'], 1) if bucket['avg_decision_days']['value'] else 0,
                    "total_dwellings": int(bucket['dwellings']['value']) if bucket['dwellings']['value'] else 0,
                    "is_hotspot": bucket['doc_count'] >= hotspot_threshold,
                    "lat": bucket['centroid']['location']['lat'] if bucket.get('centroid', {}).get('location') else None,
                    "lng": bucket['centroid']['location']['lon'] if bucket.get('centroid', {}).get('location') else None
                }
                for bucket in ward_buckets
            ]
        }

        return self.data['geographic']

    async def extract_notable_applications(self) -> List[Dict]:
        """Extract major and notable applications"""

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"local_authority_id": self.authority_id}},
                        {"range": {"decision_date": {"gte": "now-12M"}}}
                    ],
                    "should": [
                        {"term": {"application_type.keyword": "major"}},
                        {"range": {"num_dwellings": {"gte": 10}}},
                        {"range": {"floorspace_sqm": {"gte": 1000}}},
                        {"term": {"committee_decision": True}},
                        {"range": {"num_objections": {"gte": 10}}}
                    ],
                    "minimum_should_match": 1
                }
            },
            "sort": [
                {"decision_date": {"order": "desc"}},
                {"num_dwellings": {"order": "desc"}}
            ],
            "size": 25
        }

        result = await self.es.search(index="planning_applications", body=query)

        self.data['notable_applications'] = [
            {
                "reference": hit['_source'].get('application_reference'),
                "address": hit['_source'].get('site_address'),
                "description": hit['_source'].get('development_description'),
                "applicant": hit['_source'].get('applicant_name'),
                "agent": hit['_source'].get('agent_name'),
                "decision": hit['_source'].get('decision'),
                "decision_date": hit['_source'].get('decision_date'),
                "decision_route": "Committee" if hit['_source'].get('committee_decision') else "Delegated",
                "dwellings": hit['_source'].get('num_dwellings', 0),
                "floorspace": hit['_source'].get('floorspace_sqm', 0),
                "public_engagement": {
                    "objections": hit['_source'].get('num_objections', 0),
                    "supports": hit['_source'].get('num_supports', 0),
                    "comments": hit['_source'].get('num_comments', 0)
                },
                "ward": hit['_source'].get('ward'),
                "application_type": hit['_source'].get('application_type')
            }
            for hit in result['hits']['hits']
        ]

        return self.data['notable_applications']

    async def extract_comparative_data(self, region: str) -> Dict:
        """Extract regional and national comparative metrics"""

        # Regional comparison
        regional_query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"region.keyword": region}},
                        {"range": {"date_received": {"gte": "now-12M"}}}
                    ]
                }
            },
            "aggs": {
                "by_authority": {
                    "terms": {"field": "local_authority_id.keyword", "size": 100},
                    "aggs": {
                        "approved": {"filter": {"term": {"decision": "approved"}}},
                        "avg_decision_days": {"avg": {"field": "decision_days"}}
                    }
                }
            },
            "size": 0
        }

        regional_result = await self.es.search(index="planning_applications", body=regional_query)

        # National benchmarks
        national_query = {
            "query": {
                "range": {"date_received": {"gte": "now-12M"}}
            },
            "aggs": {
                "national_approval": {
                    "filters": {
                        "filters": {
                            "approved": {"term": {"decision": "approved"}},
                            "total": {"match_all": {}}
                        }
                    }
                },
                "decision_days_percentiles": {
                    "percentiles": {"field": "decision_days", "percents": [25, 50, 75, 90]}
                }
            },
            "size": 0
        }

        national_result = await self.es.search(index="planning_applications", body=national_query)

        # Calculate rankings
        regional_authorities = regional_result['aggregations']['by_authority']['buckets']
        regional_authorities_sorted = sorted(
            regional_authorities,
            key=lambda x: (x['approved']['doc_count'] / x['doc_count']) if x['doc_count'] > 0 else 0,
            reverse=True
        )

        authority_rank = next(
            (i+1 for i, auth in enumerate(regional_authorities_sorted) if auth['key'] == self.authority_id),
            None
        )

        self.data['comparative'] = {
            "regional": {
                "total_authorities": len(regional_authorities),
                "authority_rank": authority_rank,
                "regional_avg_approval": round(
                    sum((b['approved']['doc_count'] / b['doc_count']) for b in regional_authorities if b['doc_count'] > 0) /
                    len([b for b in regional_authorities if b['doc_count'] > 0]) * 100, 1
                ) if regional_authorities else 0,
                "regional_avg_days": round(
                    sum(b['avg_decision_days']['value'] for b in regional_authorities if b['avg_decision_days']['value']) /
                    len([b for b in regional_authorities if b['avg_decision_days']['value']]), 1
                ) if regional_authorities else 0,
                "top_performers": [
                    {
                        "authority_id": auth['key'],
                        "approval_rate": round((auth['approved']['doc_count'] / auth['doc_count'] * 100), 1),
                        "applications": auth['doc_count']
                    }
                    for auth in regional_authorities_sorted[:5]
                ]
            },
            "national": {
                "national_median_approval": round(
                    (national_result['aggregations']['national_approval']['buckets']['approved']['doc_count'] /
                     national_result['aggregations']['national_approval']['buckets']['total']['doc_count'] * 100), 1
                ),
                "decision_days_benchmarks": {
                    "p25": round(national_result['aggregations']['decision_days_percentiles']['values']['25.0'], 1),
                    "p50": round(national_result['aggregations']['decision_days_percentiles']['values']['50.0'], 1),
                    "p75": round(national_result['aggregations']['decision_days_percentiles']['values']['75.0'], 1),
                    "p90": round(national_result['aggregations']['decision_days_percentiles']['values']['90.0'], 1)
                }
            }
        }

        return self.data['comparative']

    async def extract_chart_data(self) -> Dict:
        """Extract all chart visualization data"""

        self.data['charts'] = {
            "volume_trends": await self._extract_volume_trends_chart(),
            "decision_timeline": await self._extract_decision_timeline_chart(),
            "distribution": await self._extract_distribution_chart(),
            "geographic_heatmap": await self._extract_geographic_heatmap()
        }

        return self.data['charts']

    async def _extract_volume_trends_chart(self) -> Dict:
        """Data for volume trends bar chart"""

        monthly_data = self.data.get('trends', {}).get('monthly_data', [])
        if not monthly_data:
            await self.extract_time_series_trends()
            monthly_data = self.data['trends']['monthly_data']

        # Find peak month
        peak_volume = max(m['total_applications'] for m in monthly_data) if monthly_data else 0

        return {
            'type': 'bar-chart',
            'title': 'Planning Application Volume Trends (Last 12 Months)',
            'data': [
                {
                    'month': m['month'][-2:] if '-' in m['month'] else m['month'],  # Format to 'Jan', 'Feb', etc.
                    'total_applications': m['total_applications'],
                    'approved': m['approved'],
                    'refused': m['refused'],
                    'peak': m['total_applications'] == peak_volume
                }
                for m in monthly_data[-12:]
            ],
            'comparison': {
                'approved': sum(m['approved'] for m in monthly_data[-12:]),
                'peak_month': next((m['month'] for m in monthly_data if m['total_applications'] == peak_volume), 'Unknown'),
                'average_monthly': round(sum(m['total_applications'] for m in monthly_data[-12:]) / 12, 1)
            }
        }

    async def _extract_decision_timeline_chart(self) -> Dict:
        """Data for decision timeline horizontal bar chart"""

        by_type = self.data.get('core_metrics', {}).get('by_type', [])

        colors = {
            'Householder': '#10b981',
            'Full Planning': '#059669',
            'Reserved Matters': '#047857',
            'Prior Approval': '#065f46',
            'default': '#0d9488'
        }

        return {
            'type': 'horizontal-bar-chart',
            'title': 'Average Decision Timeline by Application Type',
            'data': [
                {
                    'application_type': t['type'],
                    'avg_decision_days': round(t['avg_decision_days'], 0),
                    'color': colors.get(t['type'], colors['default'])
                }
                for t in by_type[:10]
            ],
            'note': 'Average processing times based on historical data. Actual timelines may vary by authority.'
        }

    async def _extract_distribution_chart(self) -> Dict:
        """Data for application distribution donut chart"""

        by_type = self.data.get('core_metrics', {}).get('by_type', [])
        total = sum(t['count'] for t in by_type)

        type_colors = {
            'Householder': '#10b981',
            'Full Planning': '#3b82f6',
            'Outline': '#8b5cf6',
            'Change of Use': '#f59e0b',
            'Reserved Matters': '#ef4444',
            'default': '#6b7280'
        }

        return {
            'type': 'donut-chart',
            'title': 'Application Type Distribution',
            'total_applications': total,
            'data': [
                {
                    'type': t['type'],
                    'count': t['count'],
                    'percentage': round((t['count'] / total * 100), 1),
                    'color': type_colors.get(t['type'], type_colors['default']),
                    'approval_rate': t['approval_rate']
                }
                for t in by_type
            ]
        }

    async def _extract_geographic_heatmap(self) -> Dict:
        """Data for geographic heat map"""

        wards = self.data.get('geographic', {}).get('wards', [])
        max_count = max(w['applications'] for w in wards) if wards else 1

        return {
            'type': 'heat-map',
            'title': 'Planning Application Heat Map',
            'data': [
                {
                    'ward_name': w['ward'],
                    'lat': w['lat'],
                    'lng': w['lng'],
                    'application_count': w['applications'],
                    'approval_rate': w['approval_rate'],
                    'intensity': int((w['applications'] / max_count) * 100)
                }
                for w in wards if w['lat'] and w['lng']
            ],
            'legend': {
                'min': 0,
                'max': max_count,
                'colors': ['#dbeafe', '#93c5fd', '#3b82f6', '#1e40af', '#1e3a8a']
            }
        }


# Utility function for testing
async def test_data_pipeline():
    """Test data pipeline"""
    from elasticsearch import AsyncElasticsearch

    es = AsyncElasticsearch(["http://localhost:9200"])

    pipeline = DataPipeline(es, "test-authority-001")

    test_authority = {
        'id': 'test-authority-001',
        'name': 'Test Council',
        'region': 'Test Region'
    }

    print("Extracting all data...")
    data = await pipeline.extract_all_data(test_authority)

    print(f"\n✓ Core metrics: {bool(data.get('core_metrics'))}")
    print(f"✓ Trends: {bool(data.get('trends'))}")
    print(f"✓ Top entities: {bool(data.get('top_entities'))}")
    print(f"✓ Geographic: {bool(data.get('geographic'))}")
    print(f"✓ Notable apps: {len(data.get('notable_applications', []))}")
    print(f"✓ Comparative: {bool(data.get('comparative'))}")
    print(f"✓ Charts: {bool(data.get('charts'))}")

    await es.close()


if __name__ == "__main__":
    asyncio.run(test_data_pipeline())
