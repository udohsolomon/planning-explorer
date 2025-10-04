"""
Natural Language Query Processing for Planning Applications

This module converts natural language queries into structured Elasticsearch
searches, understands planning-specific terminology, and provides intelligent
query expansion and suggestions.
"""

import asyncio
import logging
import time
import re
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import openai
import anthropic
from datetime import datetime, timedelta

from app.core.ai_config import ai_config, AIModel, AIProvider

logger = logging.getLogger(__name__)


class QueryType(str, Enum):
    """Types of natural language queries"""
    SEARCH = "search"                    # General search queries
    FILTER = "filter"                    # Filtering operations
    AGGREGATION = "aggregation"          # Statistical queries
    COMPARISON = "comparison"            # Comparative analysis
    TREND = "trend"                      # Trend analysis
    LOCATION = "location"                # Location-based queries
    TEMPORAL = "temporal"                # Time-based queries


class QueryIntent(str, Enum):
    """Intent classification for queries"""
    FIND_APPLICATIONS = "find_applications"
    GET_STATISTICS = "get_statistics"
    COMPARE_AREAS = "compare_areas"
    ANALYZE_TRENDS = "analyze_trends"
    CHECK_STATUS = "check_status"
    FIND_SIMILAR = "find_similar"
    GET_INSIGHTS = "get_insights"


@dataclass
class QueryEntity:
    """Extracted entity from natural language query"""
    entity_type: str
    value: str
    confidence: float
    start_pos: int
    end_pos: int


@dataclass
class ParsedQuery:
    """Parsed natural language query with extracted components"""
    original_query: str
    intent: QueryIntent
    query_type: QueryType
    entities: List[QueryEntity]
    filters: Dict[str, Any]
    elasticsearch_query: Dict[str, Any]
    confidence_score: float
    processing_time_ms: int
    suggestions: List[str]


@dataclass
class QuerySuggestion:
    """Query suggestion with explanation"""
    suggestion: str
    explanation: str
    confidence: float
    query_type: QueryType


