"""
Search service for Planning Explorer
"""
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from app.db.elasticsearch import es_client
from app.models.planning import (
    SearchRequest, SearchResponse, SearchFilters, PlanningApplicationSummary,
    PlanningApplication, ApplicationStatus, DevelopmentType, ApplicationType, DecisionType
)

logger = logging.getLogger(__name__)

# Development type mapping: Model enums -> Elasticsearch app_type values
# ES uses app_type field with values like "Full", "Outline", "Trees", "Conditions", etc.
# Our model uses semantic development types like "residential", "commercial", etc.
DEVELOPMENT_TYPE_MAPPING = {
    DevelopmentType.RESIDENTIAL: ["Full", "Outline"],  # Most residential are Full/Outline
    DevelopmentType.COMMERCIAL: ["Full", "Outline", "Advertising"],
    DevelopmentType.INDUSTRIAL: ["Full", "Outline"],
    DevelopmentType.MIXED_USE: ["Full", "Outline"],
    DevelopmentType.EXTENSION: ["Amendment", "Conditions"],  # Conditions often relate to extensions
    DevelopmentType.CHANGE_OF_USE: ["Full", "Conditions"],
    DevelopmentType.NEW_BUILD: ["Full"]
    # Note: ES also has "Other", "Trees", "Heritage", "Telecoms" - these don't map to model enums
}


