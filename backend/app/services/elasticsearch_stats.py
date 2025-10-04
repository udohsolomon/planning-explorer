"""
Elasticsearch statistics queries for Content Discovery pages
Phase 1 Week 1 - Elasticsearch Architect deliverables
"""
from typing import List, Tuple, Optional, Dict
from cachetools import TTLCache
import hashlib
import json
import logging
from app.db.elasticsearch import es_client

logger = logging.getLogger(__name__)

# In-memory cache with 1-hour TTL
stats_cache = TTLCache(maxsize=1000, ttl=3600)  # 1000 entries, 1 hour TTL


def get_cache_key(query_type: str, **params) -> str:
    """Generate cache key from query parameters"""
    key_data = f"{query_type}:{json.dumps(params, sort_keys=True)}"
    return hashlib.md5(key_data.encode()).hexdigest()


# ============================================================================
# Platform Overview Statistics (Homepage Stats Bar)
# ============================================================================

async def get_platform_overview_stats_cached(force_refresh: bool = False) -> dict:
    """
    Get platform-wide statistics for homepage stats bar with YoY comparisons

    **Performance:** < 200ms (cached), < 500ms (ES query)
    **Cache TTL:** 1 hour

    Returns:
        dict: Platform statistics including:
            - totalApplications: Total count of all applications
            - totalDecisions: Count of applications with decisions
            - totalGranted: Count of granted/approved applications
            - totalHousingUnits: Estimated housing units (placeholder)
            - grantedPercentage: Percentage of decisions that were granted
            - applicationsYoY: YoY % change in applications
            - decisionsYoY: YoY % change in decisions
            - housingUnitsYoY: YoY % change in housing units
    """
    cache_key = get_cache_key("platform_overview")

    # Check cache
    if not force_refresh and cache_key in stats_cache:
        logger.info("Returning cached platform overview stats")
        return stats_cache[cache_key]

    logger.info("Fetching fresh platform overview stats from Elasticsearch")

    try:
        # Define date ranges for YoY comparison
        # Current year: Oct 2024 - Sept 2025
        current_year_start = "2024-10-01"
        current_year_end = "2025-09-30"

        # Previous year: Oct 2023 - Sept 2024
        previous_year_start = "2023-10-01"
        previous_year_end = "2024-09-30"

        # 1. Total Applications (all time)
        total_applications = await es_client.count(index="planning_applications")
        logger.info(f"Total applications: {total_applications}")

        # 2. Total Decisions (has decided_date)
        total_decisions = await es_client.count(
            index="planning_applications",
            query={
                "bool": {
                    "should": [
                        {"exists": {"field": "decided_date"}},
                        {"exists": {"field": "decision_date"}}
                    ],
                    "minimum_should_match": 1
                }
            }
        )
        logger.info(f"Total decisions: {total_decisions}")

        # 3. Total Granted (app_state = Permitted or Conditions)
        total_granted = await es_client.count(
            index="planning_applications",
            query={
                "bool": {
                    "should": [
                        {"term": {"app_state.keyword": "Permitted"}},
                        {"term": {"app_state.keyword": "Conditions"}},
                        {"term": {"decision.keyword": "Granted"}},
                        {"term": {"decision.keyword": "Approved"}},
                        {"term": {"status.keyword": "Approved"}}
                    ],
                    "minimum_should_match": 1
                }
            }
        )
        logger.info(f"Total granted: {total_granted}")

        # 4. Granted Percentage
        granted_percentage = round((total_granted / total_decisions * 100), 1) if total_decisions > 0 else 0

        # 5. Applications YoY
        current_apps = await es_client.count(
            index="planning_applications",
            query={
                "range": {
                    "start_date": {
                        "gte": current_year_start,
                        "lte": current_year_end
                    }
                }
            }
        )

        previous_apps = await es_client.count(
            index="planning_applications",
            query={
                "range": {
                    "start_date": {
                        "gte": previous_year_start,
                        "lte": previous_year_end
                    }
                }
            }
        )

        applications_yoy = round(
            ((current_apps - previous_apps) / previous_apps * 100) if previous_apps > 0 else 0,
            1
        )
        logger.info(f"Applications YoY: {applications_yoy}% (current: {current_apps}, previous: {previous_apps})")

        # 6. Decisions YoY
        current_decisions = await es_client.count(
            index="planning_applications",
            query={
                "bool": {
                    "must": [
                        {
                            "range": {
                                "decided_date": {
                                    "gte": current_year_start,
                                    "lte": current_year_end
                                }
                            }
                        }
                    ]
                }
            }
        )

        previous_decisions = await es_client.count(
            index="planning_applications",
            query={
                "bool": {
                    "must": [
                        {
                            "range": {
                                "decided_date": {
                                    "gte": previous_year_start,
                                    "lte": previous_year_end
                                }
                            }
                        }
                    ]
                }
            }
        )

        decisions_yoy = round(
            ((current_decisions - previous_decisions) / previous_decisions * 100) if previous_decisions > 0 else 0,
            1
        )
        logger.info(f"Decisions YoY: {decisions_yoy}% (current: {current_decisions}, previous: {previous_decisions})")

        # 7. Housing Units (placeholder - TODO: Calculate from data if housing_units field exists)
        # For now, estimate based on residential applications
        try:
            residential_count = await es_client.count(
                index="planning_applications",
                query={
                    "bool": {
                        "should": [
                            {"match": {"app_type": "residential"}},
                            {"match": {"app_type": "dwelling"}},
                            {"match": {"app_type": "house"}},
                            {"match": {"app_type": "flat"}},
                            {"match": {"description": "dwelling"}}
                        ],
                        "minimum_should_match": 1
                    }
                }
            )
            # Rough estimate: average 3.5 units per residential application
            total_housing_units = int(residential_count * 3.5)
        except Exception as e:
            logger.warning(f"Failed to estimate housing units: {e}")
            total_housing_units = 239000  # Fallback value

        # Housing units YoY (placeholder)
        housing_units_yoy = -6.0  # TODO: Calculate from actual data

        # Build response
        stats = {
            "totalApplications": total_applications,
            "totalDecisions": total_decisions,
            "totalGranted": total_granted,
            "totalHousingUnits": total_housing_units,
            "grantedPercentage": granted_percentage,
            "applicationsYoY": applications_yoy,
            "decisionsYoY": decisions_yoy,
            "housingUnitsYoY": housing_units_yoy
        }

        # Cache the result
        stats_cache[cache_key] = stats
        logger.info(f"Platform overview stats cached: {stats}")

        return stats

    except Exception as e:
        logger.error(f"Failed to fetch platform overview stats: {str(e)}", exc_info=True)
        raise


