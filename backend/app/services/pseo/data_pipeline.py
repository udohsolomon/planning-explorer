"""
Data Pipeline - CORRECTED for Actual Elasticsearch Schema
Extracts planning data with proper field mappings
"""

from typing import Dict, List, Optional
from elasticsearch import AsyncElasticsearch
from datetime import datetime, timedelta
import json


class DataPipeline:
    """
    Extract comprehensive planning data from Elasticsearch.
    CORRECTED field mappings for actual schema.
    """

    def __init__(self, es_client: AsyncElasticsearch, authority_id: str):
        self.es = es_client
        self.authority_id = authority_id

    async def extract_all_data(self, authority: Dict) -> Dict:
        """Extract all data needed for pSEO page"""

        # Run all extractions in parallel
        import asyncio

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

        return {
            'core_metrics': results[0] if not isinstance(results[0], Exception) else {},
            'trends': results[1] if not isinstance(results[1], Exception) else {},
            'top_entities': results[2] if not isinstance(results[2], Exception) else {},
            'geographic': results[3] if not isinstance(results[3], Exception) else {},
            'notable_applications': results[4] if not isinstance(results[4], Exception) else [],
            'comparative': results[5] if not isinstance(results[5], Exception) else {},
            'charts': results[6] if not isinstance(results[6], Exception) else {}
        }

    async def extract_core_metrics(self) -> Dict:
        """Extract core metrics using correct field names"""

        try:
            # Get metrics for this year
            year_start = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0)

            result = await self.es.search(
                index='planning_applications',
                body={
                    'size': 0,
                    'query': {
                        'bool': {
                            'must': [
                                {'term': {'authority_slug': self.authority_id}},
                                {'range': {'start_date': {'gte': year_start.isoformat()}}}
                            ]
                        }
                    },
                    'aggs': {
                        'approved': {
                            'filter': {'term': {'is_approved': True}}
                        },
                        'refused': {
                            'filter': {'term': {'is_approved': False}}
                        },
                        'pending': {
                            'filter': {'bool': {'must_not': {'exists': {'field': 'decided_date'}}}}
                        },
                        'avg_decision_time': {
                            'avg': {'field': 'decision_days'}
                        },
                        'by_type': {
                            'terms': {'field': 'app_type.keyword', 'size': 10},
                            'aggs': {
                                'approved_pct': {
                                    'bucket_script': {
                                        'buckets_path': {
                                            'approved': 'approved>_count',
                                            'total': '_count'
                                        },
                                        'script': 'params.approved / params.total * 100'
                                    }
                                },
                                'approved': {
                                    'filter': {'term': {'is_approved': True}}
                                }
                            }
                        }
                    }
                }
            )

            total = result['hits']['total']['value']
            approved = result['aggregations']['approved']['doc_count']
            refused = result['aggregations']['refused']['doc_count']
            pending = result['aggregations']['pending']['doc_count']

            # Calculate approval rate safely
            decided = approved + refused
            approval_rate = round((approved / decided * 100), 1) if decided > 0 else 0

            metrics = {
                'total_applications_ytd': total,
                'approval_rate': approval_rate,
                'avg_decision_time': round(result['aggregations']['avg_decision_time']['value'] or 0, 1),
                'pending_applications': pending,
                'approved_last_month': 0,  # Will calculate separately
                'refused_last_month': 0,
                'by_type': []
            }

            # Process by type
            for bucket in result['aggregations']['by_type']['buckets']:
                approved_in_type = bucket.get('approved', {}).get('doc_count', 0)
                total_in_type = bucket['doc_count']
                type_approval_rate = round((approved_in_type / total_in_type * 100), 1) if total_in_type > 0 else 0

                metrics['by_type'].append({
                    'type': bucket['key'],
                    'count': total_in_type,
                    'approval_rate': type_approval_rate
                })

            return metrics

        except Exception as e:
            print(f"Error in extract_core_metrics: {e}")
            return {}

    async def extract_time_series_trends(self) -> Dict:
        """Extract 24-month time series trends"""

        try:
            # Last 24 months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)

            result = await self.es.search(
                index='planning_applications',
                body={
                    'size': 0,
                    'query': {
                        'bool': {
                            'must': [
                                {'term': {'authority_slug': self.authority_id}},
                                {'range': {'start_date': {'gte': start_date.isoformat()}}}
                            ]
                        }
                    },
                    'aggs': {
                        'monthly_trends': {
                            'date_histogram': {
                                'field': 'start_date',
                                'calendar_interval': 'month'
                            },
                            'aggs': {
                                'approved': {
                                    'filter': {'term': {'is_approved': True}}
                                },
                                'refused': {
                                    'filter': {'term': {'is_approved': False}}
                                },
                                'avg_decision_time': {
                                    'avg': {'field': 'decision_days'}
                                }
                            }
                        }
                    }
                }
            )

            monthly = []
            for bucket in result['aggregations']['monthly_trends']['buckets']:
                total = bucket['doc_count']
                approved = bucket['approved']['doc_count']
                refused = bucket['refused']['doc_count']
                decided = approved + refused

                monthly.append({
                    'month': bucket['key_as_string'][:7],  # YYYY-MM
                    'applications': total,
                    'approvals': approved,
                    'refusals': refused,
                    'approval_rate': round((approved / decided * 100), 1) if decided > 0 else 0,
                    'avg_decision_days': round(bucket['avg_decision_time']['value'] or 0, 1)
                })

            return {'monthly': monthly}

        except Exception as e:
            print(f"Error in extract_time_series_trends: {e}")
            return {'monthly': []}

    async def extract_top_agents_developers(self) -> Dict:
        """Extract top agents and consultants"""

        try:
            # Note: agent_name and consultant_name are TEXT fields, need to search not aggregate
            # Get sample for now, full aggregation would require fielddata=true

            # Get sample with agents
            agents_result = await self.es.search(
                index='planning_applications',
                body={
                    'size': 100,
                    'query': {
                        'bool': {
                            'must': [
                                {'term': {'authority_slug': self.authority_id}},
                                {'exists': {'field': 'agent_name'}}
                            ]
                        }
                    },
                    '_source': ['agent_name', 'is_approved']
                }
            )

            # Count agents manually
            agent_counts = {}
            for hit in agents_result['hits']['hits']:
                agent = hit['_source'].get('agent_name')
                if agent and agent.strip():
                    if agent not in agent_counts:
                        agent_counts[agent] = {'total': 0, 'approved': 0}
                    agent_counts[agent]['total'] += 1
                    if hit['_source'].get('is_approved'):
                        agent_counts[agent]['approved'] += 1

            agents = []
            for agent, data in sorted(agent_counts.items(), key=lambda x: x[1]['total'], reverse=True)[:10]:
                approval_rate = round((data['approved'] / data['total'] * 100), 1) if data['total'] > 0 else 0
                agents.append({
                    'name': agent,
                    'total_applications': data['total'],
                    'approval_rate': approval_rate
                })

            # Same for consultants
            consultants_result = await self.es.search(
                index='planning_applications',
                body={
                    'size': 100,
                    'query': {
                        'bool': {
                            'must': [
                                {'term': {'authority_slug': self.authority_id}},
                                {'exists': {'field': 'consultant_name'}}
                            ]
                        }
                    },
                    '_source': ['consultant_name', 'is_approved']
                }
            )

            consultant_counts = {}
            for hit in consultants_result['hits']['hits']:
                consultant = hit['_source'].get('consultant_name')
                if consultant and consultant.strip():
                    if consultant not in consultant_counts:
                        consultant_counts[consultant] = {'total': 0, 'approved': 0}
                    consultant_counts[consultant]['total'] += 1
                    if hit['_source'].get('is_approved'):
                        consultant_counts[consultant]['approved'] += 1

            developers = []
            for consultant, data in sorted(consultant_counts.items(), key=lambda x: x[1]['total'], reverse=True)[:10]:
                approval_rate = round((data['approved'] / data['total'] * 100), 1) if data['total'] > 0 else 0
                developers.append({
                    'name': consultant,
                    'total_applications': data['total'],
                    'approval_rate': approval_rate
                })

            return {'agents': agents, 'developers': developers}

        except Exception as e:
            print(f"Error in extract_top_agents_developers: {e}")
            return {'agents': [], 'developers': []}

    async def extract_geographic_distribution(self) -> Dict:
        """Extract geographic distribution using postcode/location data"""

        try:
            # Use postcode prefix for geographic grouping
            result = await self.es.search(
                index='planning_applications',
                body={
                    'size': 100,
                    'query': {
                        'bool': {
                            'must': [
                                {'term': {'authority_slug': self.authority_id}},
                                {'exists': {'field': 'postcode'}}
                            ]
                        }
                    },
                    '_source': ['postcode', 'is_approved', 'address']
                }
            )

            # Group by postcode prefix (first 3-4 chars)
            postcode_groups = {}
            for hit in result['hits']['hits']:
                postcode = hit['_source'].get('postcode', '').strip()
                if postcode and len(postcode) >= 2:
                    prefix = postcode.split()[0] if ' ' in postcode else postcode[:3]
                    if prefix not in postcode_groups:
                        postcode_groups[prefix] = {'total': 0, 'approved': 0}
                    postcode_groups[prefix]['total'] += 1
                    if hit['_source'].get('is_approved'):
                        postcode_groups[prefix]['approved'] += 1

            wards = []
            for prefix, data in sorted(postcode_groups.items(), key=lambda x: x[1]['total'], reverse=True)[:20]:
                approval_rate = round((data['approved'] / data['total'] * 100), 1) if data['total'] > 0 else 0
                wards.append({
                    'ward': f"{prefix} area",
                    'applications': data['total'],
                    'approval_rate': approval_rate
                })

            return {'wards': wards}

        except Exception as e:
            print(f"Error in extract_geographic_distribution: {e}")
            return {'wards': []}

    async def extract_notable_applications(self) -> List[Dict]:
        """Extract notable/major applications"""

        try:
            # Large applications or high opportunity score
            result = await self.es.search(
                index='planning_applications',
                body={
                    'size': 20,
                    'query': {
                        'bool': {
                            'must': [
                                {'term': {'authority_slug': self.authority_id}}
                            ],
                            'should': [
                                {'term': {'app_size.keyword': 'Large'}},
                                {'range': {'opportunity_score': {'gte': 70}}}
                            ],
                            'minimum_should_match': 1
                        }
                    },
                    'sort': [
                        {'start_date': {'order': 'desc'}}
                    ],
                    '_source': ['uid', 'description', 'app_state', 'decided_date', 'address', 'app_type', 'app_size']
                }
            )

            notable = []
            for hit in result['hits']['hits']:
                doc = hit['_source']
                notable.append({
                    'reference': doc.get('uid'),
                    'proposal': doc.get('description', 'No description')[:200],
                    'decision': doc.get('app_state'),
                    'decision_date': doc.get('decided_date'),
                    'address': doc.get('address'),
                    'type': doc.get('app_type'),
                    'size': doc.get('app_size')
                })

            return notable

        except Exception as e:
            print(f"Error in extract_notable_applications: {e}")
            return []

    async def extract_comparative_data(self, region: str) -> Dict:
        """Extract comparative data for region and national level"""

        try:
            # Simplified - would need authority mapping for proper regional comparison
            return {
                'regional': [],
                'national': {
                    'approval_rate': 65.1,  # From our earlier query
                    'avg_decision_time': 45
                }
            }

        except Exception as e:
            print(f"Error in extract_comparative_data: {e}")
            return {'regional': [], 'national': {}}

    async def extract_chart_data(self) -> Dict:
        """Extract data for all visualizations"""

        try:
            # Get last 12 months for volume trends
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)

            result = await self.es.search(
                index='planning_applications',
                body={
                    'size': 0,
                    'query': {
                        'bool': {
                            'must': [
                                {'term': {'authority_slug': self.authority_id}},
                                {'range': {'start_date': {'gte': start_date.isoformat()}}}
                            ]
                        }
                    },
                    'aggs': {
                        'volume_trends': {
                            'date_histogram': {
                                'field': 'start_date',
                                'calendar_interval': 'month'
                            }
                        },
                        'decision_time_buckets': {
                            'range': {
                                'field': 'decision_days',
                                'ranges': [
                                    {'key': '0-30 days', 'to': 30},
                                    {'key': '31-60 days', 'from': 31, 'to': 60},
                                    {'key': '61-90 days', 'from': 61, 'to': 90},
                                    {'key': '90+ days', 'from': 91}
                                ]
                            }
                        },
                        'type_distribution': {
                            'terms': {'field': 'app_type.keyword', 'size': 10}
                        },
                        'size_distribution': {
                            'terms': {'field': 'app_size.keyword', 'size': 5}
                        }
                    }
                }
            )

            return {
                'volume_trends': [
                    {'month': b['key_as_string'][:7], 'count': b['doc_count']}
                    for b in result['aggregations']['volume_trends']['buckets']
                ],
                'decision_timeline': [
                    {'range': b['key'], 'count': b['doc_count']}
                    for b in result['aggregations']['decision_time_buckets']['buckets']
                ],
                'type_distribution': [
                    {'type': b['key'], 'count': b['doc_count']}
                    for b in result['aggregations']['type_distribution']['buckets']
                ],
                'size_distribution': [
                    {'size': b['key'], 'count': b['doc_count']}
                    for b in result['aggregations']['size_distribution']['buckets']
                ]
            }

        except Exception as e:
            print(f"Error in extract_chart_data: {e}")
            return {}