class SearchService:
    """Service for handling search operations"""

    def __init__(self):
        self.default_size = 20
        self.max_size = 100

    async def search_applications(self, search_request: SearchRequest) -> SearchResponse:
        """
        Search planning applications with intelligent caching

        Args:
            search_request: Search parameters

        Returns:
            SearchResponse with results and metadata
        """
        try:
            # Generate cache key for search request
            cache_key = self._generate_search_cache_key(search_request)

            # Check cache first
            try:
                from app.services.cache_manager import cache_manager, CacheType

                cached_result = await cache_manager.get(cache_key, CacheType.SEARCH_RESULTS)
                if cached_result:
                    logger.debug(f"Search cache hit for key: {cache_key[:50]}...")
                    return cached_result
            except ImportError:
                logger.debug("Cache manager not available for search results")

            # Build Elasticsearch query
            query = await self._build_search_query(search_request)

            # Calculate pagination
            page = max(1, search_request.page)
            page_size = min(search_request.page_size, self.max_size)
            from_offset = (page - 1) * page_size

            # Build sort configuration
            sort_config = self._build_sort_config(search_request.sort_by, search_request.sort_order)

            # Execute search
            start_time = datetime.now()

            response = await es_client.search(
                query=query,
                size=page_size,
                from_=from_offset,
                sort=sort_config,
                source=self._get_source_fields(search_request.include_ai_fields)
            )

            end_time = datetime.now()
            took_ms = int((end_time - start_time).total_seconds() * 1000)

            # Process results
            results = []
            for hit in response.get("hits", {}).get("hits", []):
                source = hit["_source"]
                doc_id = hit.get("_id")

                # Convert ES fields to model fields
                mapped_data = self._map_es_to_model(source, doc_id)

                # Convert to PlanningApplicationSummary
                summary = PlanningApplicationSummary(**mapped_data)
                results.append(summary)

            # Get total count
            total = response.get("hits", {}).get("total", {})
            if isinstance(total, dict):
                total_count = total.get("value", 0)
            else:
                total_count = total

            # Build aggregations if requested
            aggregations = None
            if hasattr(search_request, 'include_aggregations') and search_request.include_aggregations:
                aggregations = await self._get_search_aggregations(query)

            search_response = SearchResponse(
                results=results,
                total=total_count,
                page=page,
                page_size=page_size,
                total_pages=(total_count + page_size - 1) // page_size if total_count > 0 else 0,
                aggregations=aggregations,
                took_ms=took_ms
            )

            # Cache search results
            try:
                from app.services.cache_manager import cache_manager, CacheType, CacheLevel

                # Determine cache TTL based on query characteristics
                ttl_hours = 6  # Default for search results
                cache_level = CacheLevel.NORMAL

                # Cache longer for simpler queries without filters
                if not search_request.filters or not search_request.query:
                    ttl_hours = 12
                    cache_level = CacheLevel.HIGH

                await cache_manager.set(
                    cache_key,
                    search_response,
                    CacheType.SEARCH_RESULTS,
                    ttl_hours=ttl_hours,
                    level=cache_level,
                    metadata={
                        "query": search_request.query or "",
                        "total_results": total_count,
                        "search_type": "standard"
                    }
                )
            except ImportError:
                pass  # Cache manager not available

            return search_response

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise

    async def semantic_search(
        self,
        query_text: str,
        filters: Optional[SearchFilters] = None,
        k: int = 50,
        num_candidates: int = 100
    ) -> SearchResponse:
        """
        Perform hybrid search combining semantic (vector) and keyword (BM25) search

        This implementation uses a hybrid approach:
        1. Semantic search via vector embeddings for conceptual matching
        2. Keyword search for exact developer/applicant name matches
        3. Field boosting to prioritize exact matches
        4. Natural language filter extraction for status and date filters

        Args:
            query_text: Natural language query
            filters: Optional search filters
            k: Number of results to return
            num_candidates: Number of candidates for vector search

        Returns:
            SearchResponse with hybrid search results
        """
        try:
            from app.services.ai_processor import ai_processor

            # Extract filters from natural language query if not provided
            if not filters:
                filters = self._extract_filters_from_query(query_text)
                logger.info(f"[SEMANTIC_SEARCH] Extracted filters from query '{query_text}':")
                if filters:
                    logger.info(f"  - statuses: {[s.value for s in filters.statuses] if filters.statuses else None}")
                    logger.info(f"  - authorities: {filters.authorities[:5] if filters.authorities else None}{'...' if filters.authorities and len(filters.authorities) > 5 else ''}")
                    logger.info(f"  - date_from: {filters.submission_date_from}")
                    logger.info(f"  - date_to: {filters.submission_date_to}")
                else:
                    logger.info(f"  - No filters extracted")
            else:
                # Merge extracted filters with provided filters
                extracted_filters = self._extract_filters_from_query(query_text)
                filters = self._merge_filters(filters, extracted_filters)
                logger.info(f"[SEMANTIC_SEARCH] Merged filters for query '{query_text}': {filters}")

            # Try to use AI processor for semantic search
            if ai_processor.embedding_service:
                # Generate embedding for query
                query_embedding = await ai_processor.embedding_service.generate_text_embedding(query_text)

                # Build hybrid search query combining KNN (semantic) + keyword search
                # This ensures we match both conceptually similar AND exact developer names

                # Add filters if provided - build filter clauses first
                filter_clauses = []
                if filters:
                    filter_clauses = await self._build_filter_query(filters)
                    logger.info(f"[SEMANTIC_SEARCH] Built {len(filter_clauses)} filter clauses")
                    for i, clause in enumerate(filter_clauses[:3]):
                        logger.debug(f"  Filter clause {i}: {clause}")

                # Build keyword query for developer/applicant matching
                # IMPORTANT: Apply filters to keyword query as well
                keyword_query = {
                    "bool": {
                        "should": [
                            # High boost for exact applicant/developer matches
                            {
                                "multi_match": {
                                    "query": query_text,
                                    "fields": [
                                        "other_fields.applicant_name^5",  # Very high boost
                                        "other_fields.agent_name^3",
                                        "other_fields.agent_company^3",
                                        "description^2",
                                        "address",
                                        "area_name"
                                    ],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            }
                        ],
                        "minimum_should_match": 1
                    }
                }

                # Add filter clauses to keyword query
                if filter_clauses:
                    keyword_query["bool"]["filter"] = filter_clauses
                    logger.info(f"[SEMANTIC_SEARCH] Applied {len(filter_clauses)} filters to keyword query")

                # Build KNN query for semantic search
                knn_query = {
                    "field": "description_embedding",
                    "query_vector": query_embedding.embedding,
                    "k": k,
                    "num_candidates": num_candidates
                }

                # Add filters to KNN if provided
                if filter_clauses:
                    knn_query["filter"] = {
                        "bool": {
                            "must": filter_clauses
                        }
                    }

                # Execute hybrid search: KNN + keyword query
                # ES will combine scores using RRF (Reciprocal Rank Fusion) or score addition
                logger.info(f"[SEMANTIC_SEARCH] Executing hybrid search:")
                logger.info(f"  - KNN candidates: {num_candidates}")
                logger.info(f"  - Results to return: {k}")
                logger.info(f"  - KNN has filters: {bool(filter_clauses)}")
                logger.info(f"  - Keyword query has filters: {'filter' in keyword_query.get('bool', {})}")
                logger.debug(f"[SEMANTIC_SEARCH] KNN query structure: {knn_query}")
                logger.debug(f"[SEMANTIC_SEARCH] Keyword query structure: {keyword_query}")

                response = await es_client.search(
                    knn=knn_query,
                    query=keyword_query,
                    size=k,
                    source=self._get_source_fields(True)
                )

                # Process results
                total_hits = response.get("hits", {}).get("total", {})
                if isinstance(total_hits, dict):
                    total_count = total_hits.get("value", 0)
                else:
                    total_count = total_hits

                logger.info(f"[SEMANTIC_SEARCH] ES returned {total_count} total matches, processing {len(response.get('hits', {}).get('hits', []))} results")

                results = []
                for i, hit in enumerate(response.get("hits", {}).get("hits", [])):
                    source = hit["_source"]
                    doc_id = hit.get("_id")

                    # Log first few results for debugging
                    if i < 3:
                        logger.debug(f"[SEMANTIC_SEARCH] Result {i+1}: ref={source.get('reference')}, status={source.get('app_state')}, authority={source.get('area_name')}, score={hit.get('_score')}")

                    # Convert ES fields to model fields
                    mapped_data = self._map_es_to_model(source, doc_id)
                    mapped_data["similarity_score"] = hit["_score"]  # Use hybrid score

                    summary = PlanningApplicationSummary(**mapped_data)
                    results.append(summary)

                total = len(results)

                return SearchResponse(
                    results=results,
                    total=total,
                    page=1,
                    page_size=k,
                    total_pages=1,
                    took_ms=50  # Placeholder
                )

            else:
                # Fallback to enhanced text search with developer field boosting
                search_request = SearchRequest(
                    query=query_text,
                    filters=filters,
                    page_size=k
                )
                return await self.search_applications(search_request)

        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            # Fallback to regular search
            search_request = SearchRequest(
                query=query_text,
                filters=filters,
                page_size=k
            )
            return await self.search_applications(search_request)

    async def get_application_by_id(self, application_id: str) -> Optional[PlanningApplication]:
        """
        Get planning application by ID

        Args:
            application_id: Application unique identifier (can be uid, name, or reference)

        Returns:
            PlanningApplication if found, None otherwise
        """
        try:
            logger.info(f"[DEBUG] get_application_by_id called with application_id: '{application_id}'")

            # First try direct document lookup by ES _id
            # This is fast but only works if application_id IS the ES document _id
            try:
                document = await es_client.get_document(application_id)
                if document:
                    logger.info(f"[DEBUG] Found application by ES _id: {application_id}")
                    # Map ES fields to model fields
                    mapped_data = self._map_es_to_model(document, application_id)
                    return PlanningApplication(**mapped_data)
            except Exception as direct_lookup_error:
                # Direct lookup failed, document _id doesn't match application_id
                # This is expected for most cases
                logger.debug(f"Direct ES _id lookup failed for {application_id}, trying field search")

            # Search for document by uid, name, or reference fields
            # This is the primary lookup method since application_id comes from these fields
            query = {
                "bool": {
                    "should": [
                        {"term": {"uid.keyword": application_id}},
                        {"term": {"name.keyword": application_id}},
                        {"term": {"reference.keyword": application_id}},
                        # Also try without .keyword for non-keyword fields
                        {"term": {"uid": application_id}},
                        {"term": {"name": application_id}},
                        {"term": {"reference": application_id}}
                    ],
                    "minimum_should_match": 1
                }
            }

            logger.info(f"[DEBUG] Executing ES query for application_id '{application_id}'")
            logger.info(f"[DEBUG] Query: {query}")

            response = await es_client.search(
                query=query,
                size=1,
                source=self._get_source_fields(True)
            )

            logger.info(f"[DEBUG] ES response: total hits = {response.get('hits', {}).get('total', {})}")

            hits = response.get("hits", {}).get("hits", [])
            if hits:
                hit = hits[0]
                source = hit["_source"]
                doc_id = hit.get("_id")

                logger.info(f"[DEBUG] Found application: ES _id={doc_id}, uid={source.get('uid')}, name={source.get('name')}, reference={source.get('reference')}")

                # Map ES fields to model fields
                mapped_data = self._map_es_to_model(source, doc_id)
                return PlanningApplication(**mapped_data)

            # No document found
            logger.warning(f"[DEBUG] Application {application_id} not found in Elasticsearch")
            return None

        except Exception as e:
            logger.error(f"[DEBUG] Failed to get application {application_id}: {str(e)}")
            import traceback
            logger.error(f"[DEBUG] Traceback: {traceback.format_exc()}")
            return None

    async def get_applications_list(
        self,
        filters: Optional[SearchFilters] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "submission_date",
        sort_order: str = "desc"
    ) -> SearchResponse:
        """
        Get list of planning applications with optional filters

        Args:
            filters: Optional search filters
            page: Page number
            page_size: Results per page
            sort_by: Sort field
            sort_order: Sort order (asc/desc)

        Returns:
            SearchResponse with applications list
        """
        search_request = SearchRequest(
            filters=filters,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )

        return await self.search_applications(search_request)

    async def get_aggregations(self, filters: Optional[SearchFilters] = None) -> Dict[str, Any]:
        """
        Get search aggregations for market intelligence

        Args:
            filters: Optional search filters

        Returns:
            Dict containing aggregation results
        """
        try:
            # Build base query
            query = {"match_all": {}}
            if filters:
                query = await self._build_filter_query(filters)

            # Define aggregations
            aggs = {
                "by_authority": {
                    "terms": {
                        "field": "authority",
                        "size": 20
                    }
                },
                "by_status": {
                    "terms": {
                        "field": "status",
                        "size": 10
                    }
                },
                "by_development_type": {
                    "terms": {
                        "field": "development_type",
                        "size": 15
                    }
                },
                "by_application_type": {
                    "terms": {
                        "field": "application_type",
                        "size": 10
                    }
                },
                "by_decision": {
                    "terms": {
                        "field": "decision",
                        "size": 5
                    }
                },
                "by_month": {
                    "date_histogram": {
                        "field": "start_date",  # Use ES field name
                        "calendar_interval": "month",
                        "format": "yyyy-MM"
                    }
                },
                "opportunity_score_stats": {
                    "stats": {
                        "field": "opportunity_score"
                    }
                },
                "approval_probability_stats": {
                    "stats": {
                        "field": "approval_probability"
                    }
                },
                "project_value_ranges": {
                    "range": {
                        "field": "project_value",
                        "ranges": [
                            {"to": 100000},
                            {"from": 100000, "to": 500000},
                            {"from": 500000, "to": 1000000},
                            {"from": 1000000, "to": 5000000},
                            {"from": 5000000}
                        ]
                    }
                }
            }

            return await es_client.aggregations(aggs, query)

        except Exception as e:
            logger.error(f"Aggregations failed: {str(e)}")
            raise

    async def _build_search_query(self, search_request: SearchRequest) -> Dict[str, Any]:
        """Build Elasticsearch query from search request"""

        # Start with base query
        if search_request.query:
            # Multi-match query across relevant fields
            query = {
                "bool": {
                    "must": [{
                        "multi_match": {
                            "query": search_request.query,
                            "fields": [
                                "description^3",
                                "address^2",
                                "area_name^1.5",
                                "app_type^1.5",
                                "other_fields.applicant_name",
                                "other_fields.agent_name",
                                "other_fields.agent_company",
                                "other_fields.development_type",
                                "postcode"
                            ],
                            "type": "best_fields",
                            "fuzziness": "AUTO"
                        }
                    }]
                }
            }
        else:
            query = {"bool": {"must": [{"match_all": {}}]}}

        # Add filters
        if search_request.filters:
            filter_query = await self._build_filter_query(search_request.filters)
            if filter_query:
                if "bool" not in query:
                    query = {"bool": {"must": [query]}}
                query["bool"]["filter"] = filter_query

        return query

    async def _build_filter_query(self, filters: SearchFilters) -> Optional[List[Dict[str, Any]]]:
        """Build filter query from search filters"""
        filter_clauses = []

        # Authority filters - use ES field "area_name"
        if filters.authorities:
            filter_clauses.append({
                "terms": {"area_name.keyword": filters.authorities}
            })

        # Status filters - use ES field "app_state" and "other_fields.decision"
        if filters.statuses:
            status_values = []
            decision_values = []

            for status in filters.statuses:
                if status.value == 'rejected':
                    status_values.extend(['Rejected', 'Refused'])
                    decision_values.extend(['Refused', 'Rejected'])
                elif status.value == 'approved':
                    # ES ground truth: "Permitted" (1.17M), "Conditions" (371K), "Granted" (rare)
                    # Removed "Decided" - does not exist in ES data
                    status_values.extend(['Permitted', 'Conditions', 'Granted'])
                    decision_values.extend(['Approved', 'Granted'])
                elif status.value == 'under_consideration':
                    # ES ground truth: "Undecided" (486K)
                    # Removed "Under Consideration" - does not exist in ES data
                    status_values.extend(['Undecided', 'Unresolved', 'Referred'])
                elif status.value == 'submitted':
                    status_values.extend(['Pending', 'Registered'])
                elif status.value == 'withdrawn':
                    status_values.append('Withdrawn')
                    decision_values.append('Withdrawn')

            if status_values or decision_values:
                status_filter = {
                    "bool": {
                        "should": []
                    }
                }

                if status_values:
                    status_filter["bool"]["should"].append({
                        "terms": {"app_state.keyword": status_values}
                    })

                if decision_values:
                    status_filter["bool"]["should"].append({
                        "terms": {"other_fields.decision.keyword": decision_values}
                    })

                filter_clauses.append(status_filter)

        # Development type filters - map model enums to ES app_type values
        if filters.development_types:
            es_app_types = []
            for dev_type in filters.development_types:
                # Map each development type enum to its corresponding ES app_type values
                mapped_values = DEVELOPMENT_TYPE_MAPPING.get(dev_type, [])
                es_app_types.extend(mapped_values)

            # Only add filter if we have mapped values
            if es_app_types:
                filter_clauses.append({
                    "terms": {"app_type.keyword": es_app_types}
                })

        # Application type filters - use ES field "app_type" or "other_fields.application_type"
        if filters.application_types:
            filter_clauses.append({
                "bool": {
                    "should": [
                        {"terms": {"app_type.keyword": [at.value for at in filters.application_types]}},
                        {"terms": {"other_fields.application_type.keyword": [at.value for at in filters.application_types]}}
                    ]
                }
            })

        # Decision filters - use ES field "other_fields.decision"
        if filters.decisions:
            decision_values = []
            for decision in filters.decisions:
                if decision.value == 'rejected':
                    decision_values.extend(['Refused', 'Rejected'])
                elif decision.value == 'approved':
                    decision_values.extend(['Approved', 'Granted'])
                elif decision.value == 'withdrawn':
                    decision_values.append('Withdrawn')

            if decision_values:
                filter_clauses.append({
                    "terms": {"other_fields.decision.keyword": decision_values}
                })

        # Date range filters - use ES field "start_date"
        if filters.submission_date_from or filters.submission_date_to:
            date_range = {}
            if filters.submission_date_from:
                date_range["gte"] = filters.submission_date_from.isoformat()
            if filters.submission_date_to:
                date_range["lte"] = filters.submission_date_to.isoformat()

            filter_clauses.append({
                "range": {"start_date": date_range}
            })

        # Decision date filters - use ES field "decided_date"
        if filters.decision_date_from or filters.decision_date_to:
            date_range = {}
            if filters.decision_date_from:
                date_range["gte"] = filters.decision_date_from.isoformat()
            if filters.decision_date_to:
                date_range["lte"] = filters.decision_date_to.isoformat()

            filter_clauses.append({
                "range": {"decided_date": date_range}
            })

        # Numeric range filters
        if filters.opportunity_score_min is not None or filters.opportunity_score_max is not None:
            score_range = {}
            if filters.opportunity_score_min is not None:
                score_range["gte"] = filters.opportunity_score_min
            if filters.opportunity_score_max is not None:
                score_range["lte"] = filters.opportunity_score_max

            filter_clauses.append({
                "range": {"opportunity_score": score_range}
            })

        if filters.approval_probability_min is not None or filters.approval_probability_max is not None:
            prob_range = {}
            if filters.approval_probability_min is not None:
                prob_range["gte"] = filters.approval_probability_min
            if filters.approval_probability_max is not None:
                prob_range["lte"] = filters.approval_probability_max

            filter_clauses.append({
                "range": {"approval_probability": prob_range}
            })

        if filters.project_value_min is not None or filters.project_value_max is not None:
            value_range = {}
            if filters.project_value_min is not None:
                value_range["gte"] = filters.project_value_min
            if filters.project_value_max is not None:
                value_range["lte"] = filters.project_value_max

            filter_clauses.append({
                "range": {"project_value": value_range}
            })

        # Geographic filters
        if filters.postcode:
            filter_clauses.append({
                "wildcard": {"postcode.keyword": f"{filters.postcode.upper()}*"}
            })

        if filters.ward:
            filter_clauses.append({
                "term": {"ward": filters.ward}
            })

        # Location radius search
        if filters.lat is not None and filters.lon is not None and filters.radius_km is not None:
            filter_clauses.append({
                "geo_distance": {
                    "distance": f"{filters.radius_km}km",
                    "location": {
                        "lat": filters.lat,
                        "lon": filters.lon
                    }
                }
            })

        return filter_clauses if filter_clauses else None

    def _build_sort_config(self, sort_by: str, sort_order: str) -> List[Dict[str, Any]]:
        """Build sort configuration"""

        sort_order = sort_order.lower() if sort_order else "desc"

        # Map sort fields (ES has start_date, not submission_date)
        sort_field_mapping = {
            "relevance": "_score",
            "submission_date": "start_date",  # Map to ES field
            "decision_date": "decided_date",  # Map to ES field
            "opportunity_score": "opportunity_score",
            "approval_probability": "approval_probability",
            "project_value": "project_value",
            "created_at": "created_at",
            "updated_at": "updated_at"
        }

        sort_field = sort_field_mapping.get(sort_by, "_score")

        if sort_field == "_score":
            return [{"_score": {"order": "desc"}}]
        else:
            return [{sort_field: {"order": sort_order, "missing": "_last"}}]

    def _get_source_fields(self, include_ai_fields: bool = True) -> List[str]:
        """Get source fields to include in response - use actual ES field names"""

        # Use actual ES field names based on what exists in the documents
        base_fields = [
            # Core identifiers
            "uid", "name", "reference", "altid", "associated_id",

            # Authority and area
            "area_id", "area_name", "scraper_name",

            # Location
            "address", "postcode", "location", "location_x", "location_y",

            # Application details
            "app_size", "app_state", "app_type",

            # Dates
            "start_date", "decided_date", "consulted_date",
            "last_changed", "last_different", "last_scraped",

            # Description and classification
            "description",

            # URLs and links
            "link", "url",

            # Nested other_fields object (ES will return entire nested object)
            "other_fields"
        ]

        if include_ai_fields:
            ai_fields = [
                "opportunity_score", "approval_probability", "ai_summary",
                "ai_confidence_score", "ai_key_points", "ai_rationale", "ai_recommendations",
                "ai_risk_factors", "ai_sentiment", "market_context"
            ]
            base_fields.extend(ai_fields)

        return base_fields

    async def _get_search_aggregations(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Get aggregations for search results"""

        aggs = {
            "authorities": {
                "terms": {"field": "authority", "size": 10}
            },
            "statuses": {
                "terms": {"field": "status", "size": 10}
            },
            "development_types": {
                "terms": {"field": "development_type", "size": 10}
            }
        }

        return await es_client.aggregations(aggs, query)

    def _generate_search_cache_key(self, search_request: SearchRequest) -> str:
        """Generate cache key for search request"""
        import hashlib
        import json

        # Create a normalized representation of the search request
        cache_data = {
            "query": search_request.query or "",
            "page": search_request.page,
            "page_size": search_request.page_size,
            "sort_by": search_request.sort_by,
            "sort_order": search_request.sort_order,
            "include_ai_fields": getattr(search_request, 'include_ai_fields', True)
        }

        # Add filters if present
        if search_request.filters:
            filters_dict = {}
            for field, value in search_request.filters.dict(exclude_none=True).items():
                if value is not None:
                    if isinstance(value, list):
                        # Convert enum values to strings for consistent hashing
                        filters_dict[field] = [str(v) for v in value]
                    else:
                        filters_dict[field] = str(value)
            cache_data["filters"] = filters_dict

        # Create hash of the normalized data
        cache_string = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()

        return f"search_{cache_hash}"

    def _map_es_to_model(self, source: Dict[str, Any], doc_id: Optional[str] = None) -> Dict[str, Any]:
        """Map Elasticsearch document fields to PlanningApplicationSummary fields

        Args:
            source: Elasticsearch document source
            doc_id: Elasticsearch document _id (used as ultimate fallback for application_id)
        """
        from app.models.planning import GeoPoint

        # Create mapped data with available fields
        mapped_data = {}

        # ===== CORE IDENTIFIERS =====
        mapped_data['application_id'] = source.get('uid') or source.get('name') or source.get('reference') or doc_id or 'unknown'
        mapped_data['reference'] = source.get('reference') or source.get('uid') or source.get('name')

        if source.get('uid'):
            mapped_data['uid'] = source.get('uid')
        if source.get('name'):
            mapped_data['name'] = source.get('name')
        if source.get('altid'):
            mapped_data['altid'] = source.get('altid')
        if source.get('associated_id'):
            mapped_data['associated_id'] = source.get('associated_id')

        # ===== AUTHORITY AND AREA =====
        mapped_data['authority'] = source.get('area_name') or source.get('scraper_name') or 'unknown'

        if source.get('area_id') is not None:
            mapped_data['area_id'] = source.get('area_id')
        if source.get('area_name'):
            mapped_data['area_name'] = source.get('area_name')
        if source.get('scraper_name'):
            mapped_data['scraper_name'] = source.get('scraper_name')

        # ===== LOCATION =====
        mapped_data['address'] = source.get('address') or 'Not specified'

        if source.get('postcode'):
            mapped_data['postcode'] = source.get('postcode')

        if source.get('location_x') is not None:
            mapped_data['location_x'] = source.get('location_x')
        if source.get('location_y') is not None:
            mapped_data['location_y'] = source.get('location_y')

        # Handle location conversion from GeoJSON to lat/lon
        location_data = source.get('location')
        if location_data and isinstance(location_data, dict):
            coordinates = location_data.get('coordinates')
            if coordinates and isinstance(coordinates, list) and len(coordinates) >= 2:
                # GeoJSON format is [longitude, latitude]
                mapped_data['location'] = GeoPoint(
                    lat=coordinates[1],
                    lon=coordinates[0]
                )

        # ===== APPLICATION DETAILS =====
        if source.get('app_size'):
            mapped_data['app_size'] = source.get('app_size')
        if source.get('app_state'):
            mapped_data['app_state'] = source.get('app_state')
        if source.get('app_type'):
            mapped_data['app_type'] = source.get('app_type')

        # ===== DATES =====
        mapped_data['description'] = source.get('description') or 'No description available'

        # Parse and map all date fields
        if source.get('start_date'):
            parsed_date = self._parse_date(source.get('start_date'))
            if parsed_date:
                mapped_data['start_date'] = parsed_date
                mapped_data['submission_date'] = parsed_date  # Alias for compatibility

        if source.get('decided_date'):
            parsed_date = self._parse_date(source.get('decided_date'))
            if parsed_date:
                mapped_data['decided_date'] = parsed_date

        if source.get('consulted_date'):
            parsed_date = self._parse_date(source.get('consulted_date'))
            if parsed_date:
                mapped_data['consulted_date'] = parsed_date

        if source.get('last_changed'):
            parsed_date = self._parse_date(source.get('last_changed'))
            if parsed_date:
                mapped_data['last_changed'] = parsed_date

        if source.get('last_different'):
            parsed_date = self._parse_date(source.get('last_different'))
            if parsed_date:
                mapped_data['last_different'] = parsed_date

        if source.get('last_scraped'):
            parsed_date = self._parse_date(source.get('last_scraped'))
            if parsed_date:
                mapped_data['last_scraped'] = parsed_date

        # ===== URLs AND LINKS =====
        if source.get('link'):
            mapped_data['link'] = source.get('link')
        if source.get('url'):
            mapped_data['url'] = source.get('url')

        # ===== OTHER_FIELDS (NESTED OBJECT) =====
        other_fields = source.get('other_fields', {})
        if other_fields and isinstance(other_fields, dict):
            # Extract all fields from other_fields nested object
            if other_fields.get('applicant_name'):
                mapped_data['applicant_name'] = other_fields.get('applicant_name')
            if other_fields.get('applicant_address'):
                mapped_data['applicant_address'] = other_fields.get('applicant_address')
            if other_fields.get('application_type'):
                # NORMALIZE application_type using comprehensive mapping
                normalized_type = self._normalize_application_type(other_fields.get('application_type'))
                if normalized_type:
                    mapped_data['application_type'] = normalized_type
                    logger.debug(f"Normalized application_type: '{other_fields.get('application_type')}' -> '{normalized_type}'")
            if other_fields.get('case_officer'):
                mapped_data['case_officer'] = other_fields.get('case_officer')
            if other_fields.get('comment_url'):
                mapped_data['comment_url'] = other_fields.get('comment_url')
            if other_fields.get('map_url'):
                mapped_data['map_url'] = other_fields.get('map_url')
            if other_fields.get('source_url'):
                mapped_data['source_url'] = other_fields.get('source_url')
            if other_fields.get('status'):
                mapped_data['status_other_fields'] = other_fields.get('status')

            # Parse dates from other_fields
            if other_fields.get('consultation_end_date'):
                parsed_date = self._parse_date(other_fields.get('consultation_end_date'))
                if parsed_date:
                    mapped_data['consultation_end_date'] = parsed_date

            if other_fields.get('date_received'):
                parsed_date = self._parse_date(other_fields.get('date_received'))
                if parsed_date:
                    mapped_data['date_received'] = parsed_date

            if other_fields.get('date_validated'):
                parsed_date = self._parse_date(other_fields.get('date_validated'))
                if parsed_date:
                    mapped_data['date_validated'] = parsed_date

            # Extract numeric fields from other_fields
            if other_fields.get('easting') is not None:
                mapped_data['easting'] = other_fields.get('easting')
            if other_fields.get('northing') is not None:
                mapped_data['northing'] = other_fields.get('northing')
            if other_fields.get('lat') is not None:
                mapped_data['lat'] = other_fields.get('lat')
            if other_fields.get('lng') is not None:
                mapped_data['lng'] = other_fields.get('lng')
            if other_fields.get('n_documents') is not None:
                mapped_data['n_documents'] = other_fields.get('n_documents')

            # ===== DECISION MAPPING FROM OTHER_FIELDS =====
            decision = other_fields.get('decision')
            if decision:
                # Map decision values to correct enum values
                decision_mapping = {
                    'Approved': 'approved',
                    'Refused': 'refused',
                    'Rejected': 'refused',
                    'Granted': 'approved',
                    'Withdrawn': 'withdrawn'
                }
                mapped_decision = decision_mapping.get(decision)
                if mapped_decision:
                    mapped_data['decision'] = mapped_decision

        # ===== STATUS MAPPING =====
        # ES uses app_state field (ES ground truth from aggregations)
        app_state = source.get('app_state')
        if app_state:
            # Map ES status values to our enum based on actual ES data
            # ES ground truth:
            #   "Permitted" (1.17M docs) → APPROVED
            #   "Undecided" (486K docs) → UNDER_CONSIDERATION
            #   "Conditions" (371K docs) → APPROVED (FIXED!)
            #   "Rejected" (184K docs) → REJECTED
            #   "Withdrawn" (103K docs) → WITHDRAWN
            status_mapping = {
                # APPROVED statuses (ES ground truth)
                'Permitted': 'approved',    # 1.17M docs
                'Conditions': 'approved',   # 371K docs (ADDED!)
                'Granted': 'approved',      # Rare

                # REJECTED statuses
                'Rejected': 'rejected',     # 184K docs
                'Refused': 'rejected',      # Alternative term

                # UNDER_CONSIDERATION statuses
                'Undecided': 'under_consideration',  # 486K docs
                'Unresolved': 'under_consideration',
                'Referred': 'under_consideration',

                # WITHDRAWN statuses
                'Withdrawn': 'withdrawn',   # 103K docs

                # Other statuses
                'Pending': 'submitted',
                'Valid': 'validated',
                'Registered': 'submitted'
            }

            mapped_status = status_mapping.get(app_state)
            if mapped_status:
                mapped_data['status'] = mapped_status

        # ===== APPLICATION TYPE FROM APP_TYPE FIELD =====
        # The ES app_type field can also contain application type info
        # Try to normalize it if other_fields.application_type is not set
        app_type = source.get('app_type')
        if app_type and not mapped_data.get('application_type'):
            normalized_app_type = self._normalize_application_type(app_type)
            if normalized_app_type:
                mapped_data['application_type'] = normalized_app_type
                logger.debug(f"Normalized app_type to application_type: '{app_type}' -> '{normalized_app_type}'")

        # ===== DEVELOPMENT TYPE MAPPING =====
        if app_type:
            # Map app_type to development_type enum values
            development_type_mapping = {
                'Full': 'residential',
                'Householder': 'extension',
                'Trees': 'extension',
                'Advertising': 'commercial',
                'Listed Building': 'change_of_use',
                'Conditions': 'change_of_use',
                'Commercial': 'commercial',
                'Industrial': 'industrial',
                'Residential': 'residential',
                'Mixed': 'mixed_use'
            }

            mapped_dev_type = development_type_mapping.get(app_type)
            if mapped_dev_type:
                mapped_data['development_type'] = mapped_dev_type
            else:
                # Default fallback
                mapped_data['development_type'] = 'residential'

        # ===== AI FIELDS =====
        if source.get('opportunity_score') is not None:
            mapped_data['opportunity_score'] = source.get('opportunity_score')
        if source.get('approval_probability') is not None:
            mapped_data['approval_probability'] = source.get('approval_probability')
        if source.get('ai_summary'):
            mapped_data['ai_summary'] = source.get('ai_summary')
        if source.get('ai_confidence_score') is not None:
            mapped_data['ai_confidence_score'] = source.get('ai_confidence_score')

        return mapped_data

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None

        try:
            # Handle various date formats
            from dateutil import parser
            return parser.parse(date_str)
        except Exception:
            try:
                # Fallback to basic ISO format
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except Exception:
                return None

    def _normalize_application_type(self, raw_type: str) -> Optional[str]:
        """
        Normalize raw application type values from Elasticsearch to ApplicationType enum values

        This handles the diverse range of UK planning application types that appear in real data
        and maps them to our standardized enum values.

        Args:
            raw_type: Raw application type string from ES data

        Returns:
            Normalized enum value or None if unmappable
        """
        if not raw_type:
            return None

        # Convert to lowercase for case-insensitive matching
        raw_lower = raw_type.lower().strip()

        # Comprehensive mapping of UK planning application types
        # Based on actual UK planning portal terminology
        type_mapping = {
            # Pre-application types
            'pre-application': 'pre_application',
            'pre application': 'pre_application',
            'preapp': 'pre_application',
            'pre-application publicly available': 'pre_application',
            'pre-application advice': 'pre_application',

            # Full applications
            'full': 'full',
            'full planning': 'full',
            'full application': 'full',
            'detailed planning': 'full',
            'full planning permission': 'full',

            # Outline applications
            'outline': 'outline',
            'outline planning': 'outline',
            'outline application': 'outline',
            'outline planning permission': 'outline',

            # Reserved matters
            'reserved matters': 'reserved_matters',
            'reserved': 'reserved_matters',
            'approval of reserved matters': 'reserved_matters',
            'matters': 'reserved_matters',

            # Householder applications
            'householder': 'householder',
            'householder application': 'householder',
            'householder planning': 'householder',
            'householder permission': 'householder',

            # Minor/Major applications
            'minor': 'minor',
            'minor application': 'minor',
            'minor development': 'minor',
            'major': 'major',
            'major application': 'major',
            'major development': 'major',

            # Listed building applications
            'listed building': 'listed_building',
            'listed building consent': 'listed_building',
            'listed building application': 'listed_building',
            'lbc': 'listed_building',

            # Conservation area
            'conservation area': 'conservation_area',
            'conservation area consent': 'conservation_area',
            'conservation': 'conservation_area',

            # Prior approval
            'prior approval': 'prior_approval',
            'prior notification': 'prior_approval',
            'notification': 'prior_approval',
            'pa': 'prior_approval',

            # Certificate of lawfulness
            'certificate of lawfulness': 'certificate_lawful',
            'certificate of lawful': 'certificate_lawful',
            'lawful development certificate': 'certificate_lawful',
            'certificate': 'certificate_lawful',
            'cld': 'certificate_lawful',
            'cle': 'certificate_lawful',
            'lawfulness': 'certificate_lawful',

            # Advertisement consent
            'advertisement': 'advertisement',
            'advertisement consent': 'advertisement',
            'advert': 'advertisement',
            'advertising': 'advertisement',

            # Discharge of conditions
            'discharge': 'discharge_conditions',
            'discharge of conditions': 'discharge_conditions',
            'conditions': 'discharge_conditions',
            'doc': 'discharge_conditions',

            # Non-material amendments
            'non-material amendment': 'non_material_amendment',
            'non material amendment': 'non_material_amendment',
            'non-material change': 'non_material_amendment',
            'non material change': 'non_material_amendment',
            'non-material change application': 'non_material_amendment',
            'non material change application': 'non_material_amendment',
            'nma': 'non_material_amendment',
            'amendment': 'non_material_amendment',
            'minor amendment': 'non_material_amendment',

            # Common variations
            'trees': 'other',
            'hedgerow': 'other',
            'works to trees': 'other',
            'tree preservation order': 'other',
            'tpo': 'other',
            'works': 'other',
            'removal': 'other',
            'variation': 'other',
            'variation of condition': 'discharge_conditions',
        }

        # Try exact match first
        if raw_lower in type_mapping:
            return type_mapping[raw_lower]

        # Try partial matching for more complex strings
        for key, value in type_mapping.items():
            if key in raw_lower or raw_lower in key:
                logger.debug(f"Mapped application type '{raw_type}' -> '{value}' via partial match on '{key}'")
                return value

        # Log unmapped types for future improvement
        logger.warning(f"Unknown application type '{raw_type}' - defaulting to 'other'")
        return 'other'

    def _extract_filters_from_query(self, query_text: str) -> Optional[SearchFilters]:
        """
        Extract filters from natural language query text

        Parses the query for:
        - Status terms (rejected, approved, pending, etc.)
        - Date/year terms (2025, 2024, last year, etc.)
        - Development type terms (residential, commercial, etc.)
        - Location terms (authorities, postcodes, cities, wards)

        Args:
            query_text: Natural language query

        Returns:
            SearchFilters object with extracted filters or None
        """
        import re
        from datetime import datetime
        from app.data.uk_authorities import (
            UK_PLANNING_AUTHORITIES, CITY_TO_AUTHORITY, REGIONAL_GROUPINGS,
            find_authority_by_variation
        )

        if not query_text:
            return None

        query_lower = query_text.lower()
        filters = SearchFilters()

        # ===== STATUS EXTRACTION =====
        status_patterns = {
            ApplicationStatus.REJECTED: ['reject', 'rejected', 'refuse', 'refused', 'denial', 'denied'],
            ApplicationStatus.APPROVED: ['approve', 'approved', 'grant', 'granted', 'permit', 'permitted', 'accept', 'accepted'],
            ApplicationStatus.WITHDRAWN: ['withdraw', 'withdrawn', 'cancel', 'cancelled'],
            ApplicationStatus.UNDER_CONSIDERATION: ['under consideration', 'pending', 'in progress', 'under review'],
            ApplicationStatus.SUBMITTED: ['submit', 'submitted', 'registered'],
            ApplicationStatus.VALIDATED: ['validate', 'validated', 'valid']
        }

        detected_statuses = []
        for status, patterns in status_patterns.items():
            for pattern in patterns:
                if pattern in query_lower:
                    detected_statuses.append(status)
                    logger.debug(f"Detected status '{status.value}' from pattern '{pattern}'")
                    break  # Only add once per status

        if detected_statuses:
            filters.statuses = detected_statuses

        # ===== DATE/YEAR EXTRACTION =====
        # Extract 4-digit years
        year_pattern = r'\b(20\d{2})\b'
        year_matches = re.findall(year_pattern, query_text)

        if year_matches:
            # Use the first year found
            year = int(year_matches[0])
            # Set date range for entire year
            filters.submission_date_from = datetime(year, 1, 1)
            filters.submission_date_to = datetime(year, 12, 31, 23, 59, 59)
            logger.debug(f"Detected year '{year}' - setting date range {filters.submission_date_from} to {filters.submission_date_to}")

        # Relative date patterns
        if 'last year' in query_lower or 'past year' in query_lower:
            current_year = datetime.now().year
            filters.submission_date_from = datetime(current_year - 1, 1, 1)
            filters.submission_date_to = datetime(current_year - 1, 12, 31, 23, 59, 59)
            logger.debug(f"Detected 'last year' - setting date range to {current_year - 1}")
        elif 'this year' in query_lower or 'current year' in query_lower:
            current_year = datetime.now().year
            filters.submission_date_from = datetime(current_year, 1, 1)
            filters.submission_date_to = datetime.now()
            logger.debug(f"Detected 'this year' - setting date range to {current_year}")
        elif 'last month' in query_lower or 'past month' in query_lower:
            from dateutil.relativedelta import relativedelta
            now = datetime.now()
            last_month = now - relativedelta(months=1)
            filters.submission_date_from = last_month.replace(day=1)
            # Last day of last month
            filters.submission_date_to = (now.replace(day=1) - relativedelta(days=1)).replace(hour=23, minute=59, second=59)
            logger.debug(f"Detected 'last month' - setting date range")

        # ===== DEVELOPMENT TYPE EXTRACTION =====
        dev_type_patterns = {
            DevelopmentType.RESIDENTIAL: ['residential', 'housing', 'homes', 'flats', 'apartments', 'dwellings'],
            DevelopmentType.COMMERCIAL: ['commercial', 'retail', 'shop', 'office', 'business'],
            DevelopmentType.INDUSTRIAL: ['industrial', 'factory', 'warehouse', 'manufacturing'],
            DevelopmentType.MIXED_USE: ['mixed use', 'mixed-use'],
            DevelopmentType.EXTENSION: ['extension', 'extend'],
            DevelopmentType.CHANGE_OF_USE: ['change of use', 'conversion'],
            DevelopmentType.NEW_BUILD: ['new build', 'newbuild', 'new construction']
        }

        detected_dev_types = []
        for dev_type, patterns in dev_type_patterns.items():
            for pattern in patterns:
                if pattern in query_lower:
                    detected_dev_types.append(dev_type)
                    logger.debug(f"Detected development type '{dev_type.value}' from pattern '{pattern}'")
                    break  # Only add once per dev type

        if detected_dev_types:
            filters.development_types = detected_dev_types

        # ===== LOCATION EXTRACTION =====
        # Extract location-based filters: authorities, postcodes, wards

        detected_authorities = []
        detected_postcode = None
        detected_ward = None

        # 1. POSTCODE EXTRACTION
        # UK postcode patterns (full and partial)
        # Full postcode: SW1A 1AA, M1 1AE, PR8 3BH
        # Partial postcode: SW1A, M1, PR8
        postcode_pattern = r'\b([A-Z]{1,2}\d{1,2}[A-Z]?)\s?(\d[A-Z]{2})?\b'
        postcode_matches = re.findall(postcode_pattern, query_text.upper())

        if postcode_matches:
            # Combine outward and inward codes if both present
            for match in postcode_matches:
                outward, inward = match
                if inward:
                    detected_postcode = f"{outward} {inward}"
                else:
                    detected_postcode = outward
                logger.debug(f"Detected postcode '{detected_postcode}' from query")
                break  # Use first postcode found

        # 2. WARD EXTRACTION
        # Look for explicit ward mentions with context keywords
        ward_keywords = ['ward', 'electoral ward', 'in the', 'constituency']
        for keyword in ward_keywords:
            if keyword in query_lower:
                # Extract ward name after keyword
                # Pattern: "in [ward name] ward" or "ward of [ward name]"
                ward_pattern = rf'{keyword}\s+(?:of\s+)?([A-Za-z\s]+?)(?:\s+(?:ward|area|council|borough)|$)'
                ward_match = re.search(ward_pattern, query_text, re.IGNORECASE)
                if ward_match:
                    detected_ward = ward_match.group(1).strip()
                    logger.debug(f"Detected ward '{detected_ward}' from query")
                    break

        # 3. PLANNING AUTHORITY EXTRACTION
        # Extract using location context keywords and authority matching

        # Location context keywords that indicate a location mention
        location_keywords = [
            r'\bin\s+',
            r'\bat\s+',
            r'\bnear\s+',
            r'\baround\s+',
            r'\bwithin\s+',
            r'\barea\s+',
            r'\bregion\s+',
            r'\bcouncil\s+',
            r'\bborough\s+',
            r'\bauthority\s+',
        ]

        # Build location extraction pattern
        # Match: "in London", "near Manchester", "Sefton area", etc.
        location_pattern = '|'.join(location_keywords)

        # a) Extract locations with explicit keywords
        keyword_locations = re.findall(
            rf'(?:{location_pattern})([A-Za-z\s&\-]+?)(?:\s+(?:or|and|area|region|council|borough|,|\.|$))',
            query_text,
            re.IGNORECASE
        )

        for location in keyword_locations:
            location_clean = location.strip()
            if len(location_clean) > 2:  # Ignore very short matches
                # Try to find matching authority
                canonical_authority = find_authority_by_variation(location_clean)
                if canonical_authority and canonical_authority not in detected_authorities:
                    detected_authorities.append(canonical_authority)
                    logger.debug(f"Detected authority '{canonical_authority}' from keyword location '{location_clean}'")

        # b) Check for direct authority mentions (without keywords)
        # Match against all known authorities and their variations
        for canonical_authority, variations in UK_PLANNING_AUTHORITIES.items():
            for variation in variations:
                # Use word boundaries to avoid partial matches
                if re.search(rf'\b{re.escape(variation)}\b', query_text, re.IGNORECASE):
                    if canonical_authority not in detected_authorities:
                        detected_authorities.append(canonical_authority)
                        logger.debug(f"Detected authority '{canonical_authority}' directly from variation '{variation}'")
                    break  # Move to next canonical authority

        # c) Check for city names and map to authorities
        # SPECIAL CASE: "London" should map to ALL London boroughs (Greater London)
        # BUT: "City of London" is a specific authority, so exclude that case
        if re.search(r'\bLondon\b', query_text, re.IGNORECASE) and not re.search(r'\bCity of London\b', query_text, re.IGNORECASE):
            # Check if "Greater London" exists in regional groupings
            if "Greater London" in REGIONAL_GROUPINGS:
                for authority in REGIONAL_GROUPINGS["Greater London"]:
                    if authority not in detected_authorities:
                        detected_authorities.append(authority)
                logger.debug(f"Detected 'London' (not 'City of London') - added all {len(REGIONAL_GROUPINGS['Greater London'])} Greater London authorities")
        else:
            # Normal city-to-authority mapping for other cities
            for city, authority in CITY_TO_AUTHORITY.items():
                if city.lower() == 'london':
                    continue  # Skip London - handled above
                if re.search(rf'\b{re.escape(city)}\b', query_text, re.IGNORECASE):
                    if authority not in detected_authorities:
                        detected_authorities.append(authority)
                        logger.debug(f"Detected authority '{authority}' from city name '{city}'")

        # d) Check for regional groupings (e.g., "Greater Manchester")
        for region, authorities in REGIONAL_GROUPINGS.items():
            if re.search(rf'\b{re.escape(region)}\b', query_text, re.IGNORECASE):
                # Add all authorities in the region
                for authority in authorities:
                    if authority not in detected_authorities:
                        detected_authorities.append(authority)
                logger.debug(f"Detected regional grouping '{region}' - added {len(authorities)} authorities")
                break  # Only match one region

        # e) Handle multi-location queries with "or" / "and"
        # Example: "London or Manchester", "Birmingham and Leeds"
        or_and_pattern = r'\b([A-Za-z\s]+?)\s+(?:or|and)\s+([A-Za-z\s]+?)(?:\s|$|,|\.)'
        multi_location_matches = re.findall(or_and_pattern, query_text, re.IGNORECASE)

        for loc1, loc2 in multi_location_matches:
            for loc in [loc1.strip(), loc2.strip()]:
                if len(loc) > 2:
                    canonical = find_authority_by_variation(loc)
                    if canonical and canonical not in detected_authorities:
                        detected_authorities.append(canonical)
                        logger.debug(f"Detected authority '{canonical}' from multi-location pattern")

        # Assign extracted locations to filters
        if detected_authorities:
            filters.authorities = detected_authorities

        if detected_postcode:
            filters.postcode = detected_postcode

        if detected_ward:
            filters.ward = detected_ward

        # Only return filters if we extracted something
        if (filters.statuses or filters.submission_date_from or filters.development_types or
            filters.authorities or filters.postcode or filters.ward):
            return filters

        return None

    def _merge_filters(self, base_filters: SearchFilters, extracted_filters: Optional[SearchFilters]) -> SearchFilters:
        """
        Merge extracted filters with provided filters

        Extracted filters take precedence over base filters for specific fields

        Args:
            base_filters: Base filter object
            extracted_filters: Extracted filters from query

        Returns:
            Merged SearchFilters object
        """
        if not extracted_filters:
            return base_filters

        # Start with base filters
        merged = SearchFilters(**base_filters.dict(exclude_none=True))

        # Merge extracted filters (they take precedence)
        extracted_dict = extracted_filters.dict(exclude_none=True)

        for key, value in extracted_dict.items():
            if value is not None:
                # For list fields, merge instead of replace
                if key in ['statuses', 'development_types', 'application_types', 'authorities', 'decisions']:
                    existing = getattr(merged, key) or []
                    # Combine and deduplicate
                    combined = list(set(existing + value))
                    setattr(merged, key, combined)
                else:
                    # For other fields, extracted value takes precedence
                    setattr(merged, key, value)

        return merged


# Global search service instance
search_service = SearchService()