# ============================================================================
# Authority Statistics Queries
# ============================================================================

def get_authority_stats(authority_name: str, date_from: str = "now-12M/M", date_to: str = "now/M") -> dict:
    """
    Elasticsearch query for authority page statistics

    Args:
        authority_name: Authority name (e.g., "Poole") - uses area_name.keyword
        date_from: Start date (ES date math)
        date_to: End date (ES date math)

    Returns:
        dict: Aggregation query
    """
    query = {
        "query": {
            "bool": {
                "filter": [
                    {"term": {"area_name.keyword": authority_name}}
                ]
            }
        },
        "size": 0,
        "aggs": {
            # Last 12 months stats
            "last_12_months": {
                "filter": {
                    "range": {"start_date": {"gte": date_from, "lte": date_to}}
                },
                "aggs": {
                    "total": {"value_count": {"field": "uid.keyword"}},
                    "approved": {
                        "filter": {
                            "terms": {"app_state.keyword": ["Permitted", "Conditions"]}
                        },
                        "aggs": {"count": {"value_count": {"field": "uid.keyword"}}}
                    }
                }
            },

            # All-time total
            "all_time_total": {
                "value_count": {"field": "uid.keyword"}
            },

            # Active applications (no decided_date)
            "active_applications": {
                "filter": {
                    "bool": {
                        "must_not": [
                            {"exists": {"field": "decided_date"}}
                        ]
                    }
                },
                "aggs": {
                    "count": {"value_count": {"field": "uid.keyword"}}
                }
            },

            # Top app types (use as sectors for MVP)
            "top_app_types": {
                "filter": {
                    "range": {"start_date": {"gte": date_from, "lte": date_to}}
                },
                "aggs": {
                    "types": {
                        "terms": {"field": "app_type.keyword", "size": 10}
                    }
                }
            },

            # Status breakdown
            "status_breakdown": {
                "filter": {
                    "range": {"start_date": {"gte": date_from, "lte": date_to}}
                },
                "aggs": {
                    "statuses": {
                        "terms": {"field": "app_state.keyword", "size": 20}
                    }
                }
            },

            # Monthly trend
            "monthly_trend": {
                "filter": {
                    "range": {"start_date": {"gte": date_from, "lte": date_to}}
                },
                "aggs": {
                    "by_month": {
                        "date_histogram": {
                            "field": "start_date",
                            "calendar_interval": "month",
                            "min_doc_count": 0,
                            "extended_bounds": {
                                "min": date_from,
                                "max": date_to
                            },
                            "format": "yyyy-MM"
                        },
                        "aggs": {
                            "total": {"value_count": {"field": "uid.keyword"}},
                            "permitted": {
                                "filter": {"terms": {"app_state.keyword": ["Permitted", "Conditions"]}}
                            },
                            "rejected": {
                                "filter": {"term": {"app_state.keyword": "Rejected"}}
                            },
                            "pending": {
                                "filter": {"terms": {"app_state.keyword": ["Undecided", "Unresolved", "Referred"]}}
                            }
                        }
                    }
                }
            },

            # Average decision days (using new decision_days field from ingest pipeline)
            "avg_decision_days": {
                "filter": {
                    "bool": {
                        "must": [
                            {"range": {"start_date": {"gte": date_from, "lte": date_to}}},
                            {"exists": {"field": "decision_days"}}
                        ]
                    }
                },
                "aggs": {
                    "avg_days": {
                        "avg": {"field": "decision_days"}
                    }
                }
            }
        }
    }

    return query


