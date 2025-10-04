"""
AI Configuration and Model Management for Planning Explorer
"""
from typing import Dict, Any, Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"


class AIModel(str, Enum):
    """Supported AI models"""
    # OpenAI Models
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"

    # Anthropic Models
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"

    # Sentence Transformers
    SENTENCE_TRANSFORMER = "sentence-transformers/all-MiniLM-L6-v2"


class AIConfigSettings(BaseSettings):
    """AI-specific configuration settings"""

    # API Keys
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")

    # Model Selection
    default_llm_provider: AIProvider = AIProvider.OPENAI
    default_llm_model: AIModel = AIModel.GPT_4
    default_embedding_model: AIModel = AIModel.TEXT_EMBEDDING_3_LARGE
    summarization_model: AIModel = AIModel.CLAUDE_3_5_SONNET

    # Performance Settings
    max_tokens_completion: int = 4000
    max_tokens_embedding: int = 8191
    temperature: float = 0.1
    top_p: float = 0.9

    # Rate Limiting
    requests_per_minute_openai: int = 50
    requests_per_minute_anthropic: int = 30
    tokens_per_minute_openai: int = 100000
    tokens_per_minute_anthropic: int = 80000

    # Timeout Settings
    api_timeout_seconds: int = 30
    embedding_timeout_seconds: int = 10

    # Retry Configuration
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    exponential_backoff: bool = True

    # Caching
    enable_response_caching: bool = True
    cache_ttl_hours: int = 24

    # Vector Embeddings
    embedding_dimensions: int = 1536  # text-embedding-3-large
    embedding_batch_size: int = 100
    embedding_similarity_threshold: float = 0.8

    # Performance Targets
    opportunity_scoring_timeout_ms: int = 2000
    summarization_timeout_ms: int = 3000
    embedding_timeout_ms: int = 1000
    batch_processing_rate: int = 100  # applications per minute

    # Quality Thresholds
    min_confidence_score: float = 0.7
    accuracy_target: float = 0.85

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env file


class ModelConfig:
    """Configuration for individual AI models"""

    def __init__(
        self,
        provider: AIProvider,
        model: AIModel,
        max_tokens: int = 4000,
        temperature: float = 0.1,
        top_p: float = 0.9,
        timeout: int = 30,
        cost_per_1k_tokens: float = 0.01
    ):
        self.provider = provider
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.timeout = timeout
        self.cost_per_1k_tokens = cost_per_1k_tokens


