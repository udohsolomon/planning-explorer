"""
Location Statistics API endpoints with geospatial queries
Planning Explorer - Geospatial Intelligence
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import Dict, Any, List
from cachetools import TTLCache
import hashlib
import json
import logging

from app.models.locations import LocationStats, LocationStatsResponse
from app.db.elasticsearch import es_client

logger = logging.getLogger(__name__)

# In-memory cache with 1-hour TTL
location_cache = TTLCache(maxsize=500, ttl=3600)  # 500 entries, 1 hour TTL

router = APIRouter(prefix="/stats/locations", tags=["location-statistics"])


# Location center point registry (expandable)
LOCATION_CENTERS = {
    "london": {"name": "London", "lat": 51.5074, "lng": -0.1278},
    "manchester": {"name": "Manchester", "lat": 53.4808, "lng": -2.2426},
    "birmingham": {"name": "Birmingham", "lat": 52.4862, "lng": -1.8904},
    "liverpool": {"name": "Liverpool", "lat": 53.4084, "lng": -2.9916},
    "bristol": {"name": "Bristol", "lat": 51.4545, "lng": -2.5879},
    "bournemouth": {"name": "Bournemouth", "lat": 50.7192, "lng": -1.8808},
    "poole": {"name": "Poole", "lat": 50.7150, "lng": -1.9872},
    "leeds": {"name": "Leeds", "lat": 53.8008, "lng": -1.5491},
    "sheffield": {"name": "Sheffield", "lat": 53.3811, "lng": -1.4701},
    "edinburgh": {"name": "Edinburgh", "lat": 55.9533, "lng": -3.1883},
    "glasgow": {"name": "Glasgow", "lat": 55.8642, "lng": -4.2518},
    "cardiff": {"name": "Cardiff", "lat": 51.4816, "lng": -3.1791},
    "newcastle": {"name": "Newcastle", "lat": 54.9783, "lng": -1.6178},
    "nottingham": {"name": "Nottingham", "lat": 52.9548, "lng": -1.1581},
    "southampton": {"name": "Southampton", "lat": 50.9097, "lng": -1.4044},
    "brighton": {"name": "Brighton", "lat": 50.8225, "lng": -0.1372},
    "oxford": {"name": "Oxford", "lat": 51.7520, "lng": -1.2577},
    "cambridge": {"name": "Cambridge", "lat": 52.2053, "lng": 0.1218},
    "bath": {"name": "Bath", "lat": 51.3811, "lng": -2.3590},
    "york": {"name": "York", "lat": 53.9600, "lng": -1.0873},
}


def get_cache_key(location_slug: str, radius_km: int, **params) -> str:
    """Generate cache key from query parameters"""
    key_data = f"location:{location_slug}:{radius_km}:{json.dumps(params, sort_keys=True)}"
    return hashlib.md5(key_data.encode()).hexdigest()


async def build_geospatial_query(
    center_lat: float,
    center_lng: float,
    radius_km: int,
    date_from: str = "now-12M/M",
    date_to: str = "now/M"
) -> Dict[str, Any]:
    """
    Build Elasticsearch geo_distance query with aggregations

    Args:
        center_lat: Center point latitude
        center_lng: Center point longitude
        radius_km: Search radius in kilometers
        date_from: Start date (ES date math)
        date_to: End date (ES date math)

    Returns:
        dict: Complete ES query with aggregations
    """
    return {
        "query": {
            "bool": {
                "filter": [
                    {
                        "geo_distance": {
                            "distance": f"{radius_km}km",
                            "location": {
                                "lat": center_lat,
                                "lon": center_lng
                            }
                        }
                    }
                ]
            }
        },
        "size": 0,  # We only need aggregations
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

            # Top app types (sectors)
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

            # Top authorities in area
            "top_authorities": {
                "filter": {
                    "range": {"start_date": {"gte": date_from, "lte": date_to}}
                },
                "aggs": {
                    "authorities": {
                        "terms": {"field": "area_name.keyword", "size": 10}
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

            # Average decision days
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
            },

            # Recent applications (sample)
            "recent_applications": {
                "filter": {
                    "range": {"start_date": {"gte": date_from, "lte": date_to}}
                },
                "aggs": {
                    "sample": {
                        "top_hits": {
                            "size": 10,
                            "_source": ["uid"],
                            "sort": [{"start_date": {"order": "desc"}}]
                        }
                    }
                }
            }
        }
    }


async def parse_geospatial_response(
    response: Dict[str, Any],
    location_name: str,
    location_slug: str,
    center_lat: float,
    center_lng: float,
    radius_km: int
) -> LocationStats:
    """
    Parse Elasticsearch response into LocationStats model

    Args:
        response: ES response
        location_name: Location name
        location_slug: Location slug
        center_lat: Center latitude
        center_lng: Center longitude
        radius_km: Search radius

    Returns:
        LocationStats: Parsed statistics
    """
    aggs = response.get("aggregations", {})

    # Last 12 months
    last_12_months = aggs.get("last_12_months", {})
    total_12m = last_12_months.get("total", {}).get("value", 0)
    approved_12m = last_12_months.get("approved", {}).get("count", {}).get("value", 0)

    # All time
    total_all_time = aggs.get("all_time_total", {}).get("value", 0)

    # Active applications
    active_apps = aggs.get("active_applications", {}).get("count", {}).get("value", 0)

    # Approval rate
    approval_rate = round((approved_12m / total_12m * 100) if total_12m > 0 else 0.0, 2)

    # Average decision days
    avg_days = int(aggs.get("avg_decision_days", {}).get("avg_days", {}).get("value", 0) or 0)

    # Top sector
    top_types = aggs.get("top_app_types", {}).get("types", {}).get("buckets", [])
    if top_types:
        top_type = top_types[0]
        top_sector = {
            "name": top_type.get("key", "Unknown"),
            "count": top_type.get("doc_count", 0),
            "percentage": round((top_type.get("doc_count", 0) / total_12m * 100) if total_12m > 0 else 0.0, 2)
        }
    else:
        top_sector = {"name": "Unknown", "count": 0, "percentage": 0.0}

    # Top authority
    top_authorities = aggs.get("top_authorities", {}).get("authorities", {}).get("buckets", [])
    if top_authorities:
        top_auth = top_authorities[0]
        top_authority = {
            "name": top_auth.get("key", "Unknown"),
            "count": top_auth.get("doc_count", 0),
            "percentage": round((top_auth.get("doc_count", 0) / total_12m * 100) if total_12m > 0 else 0.0, 2)
        }
    else:
        top_authority = {"name": "Unknown", "count": 0, "percentage": 0.0}

    # Monthly trend
    monthly_buckets = aggs.get("monthly_trend", {}).get("by_month", {}).get("buckets", [])
    monthly_trend = []
    for bucket in monthly_buckets:
        monthly_trend.append({
            "month": bucket.get("key_as_string", ""),
            "total": bucket.get("total", {}).get("value", 0),
            "approved": bucket.get("permitted", {}).get("doc_count", 0),
            "rejected": bucket.get("rejected", {}).get("doc_count", 0),
            "pending": bucket.get("pending", {}).get("doc_count", 0)
        })

    # Status breakdown
    status_buckets = aggs.get("status_breakdown", {}).get("statuses", {}).get("buckets", [])
    status_breakdown = {
        bucket.get("key", "Unknown"): bucket.get("doc_count", 0)
        for bucket in status_buckets
    }

    # Recent applications
    recent_hits = aggs.get("recent_applications", {}).get("sample", {}).get("hits", {}).get("hits", [])
    recent_applications = [hit.get("_source", {}).get("uid", "") for hit in recent_hits]

    return LocationStats(
        location_name=location_name,
        location_slug=location_slug,
        center_coords={"lat": center_lat, "lng": center_lng},
        radius_km=radius_km,
        total_applications=int(total_12m),
        total_applications_all_time=int(total_all_time),
        active_applications=int(active_apps),
        approval_rate=approval_rate,
        avg_decision_days=avg_days,
        top_sector=top_sector,
        top_authority=top_authority,
        monthly_trend=monthly_trend,
        status_breakdown=status_breakdown,
        recent_applications=recent_applications
    )


@router.get("/{location_slug}", response_model=LocationStatsResponse)
async def get_location_stats(
    location_slug: str = Path(..., description="Location slug (e.g., 'london', 'manchester')"),
    radius_km: int = Query(5, ge=1, le=50, description="Search radius in kilometers"),
    force_refresh: bool = Query(False, description="Skip cache and fetch fresh data"),
    date_from: str = Query("now-12M/M", description="Start date (ES date math)"),
    date_to: str = Query("now/M", description="End date (ES date math)")
):
    """
    Get location statistics using geospatial queries

    **Performance target:** < 200ms response time

    **Example:** `/stats/locations/london?radius_km=10`

    **Supported locations:**
    - london, manchester, birmingham, liverpool, bristol
    - bournemouth, poole, leeds, sheffield, edinburgh
    - glasgow, cardiff, newcastle, nottingham, southampton
    - brighton, oxford, cambridge, bath, york

    **Response includes:**
    - Total applications within radius (12 months + all time)
    - Active applications
    - Approval rate
    - Average decision days
    - Top sector and authority
    - Monthly trend (last 12 months)
    - Status breakdown
    - Recent application IDs
    """
    try:
        # Validate location slug
        if location_slug not in LOCATION_CENTERS:
            raise HTTPException(
                status_code=404,
                detail=f"Location '{location_slug}' not found. Available locations: {', '.join(LOCATION_CENTERS.keys())}"
            )

        # Get location details
        location = LOCATION_CENTERS[location_slug]
        location_name = location["name"]
        center_lat = location["lat"]
        center_lng = location["lng"]

        # Check cache
        cache_key = get_cache_key(location_slug, radius_km, date_from=date_from, date_to=date_to)
        if not force_refresh and cache_key in location_cache:
            logger.info(f"Cache hit for location stats: {location_slug} (radius: {radius_km}km)")
            return LocationStatsResponse(
                success=True,
                data=location_cache[cache_key],
                cached=True
            )

        # Build ES query
        query = await build_geospatial_query(
            center_lat=center_lat,
            center_lng=center_lng,
            radius_km=radius_km,
            date_from=date_from,
            date_to=date_to
        )

        # Execute query
        if not es_client.client:
            raise HTTPException(
                status_code=503,
                detail="Elasticsearch client not connected"
            )

        response = await es_client.client.search(
            index=es_client.index_name,
            body=query
        )

        # Parse response
        stats = await parse_geospatial_response(
            response=response,
            location_name=location_name,
            location_slug=location_slug,
            center_lat=center_lat,
            center_lng=center_lng,
            radius_km=radius_km
        )

        # Cache result
        location_cache[cache_key] = stats

        logger.info(
            f"Location stats query completed: {location_slug} "
            f"(radius: {radius_km}km, total: {stats.total_applications})"
        )

        return LocationStatsResponse(
            success=True,
            data=stats,
            cached=False
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch location statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch location statistics: {str(e)}"
        )


@router.get("/", response_model=Dict[str, Any])
async def list_available_locations():
    """
    List all available locations with their center coordinates

    **Example:** `/stats/locations/`

    Returns a list of all supported locations with metadata.
    """
    return {
        "success": True,
        "locations": [
            {
                "slug": slug,
                "name": data["name"],
                "center_coords": {
                    "lat": data["lat"],
                    "lng": data["lng"]
                }
            }
            for slug, data in LOCATION_CENTERS.items()
        ],
        "total_locations": len(LOCATION_CENTERS)
    }


@router.get("/health", response_model=Dict[str, Any])
async def location_stats_health_check():
    """
    Health check endpoint for location statistics service
    """
    return {
        "status": "healthy",
        "service": "location-statistics",
        "cache_size": len(location_cache),
        "cache_maxsize": location_cache.maxsize,
        "cache_ttl": location_cache.ttl,
        "available_locations": len(LOCATION_CENTERS)
    }