def parse_authority_stats(es_response: dict, authority_name: str) -> dict:
    """
    Parse Elasticsearch aggregation response into API response format

    Args:
        es_response: Raw ES aggregation response
        authority_name: Authority name for response

    Returns:
        dict: Formatted statistics for API
    """
    aggs = es_response['aggregations']

    # Calculate approval rate
    last_12 = aggs['last_12_months']
    total_last_12 = last_12['total']['value']
    approved_last_12 = last_12['approved']['doc_count']
    approval_rate = (approved_last_12 / total_last_12 * 100) if total_last_12 > 0 else 0

    # Parse monthly trend
    monthly_buckets = aggs['monthly_trend']['by_month']['buckets']
    monthly_trend = [
        {
            "month": bucket['key_as_string'],
            "total": bucket['doc_count'],
            "permitted": bucket['permitted']['doc_count'],
            "rejected": bucket['rejected']['doc_count'],
            "pending": bucket['pending']['doc_count']
        }
        for bucket in monthly_buckets
    ]

    # Parse top app types (sectors)
    top_sectors = [
        {
            "sector": bucket['key'],
            "count": bucket['doc_count'],
            "percentage": round(bucket['doc_count'] / total_last_12 * 100, 1) if total_last_12 > 0 else 0
        }
        for bucket in aggs['top_app_types']['types']['buckets'][:3]  # Top 3
    ]

    # Parse status breakdown
    status_breakdown = {
        bucket['key']: bucket['doc_count']
        for bucket in aggs['status_breakdown']['statuses']['buckets']
    }

    # Get average decision days
    avg_decision_days_val = aggs['avg_decision_days']['avg_days'].get('value')

    return {
        "authority_name": authority_name,
        "total_applications_12m": int(total_last_12),
        "total_applications_all_time": int(aggs['all_time_total']['value']),
        "approval_rate": round(approval_rate, 1),
        "avg_decision_days": round(avg_decision_days_val, 0) if avg_decision_days_val else 0,
        "active_applications": int(aggs['active_applications']['count']['value']),
        "top_sectors": top_sectors,
        "status_breakdown": status_breakdown,
        "monthly_trend": monthly_trend
    }