class NLPProcessor:
    """
    Natural Language Processing service for planning queries.

    Converts natural language into structured Elasticsearch queries with
    planning domain expertise and intelligent query expansion.
    """

    def __init__(self):
        self.config = ai_config
        self._initialize_clients()
        self._load_planning_vocabulary()
        self._load_query_templates()

    def _initialize_clients(self) -> None:
        """Initialize AI service clients"""
        self.openai_client = None
        self.anthropic_client = None

        if self.config.settings.openai_api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=self.config.settings.openai_api_key)
            logger.info("OpenAI client initialized for NLP processing")

        if self.config.settings.anthropic_api_key:
            self.anthropic_client = anthropic.AsyncAnthropic(
                api_key=self.config.settings.anthropic_api_key
            )
            logger.info("Anthropic client initialized for NLP processing")

    def _load_planning_vocabulary(self) -> None:
        """Load planning-specific vocabulary and synonyms"""
        self.planning_vocabulary = {
            # Development types
            "development_types": {
                "residential": ["housing", "homes", "flats", "apartments", "dwellings", "houses"],
                "commercial": ["retail", "shop", "store", "office", "business", "commercial"],
                "industrial": ["factory", "warehouse", "manufacturing", "industrial"],
                "mixed_use": ["mixed use", "mixed-use", "mixed development"],
                "change_of_use": ["change of use", "conversion", "repurpose"],
                "extension": ["extension", "extend", "addition", "enlargement"],
                "demolition": ["demolish", "demolition", "tear down", "remove"]
            },

            # Status terms
            "status": {
                "approved": ["approved", "granted", "permitted", "accepted"],
                "refused": ["refused", "rejected", "denied", "declined"],
                "pending": ["pending", "submitted", "under review", "in progress"],
                "withdrawn": ["withdrawn", "cancelled", "retracted"]
            },

            # Location terms
            "location_types": {
                "urban": ["city", "town", "urban", "metropolitan"],
                "rural": ["rural", "countryside", "village", "hamlet"],
                "suburb": ["suburban", "suburb", "residential area"],
                "industrial": ["industrial estate", "business park", "industrial area"]
            },

            # Time periods
            "time_periods": {
                "recent": ["recent", "latest", "new", "current"],
                "last_month": ["last month", "past month", "previous month"],
                "last_year": ["last year", "past year", "previous year"],
                "this_year": ["this year", "current year", "2024"]
            },

            # Planning terms
            "planning_terms": {
                "major": ["major", "large", "significant", "substantial"],
                "minor": ["minor", "small", "householder"],
                "outline": ["outline", "outline planning"],
                "full": ["full", "detailed", "full planning"],
                "listed": ["listed building", "heritage", "historic"],
                "conservation": ["conservation area", "conservation"]
            }
        }

        # Create reverse lookup for quick matching
        self.term_mapping = {}
        for category, subcategories in self.planning_vocabulary.items():
            for standard_term, synonyms in subcategories.items():
                for synonym in synonyms:
                    self.term_mapping[synonym.lower()] = {
                        "category": category,
                        "standard_term": standard_term
                    }

    def _load_query_templates(self) -> None:
        """Load query templates for different intents"""
        self.query_templates = {
            QueryIntent.FIND_APPLICATIONS: {
                "base_query": {
                    "query": {
                        "bool": {
                            "must": [],
                            "filter": [],
                            "should": []
                        }
                    },
                    "sort": [{"date_received": {"order": "desc"}}],
                    "size": 20
                },
                "description": "Find planning applications matching criteria"
            },

            QueryIntent.GET_STATISTICS: {
                "base_query": {
                    "size": 0,
                    "aggs": {
                        "by_status": {
                            "terms": {"field": "status.keyword"}
                        },
                        "by_type": {
                            "terms": {"field": "development_type.keyword"}
                        }
                    }
                },
                "description": "Get statistical aggregations"
            },

            QueryIntent.ANALYZE_TRENDS: {
                "base_query": {
                    "size": 0,
                    "aggs": {
                        "over_time": {
                            "date_histogram": {
                                "field": "date_received",
                                "calendar_interval": "month"
                            }
                        }
                    }
                },
                "description": "Analyze trends over time"
            }
        }

    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> ParsedQuery:
        """
        Process natural language query and convert to structured search.

        Args:
            query: Natural language query string
            context: Additional context for query processing

        Returns:
            ParsedQuery with structured components
        """
        start_time = time.time()

        try:
            # Clean and normalize query
            normalized_query = self._normalize_query(query)

            # Extract entities using pattern matching
            entities = self._extract_entities(normalized_query)

            # Classify intent and query type
            intent = await self._classify_intent(normalized_query, entities)
            query_type = self._determine_query_type(normalized_query, intent)

            # Build filters from entities
            filters = self._build_filters_from_entities(entities)

            # Generate Elasticsearch query
            es_query = self._build_elasticsearch_query(intent, filters, entities)

            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(entities, intent)

            # Generate suggestions
            suggestions = await self._generate_suggestions(normalized_query, intent, entities)

            processing_time_ms = int((time.time() - start_time) * 1000)

            parsed_query = ParsedQuery(
                original_query=query,
                intent=intent,
                query_type=query_type,
                entities=entities,
                filters=filters,
                elasticsearch_query=es_query,
                confidence_score=confidence_score,
                processing_time_ms=processing_time_ms,
                suggestions=suggestions
            )

            logger.info(f"Processed NLP query in {processing_time_ms}ms: '{query}' -> {intent.value}")
            return parsed_query

        except Exception as e:
            logger.error(f"Error processing query '{query}': {str(e)}")
            return self._generate_fallback_query(query)

    def _normalize_query(self, query: str) -> str:
        """Normalize query text for processing"""
        # Convert to lowercase
        normalized = query.lower().strip()

        # Remove extra whitespace
        normalized = re.sub(r'\\s+', ' ', normalized)

        # Handle common contractions
        contractions = {
            "won't": "will not",
            "can't": "cannot",
            "don't": "do not",
            "isn't": "is not",
            "aren't": "are not"
        }

        for contraction, expansion in contractions.items():
            normalized = normalized.replace(contraction, expansion)

        return normalized

    def _extract_entities(self, query: str) -> List[QueryEntity]:
        """Extract entities from query using pattern matching and vocabulary"""
        entities = []

        # Extract locations (postcodes, area names)
        postcode_pattern = r'\\b[a-z]{1,2}\\d[a-z\\d]?\\s*\\d[a-z]{2}\\b'
        postcode_matches = re.finditer(postcode_pattern, query, re.IGNORECASE)
        for match in postcode_matches:
            entities.append(QueryEntity(
                entity_type="postcode",
                value=match.group().upper(),
                confidence=0.95,
                start_pos=match.start(),
                end_pos=match.end()
            ))

        # Extract dates
        date_patterns = [
            (r'\\b(\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4})\\b', "date"),
            (r'\\b(\\d{4})\\b', "year"),
            (r'\\b(january|february|march|april|may|june|july|august|september|october|november|december)\\b', "month"),
            (r'\\b(last|past|previous)\\s+(year|month|week)\\b', "relative_date")
        ]

        for pattern, entity_type in date_patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                entities.append(QueryEntity(
                    entity_type=entity_type,
                    value=match.group(),
                    confidence=0.9,
                    start_pos=match.start(),
                    end_pos=match.end()
                ))

        # Extract planning vocabulary terms
        for term, mapping in self.term_mapping.items():
            if term in query:
                # Find position in query
                start_pos = query.find(term)
                entities.append(QueryEntity(
                    entity_type=mapping["category"],
                    value=mapping["standard_term"],
                    confidence=0.85,
                    start_pos=start_pos,
                    end_pos=start_pos + len(term)
                ))

        # Extract numbers (for statistics queries)
        number_pattern = r'\\b(\\d+)\\b'
        number_matches = re.finditer(number_pattern, query)
        for match in number_matches:
            entities.append(QueryEntity(
                entity_type="number",
                value=match.group(),
                confidence=0.7,
                start_pos=match.start(),
                end_pos=match.end()
            ))

        # Remove duplicates and overlapping entities
        entities = self._deduplicate_entities(entities)

        return entities

    def _deduplicate_entities(self, entities: List[QueryEntity]) -> List[QueryEntity]:
        """Remove duplicate and overlapping entities"""
        # Sort by start position
        entities.sort(key=lambda e: e.start_pos)

        deduplicated = []
        for entity in entities:
            # Check for overlap with existing entities
            overlaps = False
            for existing in deduplicated:
                if (entity.start_pos < existing.end_pos and
                    entity.end_pos > existing.start_pos):
                    # Choose entity with higher confidence
                    if entity.confidence > existing.confidence:
                        deduplicated.remove(existing)
                    else:
                        overlaps = True
                    break

            if not overlaps:
                deduplicated.append(entity)

        return deduplicated

    async def _classify_intent(self, query: str, entities: List[QueryEntity]) -> QueryIntent:
        """Classify the intent of the query"""

        # Rule-based intent classification
        query_lower = query.lower()

        # Statistical queries
        if any(word in query_lower for word in ["how many", "count", "number of", "statistics", "stats"]):
            return QueryIntent.GET_STATISTICS

        # Comparison queries
        if any(word in query_lower for word in ["compare", "comparison", "versus", "vs", "difference"]):
            return QueryIntent.COMPARE_AREAS

        # Trend queries
        if any(word in query_lower for word in ["trend", "over time", "change", "increase", "decrease"]):
            return QueryIntent.ANALYZE_TRENDS

        # Status queries
        if any(word in query_lower for word in ["status", "approved", "refused", "pending"]):
            return QueryIntent.CHECK_STATUS

        # Similarity queries
        if any(word in query_lower for word in ["similar", "like", "comparable"]):
            return QueryIntent.FIND_SIMILAR

        # Insights queries
        if any(word in query_lower for word in ["insights", "analysis", "opportunities", "risks"]):
            return QueryIntent.GET_INSIGHTS

        # Default to find applications
        return QueryIntent.FIND_APPLICATIONS

    def _determine_query_type(self, query: str, intent: QueryIntent) -> QueryType:
        """Determine the type of query based on content and intent"""

        query_lower = query.lower()

        # Location-based queries
        if any(entity.entity_type == "postcode" for entity in []) or \
           any(word in query_lower for word in ["near", "in", "area", "location"]):
            return QueryType.LOCATION

        # Temporal queries
        if any(word in query_lower for word in ["when", "date", "recent", "last", "since"]):
            return QueryType.TEMPORAL

        # Aggregation queries
        if intent in [QueryIntent.GET_STATISTICS, QueryIntent.ANALYZE_TRENDS]:
            return QueryType.AGGREGATION

        # Comparison queries
        if intent == QueryIntent.COMPARE_AREAS:
            return QueryType.COMPARISON

        # Filter queries
        if any(word in query_lower for word in ["where", "with", "having", "type"]):
            return QueryType.FILTER

        # Default to search
        return QueryType.SEARCH

    def _build_filters_from_entities(self, entities: List[QueryEntity]) -> Dict[str, Any]:
        """Build filter dictionary from extracted entities"""
        filters = {}

        for entity in entities:
            if entity.entity_type == "development_types":
                filters["development_type"] = entity.value
            elif entity.entity_type == "status":
                filters["status"] = entity.value
            elif entity.entity_type == "postcode":
                filters["postcode"] = entity.value
            elif entity.entity_type == "year":
                filters["year"] = int(entity.value)
            elif entity.entity_type == "relative_date":
                filters["date_range"] = self._parse_relative_date(entity.value)

        return filters

    def _parse_relative_date(self, relative_date: str) -> Dict[str, str]:
        """Parse relative date expressions"""
        now = datetime.utcnow()

        if "last year" in relative_date or "past year" in relative_date:
            start_date = now - timedelta(days=365)
            return {"gte": start_date.isoformat()}
        elif "last month" in relative_date or "past month" in relative_date:
            start_date = now - timedelta(days=30)
            return {"gte": start_date.isoformat()}
        elif "last week" in relative_date or "past week" in relative_date:
            start_date = now - timedelta(days=7)
            return {"gte": start_date.isoformat()}

        return {}

    def _build_elasticsearch_query(
        self,
        intent: QueryIntent,
        filters: Dict[str, Any],
        entities: List[QueryEntity]
    ) -> Dict[str, Any]:
        """Build Elasticsearch query from intent and filters"""

        # Get base query template
        template = self.query_templates.get(intent, self.query_templates[QueryIntent.FIND_APPLICATIONS])
        es_query = template["base_query"].copy()

        # Apply filters
        if "query" in es_query and "bool" in es_query["query"]:
            bool_query = es_query["query"]["bool"]

            # Add term filters
            for field, value in filters.items():
                if field == "date_range":
                    bool_query["filter"].append({
                        "range": {
                            "date_received": value
                        }
                    })
                elif field in ["development_type", "status", "authority"]:
                    bool_query["filter"].append({
                        "term": {f"{field}.keyword": value}
                    })
                elif field == "postcode":
                    bool_query["should"].append({
                        "match": {"address": value}
                    })

            # Add text search for remaining terms
            search_terms = self._extract_search_terms(entities)
            if search_terms:
                bool_query["must"].append({
                    "multi_match": {
                        "query": " ".join(search_terms),
                        "fields": ["description^2", "proposal", "address", "development_type"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                })

        return es_query

    def _extract_search_terms(self, entities: List[QueryEntity]) -> List[str]:
        """Extract search terms that aren't covered by filters"""
        # This would extract free-form search terms that aren't structured entities
        # For now, returning empty list as entities cover most cases
        return []

    def _calculate_confidence_score(self, entities: List[QueryEntity], intent: QueryIntent) -> float:
        """Calculate confidence score for query processing"""
        if not entities:
            return 0.3  # Low confidence without entities

        # Base confidence from entities
        entity_confidence = sum(e.confidence for e in entities) / len(entities)

        # Boost for clear intent indicators
        intent_boost = 0.1 if intent != QueryIntent.FIND_APPLICATIONS else 0.0

        # Boost for multiple entities
        entity_count_boost = min(0.2, len(entities) * 0.05)

        return min(1.0, entity_confidence + intent_boost + entity_count_boost)

    async def _generate_suggestions(
        self,
        query: str,
        intent: QueryIntent,
        entities: List[QueryEntity]
    ) -> List[str]:
        """Generate query suggestions for improvement"""
        suggestions = []

        # Suggest missing common filters
        if intent == QueryIntent.FIND_APPLICATIONS:
            if not any(e.entity_type == "development_types" for e in entities):
                suggestions.append("Try adding a development type (e.g., 'residential', 'commercial')")

            if not any(e.entity_type == "postcode" for e in entities):
                suggestions.append("Add a location or postcode to narrow results")

        # Suggest time filters for statistics
        if intent == QueryIntent.GET_STATISTICS:
            if not any(e.entity_type in ["date", "year", "relative_date"] for e in entities):
                suggestions.append("Add a time period (e.g., 'last year', '2024')")

        # Suggest comparison targets
        if intent == QueryIntent.COMPARE_AREAS:
            postcodes = [e for e in entities if e.entity_type == "postcode"]
            if len(postcodes) < 2:
                suggestions.append("Add another location for comparison")

        return suggestions

    def _generate_fallback_query(self, query: str) -> ParsedQuery:
        """Generate fallback query when processing fails"""
        logger.warning(f"Using fallback query processing for: '{query}'")

        # Simple text search fallback
        es_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["description", "proposal", "address"],
                    "fuzziness": "AUTO"
                }
            },
            "size": 20
        }

        return ParsedQuery(
            original_query=query,
            intent=QueryIntent.FIND_APPLICATIONS,
            query_type=QueryType.SEARCH,
            entities=[],
            filters={},
            elasticsearch_query=es_query,
            confidence_score=0.2,
            processing_time_ms=10,
            suggestions=["Try using more specific terms or filters"]
        )

    async def expand_query(self, query: str) -> List[QuerySuggestion]:
        """Generate expanded query suggestions using AI"""
        suggestions = []

        try:
            if self.openai_client:
                suggestions = await self._generate_ai_suggestions(query)
            else:
                suggestions = self._generate_rule_based_suggestions(query)

        except Exception as e:
            logger.error(f"Error generating query expansions: {e}")
            suggestions = self._generate_rule_based_suggestions(query)

        return suggestions

    async def _generate_ai_suggestions(self, query: str) -> List[QuerySuggestion]:
        """Generate query suggestions using AI"""
        system_prompt = """You are an expert in UK planning applications and search queries.
        Generate 3-5 alternative query suggestions that would help users find relevant planning applications.
        Focus on planning-specific terminology and common search patterns."""

        user_prompt = f"""Original query: "{query}"

        Provide alternative search suggestions that:
        1. Use planning-specific terminology
        2. Add relevant filters or constraints
        3. Broaden or narrow the search appropriately
        4. Help users discover related information

        Format each suggestion with a brief explanation."""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            # Parse AI response into suggestions
            content = response.choices[0].message.content
            return self._parse_ai_suggestions(content)

        except Exception as e:
            logger.error(f"Error with AI suggestion generation: {e}")
            return []

    def _parse_ai_suggestions(self, content: str) -> List[QuerySuggestion]:
        """Parse AI-generated suggestions into structured format"""
        suggestions = []

        # Simple parsing - in production would use more sophisticated NLP
        lines = content.split('\\n')
        for line in lines:
            if line.strip() and not line.startswith('#'):
                suggestions.append(QuerySuggestion(
                    suggestion=line.strip(),
                    explanation="AI-generated suggestion",
                    confidence=0.8,
                    query_type=QueryType.SEARCH
                ))

        return suggestions[:5]  # Limit to 5 suggestions

    def _generate_rule_based_suggestions(self, query: str) -> List[QuerySuggestion]:
        """Generate suggestions using rule-based approach"""
        suggestions = []
        query_lower = query.lower()

        # Development type suggestions
        if "residential" not in query_lower and "commercial" not in query_lower:
            suggestions.append(QuerySuggestion(
                suggestion=f"{query} residential",
                explanation="Filter by residential developments",
                confidence=0.7,
                query_type=QueryType.FILTER
            ))

        # Location suggestions
        if not re.search(r'\\b[a-z]{1,2}\\d[a-z\\d]?\\s*\\d[a-z]{2}\\b', query_lower):
            suggestions.append(QuerySuggestion(
                suggestion=f"{query} in [postcode]",
                explanation="Add location to narrow results",
                confidence=0.6,
                query_type=QueryType.LOCATION
            ))

        # Time suggestions
        if "recent" not in query_lower and "last" not in query_lower:
            suggestions.append(QuerySuggestion(
                suggestion=f"{query} in last year",
                explanation="Filter by recent applications",
                confidence=0.7,
                query_type=QueryType.TEMPORAL
            ))

        return suggestions

    def get_vocabulary_stats(self) -> Dict[str, Any]:
        """Get statistics about the planning vocabulary"""
        return {
            "total_categories": len(self.planning_vocabulary),
            "total_terms": sum(len(subcats) for subcats in self.planning_vocabulary.values()),
            "total_synonyms": len(self.term_mapping),
            "categories": list(self.planning_vocabulary.keys())
        }

    def add_vocabulary_term(self, category: str, term: str, synonyms: List[str]) -> None:
        """Add new term to planning vocabulary"""
        if category not in self.planning_vocabulary:
            self.planning_vocabulary[category] = {}

        self.planning_vocabulary[category][term] = synonyms

        # Update term mapping
        for synonym in synonyms:
            self.term_mapping[synonym.lower()] = {
                "category": category,
                "standard_term": term
            }

        logger.info(f"Added vocabulary term: {term} with {len(synonyms)} synonyms to {category}")

    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate query and provide feedback"""
        issues = []
        suggestions = []

        # Check query length
        if len(query) < 3:
            issues.append("Query too short - needs at least 3 characters")

        if len(query) > 500:
            issues.append("Query too long - consider simplifying")

        # Check for meaningful content
        words = query.split()
        if len(words) < 2:
            suggestions.append("Try using more descriptive terms")

        # Check for planning terminology
        has_planning_terms = any(
            term in query.lower() for term in self.term_mapping.keys()
        )
        if not has_planning_terms:
            suggestions.append("Consider using planning-specific terms like 'residential' or 'commercial'")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "estimated_results": "many" if has_planning_terms else "few"
        }