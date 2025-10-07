"""
Elasticsearch Tools

Tools for querying, indexing, and managing Elasticsearch data.
Enables agents to interact with the Planning Explorer ES index.
"""

import json
from typing import Any, List, Dict, Optional
from elasticsearch import AsyncElasticsearch

from .base_tool import BaseTool, ToolParameter
from app.core.config import settings


class ElasticsearchQueryTool(BaseTool):
    """Execute Elasticsearch queries"""

    def __init__(self):
        super().__init__()
        self.es_client: Optional[AsyncElasticsearch] = None

    def get_name(self) -> str:
        return "elasticsearch_query"

    def get_description(self) -> str:
        return """Execute an Elasticsearch query against the planning_applications index.

Supports:
- Full-text search with keyword and semantic modes
- Filtering by authority, status, date ranges
- Aggregations for analytics
- Vector similarity search with embeddings"""

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                type="object",
                description="Elasticsearch query DSL (JSON object)",
                required=True
            ),
            ToolParameter(
                name="index",
                type="string",
                description=f"Index name (default: {settings.elasticsearch_index})",
                required=False,
                default=settings.elasticsearch_index
            ),
            ToolParameter(
                name="size",
                type="number",
                description="Number of results to return (default: 10)",
                required=False,
                default=10
            ),
            ToolParameter(
                name="from_",
                type="number",
                description="Offset for pagination (default: 0)",
                required=False,
                default=0
            ),
            ToolParameter(
                name="include_aggregations",
                type="boolean",
                description="Include aggregation results",
                required=False,
                default=False
            )
        ]

    async def execute(
        self,
        query: Dict[str, Any],
        index: str = None,
        size: int = 10,
        from_: int = 0,
        include_aggregations: bool = False
    ) -> Any:
        """
        Execute Elasticsearch query.

        Args:
            query: ES query DSL
            index: Index name
            size: Results limit
            from_: Pagination offset
            include_aggregations: Include aggs in response

        Returns:
            Query results with hits and optional aggregations
        """
        self.validate_parameters(query=query)

        try:
            # Use default index if none provided
            if not index:
                index = settings.elasticsearch_index

            # Initialize ES client if needed
            if not self.es_client:
                self.es_client = AsyncElasticsearch(
                    hosts=[settings.ELASTICSEARCH_URL],
                    verify_certs=False
                )

            # Build search body
            body = {
                "query": query,
                "size": size,
                "from": from_
            }

            # Add aggregations if requested
            if include_aggregations:
                body["aggs"] = self._get_default_aggregations()

            # Execute search
            response = await self.es_client.search(
                index=index,
                body=body
            )

            # Format results
            hits = []
            for hit in response["hits"]["hits"]:
                hits.append({
                    "id": hit["_id"],
                    "score": hit.get("_score"),
                    "source": hit["_source"]
                })

            result = {
                "success": True,
                "total": response["hits"]["total"]["value"],
                "hits": hits,
                "took_ms": response["took"]
            }

            # Add aggregations if present
            if "aggregations" in response:
                result["aggregations"] = response["aggregations"]

            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"Elasticsearch query failed: {str(e)}",
                "query": query
            }

    def _get_default_aggregations(self) -> Dict[str, Any]:
        """Get default aggregations for planning data"""
        return {
            "by_authority": {
                "terms": {
                    "field": "authority.keyword",
                    "size": 20
                }
            },
            "by_status": {
                "terms": {
                    "field": "status.keyword",
                    "size": 10
                }
            },
            "by_development_type": {
                "terms": {
                    "field": "development_type.keyword",
                    "size": 15
                }
            },
            "date_histogram": {
                "date_histogram": {
                    "field": "decision_date",
                    "calendar_interval": "month"
                }
            }
        }