async def get_authority_stats_cached(
    authority_name: str,
    date_from: str = "now-12M/M",
    date_to: str = "now/M",
    force_refresh: bool = False
) -> dict:
    """
    Cached authority stats query

    Args:
        authority_name: Authority name
        date_from: Start date
        date_to: End date
        force_refresh: Skip cache if True

    Returns:
        dict: Authority statistics
    """
    cache_key = get_cache_key("authority_stats", authority=authority_name, date_from=date_from, date_to=date_to)

    # Check cache
    if not force_refresh and cache_key in stats_cache:
        return stats_cache[cache_key]

    # Execute ES query
    query = get_authority_stats(authority_name, date_from, date_to)
    es_response = await es_client.client.search(
        index="planning_applications",
        body=query,
        request_cache=True
    )

    # Parse and cache
    stats = parse_authority_stats(es_response, authority_name)
    stats_cache[cache_key] = stats

    return stats


# ============================================================================
# Location Statistics Queries
# ============================================================================

def get_location_stats(
    location_slug: str,
    boundary_geojson: dict,
    centroid: Tuple[float, float],
    date_from: str = "now-12M/M",
    date_to: str = "now/M"
) -> dict:
    """
    Elasticsearch query for location page statistics with geospatial filtering

    Args:
        location_slug: URL-safe location identifier (e.g., "manchester", "mk1-2ab")
        boundary_geojson: GeoJSON polygon for location boundary
        centroid: Location center coordinates (lat, lon) for distance sorting
        date_from: Start date (ES date math)
        date_to: End date (ES date math)

    Returns:
        dict: Aggregation results for location statistics
    """
    query = {
        "query": {
            "bool": {
                "filter": [
                    {
                        # Use geo_polygon with existing 'location' field
                        "geo_polygon": {
                            "location": {
                                "points": [
                                    {"lat": p[1], "lon": p[0]}
                                    for p in boundary_geojson['coordinates'][0]
                                ]
                            }
                        }
                    }
                ]
            }
        },
        "size": 0,
        "aggs": {
            # This year total and stats
            "this_year": {
                "filter": {
                    "range": {"start_date": {"gte": date_from, "lte": date_to}}
                },
                "aggs": {
                    "total": {"value_count": {"field": "uid.keyword"}},
                    "avg_decision_days": {"avg": {"field": "decision_days"}},
                    "approved": {
                        "filter": {"terms": {"app_state.keyword": ["Permitted", "Conditions"]}},
                        "aggs": {"count": {"value_count": {"field": "uid.keyword"}}}
                    }
                }
            },

            # All-time total
            "all_time_total": {
                "value_count": {"field": "uid.keyword"}
            },

            # Top sectors
            "top_sectors": {
                "filter": {
                    "range": {"start_date": {"gte": date_from, "lte": date_to}}
                },
                "aggs": {
                    "sectors": {
                        "terms": {"field": "app_type.keyword", "size": 10}
                    }
                }
            },

            # Authority coverage (for multi-authority locations)
            "authority_coverage": {
                "terms": {"field": "area_name.keyword", "size": 10},
                "aggs": {
                    "avg_decision_days": {"avg": {"field": "decision_days"}},
                    "approved": {
                        "filter": {"terms": {"app_state.keyword": ["Permitted", "Conditions"]}}
                    }
                }
            },

            # Monthly trend
            "monthly_trend": {
                "filter": {
                    "range": {"start_date": {"gte": date_from, "lte": date_to}}
                },
                "aggs": {
                    "by_month": {
                        "date_histogram": {
                            "field": "start_date",
                            "calendar_interval": "month",
                            "min_doc_count": 0,
                            "extended_bounds": {
                                "min": date_from,
                                "max": date_to
                            },
                            "format": "yyyy-MM"
                        },
                        "aggs": {
                            "total": {"value_count": {"field": "uid.keyword"}},
                            "approved": {"filter": {"terms": {"app_state.keyword": ["Permitted", "Conditions"]}}},
                            "pending": {"filter": {"terms": {"app_state.keyword": ["Undecided", "Unresolved", "Referred"]}}},
                            "rejected": {"filter": {"term": {"app_state.keyword": "Rejected"}}}
                        }
                    }
                }
            },

            # Sector distribution (full breakdown)
            "sector_distribution": {
                "filter": {
                    "range": {"start_date": {"gte": date_from, "lte": date_to}}
                },
                "aggs": {
                    "sectors": {
                        "terms": {"field": "app_type.keyword", "size": 20}
                    }
                }
            },

            # Geographic density heatmap
            "density_heatmap": {
                "geohash_grid": {
                    "field": "location",
                    "precision": 6,
                    "size": 10000
                },
                "aggs": {
                    "centroid": {
                        "geo_centroid": {"field": "location"}
                    }
                }
            },

            # Status breakdown
            "status_breakdown": {
                "filter": {
                    "range": {"start_date": {"gte": date_from, "lte": date_to}}
                },
                "aggs": {
                    "statuses": {
                        "terms": {"field": "app_state.keyword", "size": 20}
                    }
                }
            }
        }
    }

    return query


