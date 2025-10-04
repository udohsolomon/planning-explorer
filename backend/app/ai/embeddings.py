"""
Vector Embeddings Service for Semantic Search and Similarity Matching

This module provides comprehensive vector embedding generation and management
for planning applications, enabling semantic search, similarity matching,
and AI-powered discovery capabilities.
"""

import asyncio
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np
import openai
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False
import json
from datetime import datetime

from app.core.ai_config import ai_config, AIModel, AIProvider
from app.models.planning import PlanningApplication

logger = logging.getLogger(__name__)


class EmbeddingType(str, Enum):
    """Types of embeddings that can be generated"""
    DOCUMENT = "document"           # Full document embeddings
    DESCRIPTION = "description"     # Application description only
    LOCATION = "location"          # Geographic/location-based
    METADATA = "metadata"          # Structured metadata
    COMBINED = "combined"          # Multi-modal embeddings


class EmbeddingModel(str, Enum):
    """Available embedding models"""
    OPENAI_LARGE = "text-embedding-3-large"
    OPENAI_SMALL = "text-embedding-3-small"
    SENTENCE_TRANSFORMER = "sentence-transformers/all-MiniLM-L6-v2"
    PLANNING_SPECIFIC = "planning-specialized-v1"  # Future custom model


@dataclass
class EmbeddingResult:
    """Result of embedding generation"""
    embedding: List[float]
    dimensions: int
    model_used: str
    processing_time_ms: int
    text_hash: str
    metadata: Dict[str, Any]
    confidence_score: float
    token_count: int


@dataclass
class SimilarityResult:
    """Result of similarity search"""
    application_id: str
    similarity_score: float
    embedding_type: EmbeddingType
    matched_content: str
    metadata: Dict[str, Any]


@dataclass
class SemanticSearchResult:
    """Result of semantic search query"""
    query: str
    results: List[SimilarityResult]
    processing_time_ms: int
    total_searched: int
    similarity_threshold: float
    model_used: str