class AIConfigManager:
    """Centralized AI configuration management"""

    def __init__(self):
        self.settings = AIConfigSettings()
        self._model_configs = self._initialize_model_configs()
        self._validate_configuration()

    def _initialize_model_configs(self) -> Dict[AIModel, ModelConfig]:
        """Initialize configuration for all supported models"""
        return {
            # OpenAI Models
            AIModel.GPT_4: ModelConfig(
                provider=AIProvider.OPENAI,
                model=AIModel.GPT_4,
                max_tokens=4000,
                temperature=0.1,
                cost_per_1k_tokens=0.03
            ),
            AIModel.GPT_4_TURBO: ModelConfig(
                provider=AIProvider.OPENAI,
                model=AIModel.GPT_4_TURBO,
                max_tokens=4000,
                temperature=0.1,
                cost_per_1k_tokens=0.01
            ),
            AIModel.GPT_3_5_TURBO: ModelConfig(
                provider=AIProvider.OPENAI,
                model=AIModel.GPT_3_5_TURBO,
                max_tokens=4000,
                temperature=0.1,
                cost_per_1k_tokens=0.002
            ),
            AIModel.TEXT_EMBEDDING_3_LARGE: ModelConfig(
                provider=AIProvider.OPENAI,
                model=AIModel.TEXT_EMBEDDING_3_LARGE,
                max_tokens=8191,
                timeout=10,
                cost_per_1k_tokens=0.00013
            ),
            AIModel.TEXT_EMBEDDING_3_SMALL: ModelConfig(
                provider=AIProvider.OPENAI,
                model=AIModel.TEXT_EMBEDDING_3_SMALL,
                max_tokens=8191,
                timeout=10,
                cost_per_1k_tokens=0.00002
            ),

            # Anthropic Models
            AIModel.CLAUDE_3_5_SONNET: ModelConfig(
                provider=AIProvider.ANTHROPIC,
                model=AIModel.CLAUDE_3_5_SONNET,
                max_tokens=4000,
                temperature=0.1,
                cost_per_1k_tokens=0.015
            ),
            AIModel.CLAUDE_3_HAIKU: ModelConfig(
                provider=AIProvider.ANTHROPIC,
                model=AIModel.CLAUDE_3_HAIKU,
                max_tokens=4000,
                temperature=0.1,
                cost_per_1k_tokens=0.0008
            ),

            # Sentence Transformers
            AIModel.SENTENCE_TRANSFORMER: ModelConfig(
                provider=AIProvider.HUGGINGFACE,
                model=AIModel.SENTENCE_TRANSFORMER,
                max_tokens=512,
                timeout=5,
                cost_per_1k_tokens=0.0  # Free for local inference
            )
        }

    def _validate_configuration(self) -> None:
        """Validate AI configuration and API keys"""
        errors = []

        # Check API keys
        if not self.settings.openai_api_key:
            logger.warning("OpenAI API key not configured")
            errors.append("Missing OpenAI API key")

        if not self.settings.anthropic_api_key:
            logger.warning("Anthropic API key not configured")
            errors.append("Missing Anthropic API key")

        # Validate performance targets
        if self.settings.opportunity_scoring_timeout_ms > 5000:
            logger.warning("Opportunity scoring timeout is high - may impact user experience")

        if self.settings.accuracy_target < 0.8:
            logger.warning("Accuracy target is below recommended threshold of 80%")

        if errors and not any([self.settings.openai_api_key, self.settings.anthropic_api_key]):
            logger.error("No AI provider API keys configured - AI features will be disabled")

    def get_model_config(self, model: AIModel) -> ModelConfig:
        """Get configuration for a specific model"""
        return self._model_configs.get(model)

    def get_provider_models(self, provider: AIProvider) -> List[AIModel]:
        """Get all models for a specific provider"""
        return [
            model for model, config in self._model_configs.items()
            if config.provider == provider
        ]

    def is_provider_available(self, provider: AIProvider) -> bool:
        """Check if a provider is available (has API key configured)"""
        if provider == AIProvider.OPENAI:
            return bool(self.settings.openai_api_key)
        elif provider == AIProvider.ANTHROPIC:
            return bool(self.settings.anthropic_api_key)
        elif provider == AIProvider.HUGGINGFACE:
            return True  # No API key required for sentence transformers
        return False

    def get_embedding_config(self) -> ModelConfig:
        """Get configuration for embedding model"""
        return self.get_model_config(self.settings.default_embedding_model)

    def get_llm_config(self) -> ModelConfig:
        """Get configuration for default LLM"""
        return self.get_model_config(self.settings.default_llm_model)

    def get_summarization_config(self) -> ModelConfig:
        """Get configuration for summarization model"""
        return self.get_model_config(self.settings.summarization_model)

    def estimate_cost(self, model: AIModel, token_count: int) -> float:
        """Estimate cost for a request"""
        config = self.get_model_config(model)
        if not config:
            return 0.0
        return (token_count / 1000) * config.cost_per_1k_tokens

    def get_rate_limits(self, provider: AIProvider) -> Dict[str, int]:
        """Get rate limits for a provider"""
        if provider == AIProvider.OPENAI:
            return {
                "requests_per_minute": self.settings.requests_per_minute_openai,
                "tokens_per_minute": self.settings.tokens_per_minute_openai
            }
        elif provider == AIProvider.ANTHROPIC:
            return {
                "requests_per_minute": self.settings.requests_per_minute_anthropic,
                "tokens_per_minute": self.settings.tokens_per_minute_anthropic
            }
        return {"requests_per_minute": 1000, "tokens_per_minute": 1000000}  # Default for local models

    def get_performance_targets(self) -> Dict[str, int]:
        """Get performance targets in milliseconds"""
        return {
            "opportunity_scoring": self.settings.opportunity_scoring_timeout_ms,
            "summarization": self.settings.summarization_timeout_ms,
            "embedding": self.settings.embedding_timeout_ms
        }

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return {
            "providers": {
                "openai": {
                    "available": self.is_provider_available(AIProvider.OPENAI),
                    "models": [model.value for model in self.get_provider_models(AIProvider.OPENAI)]
                },
                "anthropic": {
                    "available": self.is_provider_available(AIProvider.ANTHROPIC),
                    "models": [model.value for model in self.get_provider_models(AIProvider.ANTHROPIC)]
                },
                "huggingface": {
                    "available": self.is_provider_available(AIProvider.HUGGINGFACE),
                    "models": [model.value for model in self.get_provider_models(AIProvider.HUGGINGFACE)]
                }
            },
            "default_models": {
                "llm": self.settings.default_llm_model.value,
                "embedding": self.settings.default_embedding_model.value,
                "summarization": self.settings.summarization_model.value
            },
            "performance_targets": self.get_performance_targets(),
            "quality_thresholds": {
                "min_confidence": self.settings.min_confidence_score,
                "accuracy_target": self.settings.accuracy_target
            }
        }


# Global AI configuration instance
ai_config = AIConfigManager()