def get_location_applications_sorted_by_distance(
    location_slug: str,
    boundary_geojson: dict,
    centroid: Tuple[float, float],
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[List[str]] = None
) -> dict:
    """
    Query for location applications sorted by distance from centroid

    Args:
        location_slug: Location identifier
        boundary_geojson: GeoJSON polygon
        centroid: (lat, lon) for distance sorting
        page: Page number (1-indexed)
        page_size: Results per page
        status_filter: Optional status filter (e.g., ["Permitted", "Undecided"])

    Returns:
        dict: ES query with distance sorting
    """
    must_filters = [
        {
            "geo_polygon": {
                "location": {
                    "points": [
                        {"lat": p[1], "lon": p[0]}
                        for p in boundary_geojson['coordinates'][0]
                    ]
                }
            }
        }
    ]

    if status_filter:
        must_filters.append({"terms": {"app_state.keyword": status_filter}})

    query = {
        "query": {
            "bool": {
                "filter": must_filters
            }
        },
        "sort": [
            {
                "_geo_distance": {
                    "location": {
                        "lat": centroid[0],
                        "lon": centroid[1]
                    },
                    "order": "asc",
                    "unit": "m"
                }
            }
        ],
        "from": (page - 1) * page_size,
        "size": page_size,
        "_source": [
            "uid",
            "address",
            "app_state",
            "start_date",
            "decided_date",
            "decision_days",
            "app_type",
            "area_name",
            "location",
            "opportunity_score"
        ]
    }

    return query