class ElasticsearchIndexTool(BaseTool):
    """Index or update documents in Elasticsearch"""

    def __init__(self):
        super().__init__()
        self.es_client: Optional[AsyncElasticsearch] = None

    def get_name(self) -> str:
        return "elasticsearch_index"

    def get_description(self) -> str:
        return "Index or update a document in Elasticsearch"

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="document",
                type="object",
                description="Document to index (JSON object)",
                required=True
            ),
            ToolParameter(
                name="index",
                type="string",
                description="Index name",
                required=True
            ),
            ToolParameter(
                name="doc_id",
                type="string",
                description="Document ID (optional, auto-generated if not provided)",
                required=False
            ),
            ToolParameter(
                name="operation",
                type="string",
                description="Operation type: index, create, update",
                required=False,
                enum=["index", "create", "update"],
                default="index"
            )
        ]

    async def execute(
        self,
        document: Dict[str, Any],
        index: str,
        doc_id: Optional[str] = None,
        operation: str = "index"
    ) -> Any:
        """
        Index or update document.

        Args:
            document: Document data
            index: Index name
            doc_id: Document ID (optional)
            operation: index, create, or update

        Returns:
            Indexing result
        """
        self.validate_parameters(document=document, index=index)

        try:
            # Initialize ES client if needed
            if not self.es_client:
                self.es_client = AsyncElasticsearch(
                    hosts=[settings.ELASTICSEARCH_URL],
                    verify_certs=False
                )

            # Execute operation
            if operation == "create":
                response = await self.es_client.create(
                    index=index,
                    id=doc_id,
                    document=document
                )
            elif operation == "update":
                if not doc_id:
                    return {
                        "success": False,
                        "error": "Document ID required for update operation"
                    }
                response = await self.es_client.update(
                    index=index,
                    id=doc_id,
                    doc=document
                )
            else:  # index
                response = await self.es_client.index(
                    index=index,
                    id=doc_id,
                    document=document
                )

            return {
                "success": True,
                "operation": operation,
                "index": index,
                "doc_id": response["_id"],
                "result": response["result"],
                "version": response.get("_version")
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Elasticsearch indexing failed: {str(e)}",
                "operation": operation,
                "index": index
            }


class ElasticsearchBulkTool(BaseTool):
    """Bulk index multiple documents"""

    def __init__(self):
        super().__init__()
        self.es_client: Optional[AsyncElasticsearch] = None

    def get_name(self) -> str:
        return "elasticsearch_bulk"

    def get_description(self) -> str:
        return "Bulk index multiple documents efficiently"

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="documents",
                type="array",
                description="Array of documents to index",
                required=True
            ),
            ToolParameter(
                name="index",
                type="string",
                description="Index name",
                required=True
            )
        ]

    async def execute(
        self,
        documents: List[Dict[str, Any]],
        index: str
    ) -> Any:
        """
        Bulk index documents.

        Args:
            documents: List of documents
            index: Index name

        Returns:
            Bulk indexing results
        """
        self.validate_parameters(documents=documents, index=index)

        try:
            # Initialize ES client if needed
            if not self.es_client:
                self.es_client = AsyncElasticsearch(
                    hosts=[settings.ELASTICSEARCH_URL],
                    verify_certs=False
                )

            # Build bulk operations
            operations = []
            for doc in documents:
                # Add index action
                operations.append({"index": {"_index": index}})
                # Add document
                operations.append(doc)

            # Execute bulk
            response = await self.es_client.bulk(operations=operations)

            # Count successes and failures
            items = response.get("items", [])
            successes = sum(1 for item in items if not item.get("index", {}).get("error"))
            failures = len(items) - successes

            return {
                "success": failures == 0,
                "total": len(documents),
                "indexed": successes,
                "failed": failures,
                "took_ms": response.get("took"),
                "errors": response.get("errors", False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Bulk indexing failed: {str(e)}",
                "total": len(documents)
            }


class ElasticsearchDeleteTool(BaseTool):
    """Delete documents from Elasticsearch"""

    def __init__(self):
        super().__init__()
        self.es_client: Optional[AsyncElasticsearch] = None

    def get_name(self) -> str:
        return "elasticsearch_delete"

    def get_description(self) -> str:
        return "Delete a document from Elasticsearch by ID"

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="doc_id",
                type="string",
                description="Document ID to delete",
                required=True
            ),
            ToolParameter(
                name="index",
                type="string",
                description="Index name",
                required=True
            )
        ]

    async def execute(
        self,
        doc_id: str,
        index: str
    ) -> Any:
        """Delete document by ID"""
        self.validate_parameters(doc_id=doc_id, index=index)

        try:
            if not self.es_client:
                self.es_client = AsyncElasticsearch(
                    hosts=[settings.ELASTICSEARCH_URL],
                    verify_certs=False
                )

            response = await self.es_client.delete(
                index=index,
                id=doc_id
            )

            return {
                "success": True,
                "index": index,
                "doc_id": doc_id,
                "result": response["result"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Delete failed: {str(e)}",
                "doc_id": doc_id,
                "index": index
            }
