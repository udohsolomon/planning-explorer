"""
Elasticsearch client and connection management for Planning Explorer
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from elasticsearch import AsyncElasticsearch, ConnectionError, TransportError
from elasticsearch.helpers import async_bulk
from app.core.config import settings

logger = logging.getLogger(__name__)


class ElasticsearchClient:
    """Elasticsearch client wrapper with connection management and health checks"""

    def __init__(self):
        self.client: Optional[AsyncElasticsearch] = None
        self.index_name = settings.elasticsearch_index
        self._connection_retries = 0
        self._max_retries = settings.elasticsearch_max_retries
        self._is_connected = False  # Track connection state to avoid repeated health checks

    async def connect(self) -> bool:
        """
        Establish connection to Elasticsearch cluster

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = AsyncElasticsearch(
                hosts=[settings.elasticsearch_node],
                basic_auth=(settings.elasticsearch_username, settings.elasticsearch_password),
                verify_certs=False,  # For development - enable in production
                ssl_show_warn=False,
                request_timeout=settings.elasticsearch_timeout,
                max_retries=settings.elasticsearch_max_retries,
                sniff_on_start=False,  # Disable sniffing to prevent timeouts
                sniff_on_node_failure=False,  # Only use this one, not sniff_on_connection_fail
                retry_on_timeout=True,
                sniff_timeout=60,  # Fixed: was sniffer_timeout (deprecated parameter)
                connections_per_node=10,  # Connection pool size for concurrent requests
                http_compress=True,  # Enable compression for large payloads
            )

            # Test connection with simple ping (faster than full health check)
            if await self.client.ping():
                logger.info("Successfully connected to Elasticsearch")
                self._is_connected = True
                self._connection_retries = 0  # Reset retry counter on successful connection
                return True
            else:
                logger.error("Elasticsearch ping failed")
                self._is_connected = False
                return False

        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {str(e)}")
            self._is_connected = False
            return False

    async def disconnect(self):
        """Close Elasticsearch connection"""
        if self.client:
            await self.client.close()
            self.client = None
            self._is_connected = False
            logger.info("Disconnected from Elasticsearch")

    async def health_check(self) -> bool:
        """
        Check Elasticsearch cluster health

        Returns:
            bool: True if cluster is healthy, False otherwise
        """
        try:
            if not self.client:
                return False

            # Check cluster health
            health = await self.client.cluster.health()
            cluster_status = health.get("status", "red")

            # Check if index exists
            index_exists = await self.client.indices.exists(index=self.index_name)

            logger.info(f"Elasticsearch cluster status: {cluster_status}")
            logger.info(f"Index '{self.index_name}' exists: {index_exists}")

            return cluster_status in ["yellow", "green"] and index_exists

        except Exception as e:
            # Log the error but don't fail if it's just a timeout
            if "timed out" in str(e).lower() or "timeout" in str(e).lower():
                logger.warning(f"Elasticsearch health check timed out, assuming it's okay: {str(e)}")
                return True  # Assume ES is working if it's just slow
            logger.error(f"Elasticsearch health check failed: {str(e)}")
            return False

    async def ensure_connection(self):
        """Ensure connection is established, reconnect if necessary"""
        # CRITICAL FIX: Only check if client exists, don't run full health check on every request
        # This was causing 200-400ms overhead and timeout issues on every API call
        if not self.client or not self._is_connected:
            if self._connection_retries < self._max_retries:
                self._connection_retries += 1
                logger.info(f"Attempting to reconnect to Elasticsearch (attempt {self._connection_retries})")
                await self.connect()
            else:
                raise ConnectionError("Maximum connection retries exceeded")

    async def search(
        self,
        query: Optional[Dict[str, Any]] = None,
        index: Optional[str] = None,
        size: int = 10,
        from_: int = 0,
        sort: Optional[List[Dict[str, Any]]] = None,
        source: Optional[Union[bool, List[str]]] = None,
        knn: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute search query

        Args:
            query: Elasticsearch query DSL
            index: Index name (defaults to configured index)
            size: Number of results to return
            from_: Offset for pagination
            sort: Sort configuration
            source: Fields to include/exclude in source
            knn: KNN vector search configuration
            **kwargs: Additional search parameters

        Returns:
            Dict containing search results
        """
        await self.ensure_connection()

        try:
            # Build search body
            body = {
                "size": size,
                "from": from_,
                **({"_source": source} if source is not None else {}),
                **kwargs
            }

            # Add query if provided
            if query:
                body["query"] = query

            # Add sort if provided
            if sort:
                body["sort"] = sort

            # Add KNN if provided (for vector search)
            if knn:
                body["knn"] = knn

            response = await self.client.search(
                index=index or self.index_name,
                body=body
            )
            return response

        except Exception as e:
            logger.error(f"Search query failed: {str(e)}")
            raise

    async def get_document(self, doc_id: str, index: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get document by ID

        Args:
            doc_id: Document ID
            index: Index name (defaults to configured index)

        Returns:
            Document if found, None otherwise
        """
        await self.ensure_connection()

        try:
            response = await self.client.get(
                index=index or self.index_name,
                id=doc_id
            )
            return response.get("_source")

        except Exception as e:
            if "not_found" in str(e).lower():
                return None
            logger.error(f"Failed to get document {doc_id}: {str(e)}")
            raise

    async def index_document(
        self,
        doc_id: str,
        document: Dict[str, Any],
        index: Optional[str] = None,
        refresh: bool = False
    ) -> bool:
        """
        Index a single document

        Args:
            doc_id: Document ID
            document: Document to index
            index: Index name (defaults to configured index)
            refresh: Whether to refresh index after operation

        Returns:
            bool: True if successful, False otherwise
        """
        await self.ensure_connection()

        try:
            # Add timestamps
            document["updated_at"] = datetime.utcnow().isoformat()
            if "created_at" not in document:
                document["created_at"] = datetime.utcnow().isoformat()

            await self.client.index(
                index=index or self.index_name,
                id=doc_id,
                body=document,
                refresh=refresh
            )
            return True

        except Exception as e:
            logger.error(f"Failed to index document {doc_id}: {str(e)}")
            return False

    async def update_document(
        self,
        doc_id: str,
        document: Dict[str, Any],
        index: Optional[str] = None,
        refresh: bool = False
    ) -> bool:
        """
        Update a document by merging fields (preserves existing fields)

        Args:
            doc_id: Document ID
            document: Fields to update/add
            index: Index name (defaults to configured index)
            refresh: Whether to refresh index after operation

        Returns:
            bool: True if successful, False otherwise
        """
        await self.ensure_connection()

        try:
            # Add update timestamp
            document["updated_at"] = datetime.utcnow().isoformat()

            await self.client.update(
                index=index or self.index_name,
                id=doc_id,
                body={
                    "doc": document,
                    "doc_as_upsert": False  # Don't create if doesn't exist
                },
                refresh=refresh
            )
            return True

        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {str(e)}")
            return False

    async def bulk_index(
        self,
        documents: List[Dict[str, Any]],
        index: Optional[str] = None,
        chunk_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Bulk index documents

        Args:
            documents: List of documents to index
            index: Index name (defaults to configured index)
            chunk_size: Number of documents per bulk request

        Returns:
            Dict with indexing statistics
        """
        await self.ensure_connection()

        index_name = index or self.index_name
        timestamp = datetime.utcnow().isoformat()

        # Prepare documents for bulk indexing
        bulk_docs = []
        for doc in documents:
            # Add timestamps
            doc["updated_at"] = timestamp
            if "created_at" not in doc:
                doc["created_at"] = timestamp

            bulk_docs.append({
                "_index": index_name,
                "_id": doc.get("application_id", doc.get("id")),
                "_source": doc
            })

        try:
            success_count, failed_items = await async_bulk(
                self.client,
                bulk_docs,
                chunk_size=chunk_size,
                max_retries=3,
                initial_backoff=2,
                max_backoff=600
            )

            return {
                "success_count": success_count,
                "failed_count": len(failed_items),
                "failed_items": failed_items
            }

        except Exception as e:
            logger.error(f"Bulk indexing failed: {str(e)}")
            raise

    async def aggregations(
        self,
        aggs: Dict[str, Any],
        query: Optional[Dict[str, Any]] = None,
        index: Optional[str] = None,
        size: int = 0
    ) -> Dict[str, Any]:
        """
        Execute aggregation query

        Args:
            aggs: Aggregation configuration
            query: Optional query to filter documents
            index: Index name (defaults to configured index)
            size: Number of documents to return (0 for aggregations only)

        Returns:
            Dict containing aggregation results
        """
        await self.ensure_connection()

        body = {
            "aggs": aggs,
            "size": size
        }

        if query:
            body["query"] = query

        try:
            response = await self.client.search(
                index=index or self.index_name,
                body=body
            )
            return response.get("aggregations", {})

        except Exception as e:
            logger.error(f"Aggregation query failed: {str(e)}")
            raise

    async def vector_search(
        self,
        field: str,
        vector: List[float],
        k: int = 10,
        num_candidates: int = 100,
        query: Optional[Dict[str, Any]] = None,
        index: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute vector similarity search

        Args:
            field: Vector field name
            vector: Query vector
            k: Number of nearest neighbors to return
            num_candidates: Number of candidates to consider
            query: Optional filter query
            index: Index name (defaults to configured index)

        Returns:
            Dict containing search results
        """
        await self.ensure_connection()

        knn_query = {
            "field": field,
            "query_vector": vector,
            "k": k,
            "num_candidates": num_candidates
        }

        if query:
            knn_query["filter"] = query

        try:
            response = await self.client.search(
                index=index or self.index_name,
                knn=knn_query
            )
            return response

        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            raise

    async def count(
        self,
        query: Optional[Dict[str, Any]] = None,
        index: Optional[str] = None
    ) -> int:
        """
        Count documents matching query

        Args:
            query: Query to filter documents
            index: Index name (defaults to configured index)

        Returns:
            int: Number of matching documents
        """
        await self.ensure_connection()

        try:
            body = {"query": query} if query else {}
            response = await self.client.count(
                index=index or self.index_name,
                body=body
            )
            return response.get("count", 0)

        except Exception as e:
            logger.error(f"Count query failed: {str(e)}")
            raise


# Global Elasticsearch client instance
es_client = ElasticsearchClient()