def parse_location_stats(es_response: dict, location_name: str) -> dict:
    """
    Parse Elasticsearch geospatial aggregation response

    Args:
        es_response: Raw ES response
        location_name: Human-readable location name

    Returns:
        dict: Formatted location statistics
    """
    aggs = es_response['aggregations']

    # Calculate approval rate
    this_year = aggs['this_year']
    total_this_year = this_year['total']['value']
    approved_this_year = this_year['approved']['doc_count']
    approval_rate = (approved_this_year / total_this_year * 100) if total_this_year > 0 else 0

    # Parse monthly trend
    monthly_buckets = aggs['monthly_trend']['by_month']['buckets']
    monthly_trend = [
        {
            "month": bucket['key_as_string'],
            "total": bucket['doc_count'],
            "approved": bucket['approved']['doc_count'],
            "pending": bucket['pending']['doc_count'],
            "rejected": bucket['rejected']['doc_count']
        }
        for bucket in monthly_buckets
    ]

    # Parse top sectors
    top_sectors = [
        {
            "sector": bucket['key'],
            "count": bucket['doc_count'],
            "percentage": round(bucket['doc_count'] / total_this_year * 100, 1) if total_this_year > 0 else 0
        }
        for bucket in aggs['top_sectors']['sectors']['buckets'][:3]
    ]

    # Parse authority coverage
    authority_coverage = [
        {
            "authority": bucket['key'],
            "count": bucket['doc_count'],
            "avg_decision_days": round(bucket['avg_decision_days']['value'], 0) if bucket['avg_decision_days']['value'] else 0,
            "approval_rate": round(
                (bucket['approved']['doc_count'] / bucket['doc_count'] * 100) if bucket['doc_count'] > 0 else 0,
                1
            )
        }
        for bucket in aggs['authority_coverage']['buckets']
    ]

    # Parse sector distribution (for donut chart)
    sector_distribution = [
        {
            "sector": bucket['key'],
            "count": bucket['doc_count'],
            "percentage": round(bucket['doc_count'] / total_this_year * 100, 1) if total_this_year > 0 else 0
        }
        for bucket in aggs['sector_distribution']['sectors']['buckets']
    ]

    # Parse heatmap data (geohash grid)
    heatmap_data = [
        {
            "geohash": bucket['key'],
            "count": bucket['doc_count'],
            "centroid": bucket['centroid']['location']
        }
        for bucket in aggs['density_heatmap']['buckets']
    ]

    # Parse status breakdown
    status_breakdown = {
        bucket['key']: bucket['doc_count']
        for bucket in aggs['status_breakdown']['statuses']['buckets']
    }

    return {
        "location_name": location_name,
        "total_applications_this_year": int(total_this_year),
        "total_applications_all_time": int(aggs['all_time_total']['value']),
        "approval_rate": round(approval_rate, 1),
        "avg_decision_days": round(this_year['avg_decision_days']['value'], 0) if this_year['avg_decision_days']['value'] else 0,
        "top_sectors": top_sectors,
        "authority_coverage": authority_coverage,
        "multi_authority": len(authority_coverage) > 1,
        "monthly_trend": monthly_trend,
        "sector_distribution": sector_distribution,
        "status_breakdown": status_breakdown,
        "heatmap_data": heatmap_data
    }


async def get_location_stats_cached(
    location_slug: str,
    boundary_geojson: dict = None,
    centroid: Tuple[float, float] = None,
    date_from: str = "now-12M/M",
    date_to: str = "now/M",
    force_refresh: bool = False
) -> dict:
    """
    Cached location stats query

    Note: Requires boundary_geojson and centroid data from location registry

    Args:
        location_slug: Location identifier
        boundary_geojson: GeoJSON polygon boundary
        centroid: (lat, lon) center point
        date_from: Start date
        date_to: End date
        force_refresh: Skip cache if True

    Returns:
        dict: Location statistics
    """
    if not boundary_geojson or not centroid:
        raise ValueError("Location boundary data not available. Location registry required.")

    cache_key = get_cache_key(
        "location_stats",
        location=location_slug,
        date_from=date_from,
        date_to=date_to
    )

    # Check cache
    if not force_refresh and cache_key in stats_cache:
        return stats_cache[cache_key]

    # Execute ES query
    query = get_location_stats(location_slug, boundary_geojson, centroid, date_from, date_to)
    es_response = await es_client.client.search(
        index="planning_applications",
        body=query,
        request_cache=True
    )

    # Parse and cache
    location_name = location_slug.replace("-", " ").title()
    stats = parse_location_stats(es_response, location_name)
    stats_cache[cache_key] = stats

    return stats