class EmbeddingService:
    """
    Comprehensive vector embedding service for planning applications.

    Provides semantic search, similarity matching, and content discovery
    capabilities using state-of-the-art embedding models.
    """

    def __init__(self):
        self.config = ai_config
        self._initialize_models()
        self._cache = {}  # Simple in-memory cache
        self.similarity_threshold = 0.8

    def _initialize_models(self) -> None:
        """Initialize embedding models"""
        self.openai_client = None
        self.sentence_transformer = None

        # Initialize OpenAI client for embeddings
        if self.config.settings.openai_api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=self.config.settings.openai_api_key)
            logger.info("OpenAI embedding client initialized")

        # Initialize Sentence Transformer model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Sentence Transformer model loaded")
            except Exception as e:
                logger.warning(f"Failed to load Sentence Transformer: {e}")
                self.sentence_transformer = None
        else:
            logger.info("Sentence Transformers not available - using OpenAI embeddings only")
            self.sentence_transformer = None

        if not self.openai_client and not self.sentence_transformer:
            logger.error("No embedding models available")

    async def generate_application_embedding(
        self,
        application: PlanningApplication,
        embedding_type: EmbeddingType = EmbeddingType.COMBINED,
        model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL
    ) -> EmbeddingResult:
        """
        Generate vector embedding for a planning application.

        Args:
            application: Planning application to embed
            embedding_type: Type of embedding to generate
            model: Embedding model to use

        Returns:
            EmbeddingResult with vector and metadata
        """
        start_time = time.time()

        try:
            # Prepare text content based on embedding type
            text_content = self._prepare_text_for_embedding(application, embedding_type)

            # Generate cache key
            cache_key = self._generate_cache_key(text_content, model.value)

            # Check cache first
            if cache_key in self._cache:
                cached_result = self._cache[cache_key]
                logger.debug(f"Cache hit for embedding: {application.application_id}")
                return cached_result

            # Generate embedding using selected model
            if model in [EmbeddingModel.OPENAI_LARGE, EmbeddingModel.OPENAI_SMALL]:
                embedding_result = await self._generate_openai_embedding(text_content, model)
            elif model == EmbeddingModel.SENTENCE_TRANSFORMER:
                embedding_result = await self._generate_sentence_transformer_embedding(text_content)
            else:
                raise ValueError(f"Unsupported embedding model: {model}")

            # Add metadata
            embedding_result.metadata.update({
                "application_id": application.application_id,
                "embedding_type": embedding_type.value,
                "development_type": application.development_type,
                "authority": application.authority,
                "status": application.status,
                "created_at": datetime.utcnow().isoformat()
            })

            processing_time_ms = int((time.time() - start_time) * 1000)
            embedding_result.processing_time_ms = processing_time_ms

            # Cache result
            self._cache[cache_key] = embedding_result

            logger.info(f"Generated {embedding_type.value} embedding for application {application.application_id} in {processing_time_ms}ms")
            return embedding_result

        except Exception as e:
            logger.error(f"Error generating embedding for application {application.application_id}: {str(e)}")
            return self._generate_fallback_embedding(application, embedding_type)

    def _prepare_text_for_embedding(
        self,
        application: PlanningApplication,
        embedding_type: EmbeddingType
    ) -> str:
        """Prepare text content based on embedding type"""

        if embedding_type == EmbeddingType.DESCRIPTION:
            return application.description or "No description available"

        elif embedding_type == EmbeddingType.LOCATION:
            location_parts = []
            if application.address:
                location_parts.append(application.address)
            if application.authority:
                location_parts.append(f"Authority: {application.authority}")
            if hasattr(application, 'ward') and application.ward:
                location_parts.append(f"Ward: {application.ward}")
            if hasattr(application, 'parish') and application.parish:
                location_parts.append(f"Parish: {application.parish}")
            return " ".join(location_parts) or "Location not specified"

        elif embedding_type == EmbeddingType.METADATA:
            metadata_parts = []
            metadata_parts.append(f"Development type: {application.development_type}")
            metadata_parts.append(f"Status: {application.status}")
            if hasattr(application, 'case_officer') and application.case_officer:
                metadata_parts.append(f"Case officer: {application.case_officer}")
            if hasattr(application, 'agent') and application.agent:
                metadata_parts.append(f"Agent: {application.agent}")
            return " ".join(metadata_parts)

        elif embedding_type == EmbeddingType.DOCUMENT:
            # Full document content
            parts = []
            if application.description:
                parts.append(application.description)
            if application.proposal:
                parts.append(application.proposal)
            return " ".join(parts) or "No document content available"

        else:  # COMBINED
            # Comprehensive combined embedding
            combined_parts = []

            # Basic info
            combined_parts.append(f"Planning application {application.application_id}")
            combined_parts.append(f"Development type: {application.development_type}")
            combined_parts.append(f"Location: {application.address}")
            combined_parts.append(f"Authority: {application.authority}")
            combined_parts.append(f"Status: {application.status}")

            # Description and proposal
            if application.description:
                combined_parts.append(f"Description: {application.description}")
            if application.proposal:
                combined_parts.append(f"Proposal: {application.proposal}")

            # Additional fields
            for field in ['ward', 'parish', 'case_officer', 'agent', 'applicant']:
                value = getattr(application, field, None)
                if value:
                    combined_parts.append(f"{field.replace('_', ' ').title()}: {value}")

            return " ".join(combined_parts)

    async def _generate_openai_embedding(
        self,
        text: str,
        model: EmbeddingModel
    ) -> EmbeddingResult:
        """Generate embedding using OpenAI API"""
        if not self.openai_client:
            raise ValueError("OpenAI client not available")

        try:
            response = await self.openai_client.embeddings.create(
                model=model.value,
                input=text,
                encoding_format="float"
            )

            embedding = response.data[0].embedding
            text_hash = hashlib.md5(text.encode()).hexdigest()

            return EmbeddingResult(
                embedding=embedding,
                dimensions=len(embedding),
                model_used=model.value,
                processing_time_ms=0,  # Will be set by caller
                text_hash=text_hash,
                metadata={"text_length": len(text)},
                confidence_score=0.95,  # High confidence for OpenAI models
                token_count=response.usage.total_tokens
            )

        except Exception as e:
            logger.error(f"OpenAI embedding error: {str(e)}")
            raise

    async def _generate_sentence_transformer_embedding(self, text: str) -> EmbeddingResult:
        """Generate embedding using Sentence Transformer"""
        if not self.sentence_transformer:
            raise ValueError("Sentence Transformer not available")

        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                self.sentence_transformer.encode,
                text
            )

            embedding_list = embedding.tolist()
            text_hash = hashlib.md5(text.encode()).hexdigest()

            return EmbeddingResult(
                embedding=embedding_list,
                dimensions=len(embedding_list),
                model_used="sentence-transformers/all-MiniLM-L6-v2",
                processing_time_ms=0,  # Will be set by caller
                text_hash=text_hash,
                metadata={"text_length": len(text)},
                confidence_score=0.85,  # Good confidence for sentence transformers
                token_count=len(text.split())  # Approximate token count
            )

        except Exception as e:
            logger.error(f"Sentence Transformer embedding error: {str(e)}")
            raise

    def _generate_cache_key(self, text: str, model: str) -> str:
        """Generate cache key for text and model combination"""
        combined = f"{text}:{model}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _generate_fallback_embedding(
        self,
        application: PlanningApplication,
        embedding_type: EmbeddingType
    ) -> EmbeddingResult:
        """Generate simple fallback embedding when models fail"""
        logger.warning(f"Using fallback embedding for application {application.application_id}")

        # Create a simple hash-based embedding
        text_content = self._prepare_text_for_embedding(application, embedding_type)
        text_hash = hashlib.md5(text_content.encode()).hexdigest()

        # Convert hash to pseudo-embedding (fixed dimensions)
        embedding_dims = 384  # Common embedding dimension
        hash_bytes = bytes.fromhex(text_hash)
        embedding = []

        for i in range(embedding_dims):
            byte_index = i % len(hash_bytes)
            embedding.append((hash_bytes[byte_index] - 128) / 128.0)  # Normalize to [-1, 1]

        return EmbeddingResult(
            embedding=embedding,
            dimensions=embedding_dims,
            model_used="fallback-hash",
            processing_time_ms=10,
            text_hash=text_hash,
            metadata={"application_id": application.application_id, "text_length": len(text_content)},
            confidence_score=0.3,  # Low confidence for fallback
            token_count=len(text_content.split())
        )

    async def semantic_search(
        self,
        query: str,
        applications: List[PlanningApplication],
        embedding_type: EmbeddingType = EmbeddingType.COMBINED,
        similarity_threshold: float = None,
        max_results: int = 10
    ) -> SemanticSearchResult:
        """
        Perform semantic search across planning applications.

        Args:
            query: Search query text
            applications: List of applications to search
            embedding_type: Type of embedding to use for comparison
            similarity_threshold: Minimum similarity score (default: 0.8)
            max_results: Maximum number of results to return

        Returns:
            SemanticSearchResult with ranked matches
        """
        start_time = time.time()
        threshold = similarity_threshold or self.similarity_threshold

        try:
            # Generate query embedding
            query_embedding = await self._generate_query_embedding(query)

            # Generate embeddings for all applications
            tasks = [
                self.generate_application_embedding(app, embedding_type)
                for app in applications
            ]
            app_embeddings = await asyncio.gather(*tasks, return_exceptions=True)

            # Calculate similarities
            similarities = []
            for i, app_embedding in enumerate(app_embeddings):
                if isinstance(app_embedding, Exception):
                    logger.warning(f"Failed to embed application {applications[i].id}: {app_embedding}")
                    continue

                similarity = self._calculate_cosine_similarity(
                    query_embedding.embedding,
                    app_embedding.embedding
                )

                if similarity >= threshold:
                    similarities.append(SimilarityResult(
                        application_id=applications[i].id,
                        similarity_score=similarity,
                        embedding_type=embedding_type,
                        matched_content=self._prepare_text_for_embedding(applications[i], embedding_type)[:200],
                        metadata=app_embedding.metadata
                    ))

            # Sort by similarity score (descending)
            similarities.sort(key=lambda x: x.similarity_score, reverse=True)

            # Limit results
            similarities = similarities[:max_results]

            processing_time_ms = int((time.time() - start_time) * 1000)

            return SemanticSearchResult(
                query=query,
                results=similarities,
                processing_time_ms=processing_time_ms,
                total_searched=len(applications),
                similarity_threshold=threshold,
                model_used=query_embedding.model_used
            )

        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return SemanticSearchResult(
                query=query,
                results=[],
                processing_time_ms=int((time.time() - start_time) * 1000),
                total_searched=len(applications),
                similarity_threshold=threshold,
                model_used="error"
            )

    async def generate_text_embedding(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for any text (public method for search service)

        Args:
            text: Text to embed (query, description, etc.)

        Returns:
            EmbeddingResult with vector and metadata
        """
        # Use OPENAI_SMALL (1536 dimensions) to match ES index schema
        if self.openai_client:
            return await self._generate_openai_embedding(text, EmbeddingModel.OPENAI_SMALL)
        elif self.sentence_transformer:
            return await self._generate_sentence_transformer_embedding(text)
        else:
            raise ValueError("No embedding models available for text")

    async def _generate_query_embedding(self, query: str) -> EmbeddingResult:
        """Generate embedding for search query (internal method)"""
        return await self.generate_text_embedding(query)

    def _calculate_cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            a = np.array(embedding1)
            b = np.array(embedding2)

            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)

            if norm_a == 0 or norm_b == 0:
                return 0.0

            similarity = dot_product / (norm_a * norm_b)
            return float(similarity)

        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0

    async def find_similar_applications(
        self,
        target_application: PlanningApplication,
        candidate_applications: List[PlanningApplication],
        embedding_type: EmbeddingType = EmbeddingType.COMBINED,
        similarity_threshold: float = None,
        max_results: int = 5
    ) -> List[SimilarityResult]:
        """
        Find applications similar to a target application.

        Args:
            target_application: Application to find matches for
            candidate_applications: Pool of applications to search
            embedding_type: Type of embedding for comparison
            similarity_threshold: Minimum similarity score
            max_results: Maximum number of results

        Returns:
            List of similar applications ranked by similarity
        """
        threshold = similarity_threshold or self.similarity_threshold

        try:
            # Generate embedding for target application
            target_embedding = await self.generate_application_embedding(
                target_application, embedding_type
            )

            # Generate embeddings for candidates
            tasks = [
                self.generate_application_embedding(app, embedding_type)
                for app in candidate_applications
                if app.id != target_application.application_id  # Exclude self
            ]
            candidate_embeddings = await asyncio.gather(*tasks, return_exceptions=True)

            # Calculate similarities
            similarities = []
            for i, candidate_embedding in enumerate(candidate_embeddings):
                if isinstance(candidate_embedding, Exception):
                    continue

                similarity = self._calculate_cosine_similarity(
                    target_embedding.embedding,
                    candidate_embedding.embedding
                )

                if similarity >= threshold:
                    similarities.append(SimilarityResult(
                        application_id=candidate_applications[i].id,
                        similarity_score=similarity,
                        embedding_type=embedding_type,
                        matched_content=self._prepare_text_for_embedding(
                            candidate_applications[i], embedding_type
                        )[:200],
                        metadata=candidate_embedding.metadata
                    ))

            # Sort and limit results
            similarities.sort(key=lambda x: x.similarity_score, reverse=True)
            return similarities[:max_results]

        except Exception as e:
            logger.error(f"Error finding similar applications: {str(e)}")
            return []

    async def batch_generate_embeddings(
        self,
        applications: List[PlanningApplication],
        embedding_type: EmbeddingType = EmbeddingType.COMBINED,
        model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL,
        max_concurrent: int = 10
    ) -> List[EmbeddingResult]:
        """Generate embeddings for multiple applications concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def embed_with_semaphore(app):
            async with semaphore:
                return await self.generate_application_embedding(app, embedding_type, model)

        tasks = [embed_with_semaphore(app) for app in applications]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error embedding application {applications[i].id}: {result}")
                processed_results.append(
                    self._generate_fallback_embedding(applications[i], embedding_type)
                )
            else:
                processed_results.append(result)

        return processed_results

    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about embedding service usage"""
        return {
            "cache_size": len(self._cache),
            "models_available": {
                "openai": bool(self.openai_client),
                "sentence_transformer": bool(self.sentence_transformer)
            },
            "similarity_threshold": self.similarity_threshold,
            "supported_embedding_types": [t.value for t in EmbeddingType],
            "supported_models": [m.value for m in EmbeddingModel]
        }

    def clear_cache(self) -> None:
        """Clear embedding cache"""
        self._cache.clear()
        logger.info("Embedding cache cleared")

    def set_similarity_threshold(self, threshold: float) -> None:
        """Set similarity threshold for searches"""
        if 0.0 <= threshold <= 1.0:
            self.similarity_threshold = threshold
            logger.info(f"Similarity threshold set to {threshold}")
        else:
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")