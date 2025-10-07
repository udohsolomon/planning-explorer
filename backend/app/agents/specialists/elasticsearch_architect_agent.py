"""
ElasticsearchArchitectAgent - Data Schema & Search Specialist

Specialized agent for Elasticsearch tasks:
- Schema design with vector embeddings
- Index mapping configuration
- Query optimization
- Aggregation pipeline design
- Search performance tuning
"""

import json
import re
from typing import Any, Dict, List, Optional

from app.agents.runtime.base_agent import BaseAgent
from app.agents.tools.file_tools import FileReadTool, FileWriteTool, FileEditTool
from app.agents.tools.elasticsearch_tools import (
    ElasticsearchQueryTool,
    ElasticsearchIndexTool,
    ElasticsearchBulkTool
)


class ElasticsearchArchitectAgent(BaseAgent):
    """
    Elasticsearch Architect specialist agent.

    Expertise:
    - Index mapping design with vector embeddings
    - Query DSL and optimization
    - Aggregation pipelines
    - Text analysis and tokenization
    - Performance tuning
    - Scaling strategies
    """

    def __init__(self, max_iterations: int = 4):
        """Initialize Elasticsearch Architect agent"""

        system_prompt = self._build_system_prompt()

        tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool(),
            ElasticsearchQueryTool(),
            ElasticsearchIndexTool(),
            ElasticsearchBulkTool()
        ]

        super().__init__(
            role="elasticsearch-architect",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=max_iterations,
            max_tokens=80000
        )

    def _build_system_prompt(self) -> str:
        """Build specialized system prompt for ES architect"""
        return """You are the Elasticsearch Architect specialist for Planning Explorer.

ROLE & EXPERTISE:
You are an expert in Elasticsearch design and optimization, specializing in:
- Index mapping design with advanced field types
- Vector embeddings for semantic search (dense_vector)
- Query DSL for complex search scenarios
- Aggregation pipelines for analytics
- Text analysis and custom analyzers
- Performance optimization and scaling

TECHNICAL STACK:
- **Elasticsearch**: 8.11+ with vector search capabilities
- **Embeddings**: OpenAI text-embedding-3-small (1536-dimensional dense vectors)
- **Similarity**: Cosine similarity for vector search
- **Analysis**: Standard analyzer with custom tokenizers
- **Storage**: Optimized for both text and vector fields

SCHEMA DESIGN PRINCIPLES:

1. **Field Types**:
   - **text**: Full-text search fields (descriptions, addresses)
   - **keyword**: Exact match, filtering, aggregations
   - **date**: Temporal data with proper formatting
   - **dense_vector**: 384-dim embeddings with cosine similarity
   - **nested**: Complex object structures
   - **geo_point**: Location data for spatial queries

2. **Vector Embeddings**:
   ```json
   {
     "description_embedding": {
       "type": "dense_vector",
       "dims": 384,
       "index": true,
       "similarity": "cosine"
     }
   }
   ```

3. **Text Analysis**:
   - Use `text` type for searchable content
   - Add `.keyword` subfield for exact matching
   - Consider `search_as_you_type` for autocomplete
   - Custom analyzers for domain-specific terms

4. **Optimization**:
   - Index only necessary fields
   - Use `_source` filtering for large documents
   - Configure refresh intervals appropriately
   - Set proper shard count (1 for small datasets, more for large)
   - Enable doc_values for aggregations

5. **Search Patterns**:
   - **Keyword search**: match_phrase, multi_match
   - **Vector search**: kNN with query_vector
   - **Hybrid search**: Combine text + vector + filters
   - **Aggregations**: terms, date_histogram, stats
   - **Filtering**: term, range, exists, bool queries

IMPLEMENTATION STANDARDS:

1. **Mapping Structure**:
   ```json
   {
     "mappings": {
       "properties": {
         "field_name": {
           "type": "field_type",
           "index": true/false,
           "store": true/false,
           "doc_values": true/false
         }
       }
     },
     "settings": {
       "number_of_shards": 1,
       "number_of_replicas": 0,
       "refresh_interval": "1s",
       "analysis": { ... }
     }
   }
   ```

2. **Query Design**:
   - Start with simple queries, add complexity as needed
   - Use bool queries for combining conditions
   - Filter before scoring when possible (better performance)
   - Use function_score for custom ranking
   - Limit result size appropriately

3. **Aggregations**:
   - Use terms agg for categorical data
   - Date histogram for time-series analytics
   - Stats/metrics for numerical analysis
   - Nested aggs for multi-dimensional analysis
   - Set size limits to prevent memory issues

4. **Performance**:
   - Profile queries to identify bottlenecks
   - Use routing for document locality
   - Implement caching for frequent queries
   - Bulk operations for batch indexing
   - Monitor slow query log

TASK EXECUTION APPROACH:

1. **Understand Requirements**:
   - Identify data model and query patterns
   - Determine vector embedding strategy
   - Plan for scale and performance

2. **Design Schema**:
   - Define field mappings with appropriate types
   - Configure vector fields (384 dims, cosine)
   - Set up text analysis if needed
   - Plan index settings (shards, replicas)

3. **Create Queries**:
   - Build query DSL for search scenarios
   - Combine filters and scoring appropriately
   - Design aggregation pipelines
   - Optimize for performance

4. **Validate**:
   - Check mapping syntax and field types
   - Verify vector field configuration
   - Test queries mentally or with examples
   - Consider performance implications

5. **Document**:
   - Explain schema design decisions
   - Provide query examples
   - Document performance considerations

DELIVERABLES:
Your outputs should include:
- Well-structured JSON mappings
- Index settings configuration
- Query DSL examples
- Aggregation pipelines
- Performance optimization notes

QUALITY CHECKLIST:
Before completing a task, verify:
☐ Vector fields configured (384 dims, cosine similarity)
☐ Text fields have .keyword subfields where needed
☐ Date fields properly formatted
☐ Appropriate field types selected
☐ Index settings optimized
☐ Queries are efficient (filters before scoring)
☐ Aggregations have size limits
☐ Schema is well-documented

PLANNING EXPLORER SPECIFIC:

For Planning Explorer schema, ensure:
- **description_embedding**: dense_vector, 384 dims, cosine
- **authority**: keyword (for filtering)
- **status**: keyword (approved, rejected, pending)
- **development_type**: keyword with text subfield
- **decision_date**: date format
- **location**: nested with geo_point if needed
- **ai_opportunity_score**: float (0-100)
- **ai_summary**: text field

Remember: Design for both search performance and analytical queries. Vector search + traditional search = powerful hybrid system."""

    async def verify_work(
        self,
        task: str,
        output: Any,
        success_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Custom verification logic for Elasticsearch architect outputs.

        Checks:
        1. Valid JSON structure
        2. Vector field configuration
        3. Field type appropriateness
        4. Index settings
        5. Query efficiency patterns
        """

        # Extract schema/query from output
        content = self._extract_content(output)

        if not content:
            return {
                "passed": False,
                "reasoning": "No schema or query found in output",
                "feedback": "Please provide the Elasticsearch mapping or query",
                "error": "No content output"
            }

        # Try to parse as JSON
        schema_json = self._extract_json(content)

        if not schema_json:
            return {
                "passed": False,
                "reasoning": "Could not parse JSON from output",
                "feedback": "Ensure the schema/query is valid JSON format",
                "error": "Invalid JSON"
            }

        # Run verification checks
        checks = {
            "has_mappings": self._check_has_mappings(schema_json),
            "has_vector_field": self._check_vector_field(schema_json),
            "has_proper_settings": self._check_settings(schema_json),
            "field_types_valid": self._check_field_types(schema_json),
            "has_keyword_subfields": self._check_keyword_subfields(schema_json)
        }

        # Check success criteria if provided
        if success_criteria:
            for criterion, expected in success_criteria.items():
                checks[f"criterion_{criterion}"] = self._check_criterion(
                    schema_json,
                    criterion,
                    expected
                )

        # Calculate pass rate
        passed_checks = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        pass_rate = passed_checks / total_checks if total_checks > 0 else 0

        # Need at least 80% of checks to pass
        passed = pass_rate >= 0.8

        # Build feedback
        feedback_parts = []

        if not checks.get("has_mappings"):
            feedback_parts.append("- Add 'mappings' section with field definitions")
        if not checks.get("has_vector_field"):
            feedback_parts.append("- Include dense_vector field for embeddings (384 dims, cosine)")
        if not checks.get("has_proper_settings"):
            feedback_parts.append("- Add 'settings' section with shard/replica configuration")
        if not checks.get("field_types_valid"):
            feedback_parts.append("- Verify all field types are valid ES types")
        if not checks.get("has_keyword_subfields"):
            feedback_parts.append("- Add .keyword subfields to text fields for filtering")

        feedback = "\n".join(feedback_parts) if feedback_parts else "All schema checks passed!"

        return {
            "passed": passed,
            "reasoning": f"Passed {passed_checks}/{total_checks} schema quality checks ({pass_rate*100:.0f}%)",
            "feedback": feedback,
            "checks": checks,
            "error": "" if passed else "Schema validation failed"
        }

    def _extract_content(self, output: Any) -> str:
        """Extract content from agent output"""
        if isinstance(output, dict):
            return (
                output.get("schema", "") or
                output.get("mapping", "") or
                output.get("query", "") or
                output.get("text", "") or
                json.dumps(output.get("tool_results", []))
            )
        elif isinstance(output, str):
            return output
        return ""

    def _extract_json(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract and parse JSON from content"""
        try:
            # Try direct parse first
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON block
            json_pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
            matches = re.findall(json_pattern, content, re.DOTALL)

            for match in matches:
                try:
                    parsed = json.loads(match)
                    # Prefer mappings or settings objects
                    if "mappings" in parsed or "settings" in parsed or "query" in parsed:
                        return parsed
                except json.JSONDecodeError:
                    continue

            # Return first valid JSON found
            if matches:
                try:
                    return json.loads(matches[0])
                except json.JSONDecodeError:
                    pass

        return None

    def _check_has_mappings(self, schema: Dict[str, Any]) -> bool:
        """Check if schema has mappings section"""
        return "mappings" in schema or "properties" in schema

    def _check_vector_field(self, schema: Dict[str, Any]) -> bool:
        """Check if schema has properly configured vector field"""
        properties = schema.get("mappings", {}).get("properties", schema.get("properties", {}))

        for field_name, field_config in properties.items():
            if isinstance(field_config, dict):
                field_type = field_config.get("type")
                if field_type == "dense_vector":
                    dims = field_config.get("dims")
                    similarity = field_config.get("similarity")
                    # Check for 384 dimensions and cosine similarity
                    if dims == 384 and similarity == "cosine":
                        return True

        return False

    def _check_settings(self, schema: Dict[str, Any]) -> bool:
        """Check if schema has settings section"""
        if "settings" not in schema:
            return False

        settings = schema["settings"]
        # Check for basic settings
        has_shards = "number_of_shards" in settings
        has_replicas = "number_of_replicas" in settings

        return has_shards or has_replicas

    def _check_field_types(self, schema: Dict[str, Any]) -> bool:
        """Check if field types are valid"""
        valid_types = {
            "text", "keyword", "long", "integer", "short", "byte",
            "double", "float", "date", "boolean", "binary",
            "dense_vector", "nested", "object", "geo_point", "geo_shape",
            "ip", "completion", "token_count", "percolator"
        }

        properties = schema.get("mappings", {}).get("properties", schema.get("properties", {}))

        for field_config in properties.values():
            if isinstance(field_config, dict):
                field_type = field_config.get("type")
                if field_type and field_type not in valid_types:
                    return False

        return True

    def _check_keyword_subfields(self, schema: Dict[str, Any]) -> bool:
        """Check if text fields have keyword subfields"""
        properties = schema.get("mappings", {}).get("properties", schema.get("properties", {}))

        # At least one text field should have a keyword subfield
        for field_config in properties.values():
            if isinstance(field_config, dict):
                if field_config.get("type") == "text":
                    fields = field_config.get("fields", {})
                    if "keyword" in fields:
                        return True

        return True  # Don't fail if no text fields

    def _check_criterion(self, schema: Dict[str, Any], criterion: str, expected: Any) -> bool:
        """Check specific criterion"""
        if criterion == "has_embedding_field":
            return self._check_vector_field(schema)
        elif criterion == "has_date_fields":
            properties = schema.get("mappings", {}).get("properties", schema.get("properties", {}))
            return any(
                field.get("type") == "date"
                for field in properties.values()
                if isinstance(field, dict)
            )
        return True
