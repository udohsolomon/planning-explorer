"""
AI Intelligence Layer for Planning Explorer

This module provides the complete AI processing pipeline including:
- Opportunity scoring algorithms
- Document summarization
- Vector embeddings generation
- Natural language processing
- Market intelligence analysis
- Advanced AI personalization system
- User behavior analytics
- Privacy-first learning system
"""

# Original AI modules
from .opportunity_scorer import OpportunityScorer
from .summarizer import DocumentSummarizer
from .embeddings import EmbeddingService
from .nlp_processor import NLPProcessor
from .market_intelligence import MarketIntelligenceEngine

# Advanced AI personalization modules
from .user_analytics import UserBehaviorAnalyzer, InteractionType, UserSegment
from .personalization_engine import PersonalizationEngine, RecommendationType, PersonalizationLevel
from .learning_system import LearningSystem, FeedbackType, LearningObjective
from .user_profiling import UserProfilingSystem, PersonaType, ExpertiseLevel
from .privacy_manager import PrivacyManager, ConsentType, DataCategory
from .personalization_integration import PersonalizedAI

__all__ = [
    # Original AI modules
    "OpportunityScorer",
    "DocumentSummarizer",
    "EmbeddingService",
    "NLPProcessor",
    "MarketIntelligenceEngine",

    # Advanced personalization modules
    "UserBehaviorAnalyzer",
    "PersonalizationEngine",
    "LearningSystem",
    "UserProfilingSystem",
    "PrivacyManager",
    "PersonalizedAI",

    # Enums and types
    "InteractionType",
    "UserSegment",
    "RecommendationType",
    "PersonalizationLevel",
    "FeedbackType",
    "LearningObjective",
    "PersonaType",
    "ExpertiseLevel",
    "ConsentType",
    "DataCategory"
]

__version__ = "3.0.0"  # Major version bump for personalization features

# AI Personalization Configuration
AI_PERSONALIZATION_CONFIG = {
    "version": __version__,
    "description": "Advanced AI personalization system with privacy-first design",
    "features": {
        "behavioral_analytics": True,
        "personalized_recommendations": True,
        "adaptive_learning": True,
        "user_profiling": True,
        "privacy_management": True,
        "consent_management": True,
        "data_portability": True,
        "gdpr_compliance": True,
        "real_time_personalization": True,
        "segmentation": True,
        "ab_testing": True
    },
    "privacy": {
        "gdpr_compliant": True,
        "ccpa_compliant": True,
        "default_consent": False,
        "data_retention_days": 365,
        "anonymization_enabled": True,
        "consent_expiry_days": 365,
        "audit_trail": True
    },
    "performance": {
        "recommendation_timeout_ms": 500,
        "learning_batch_size": 100,
        "min_interactions_for_profiling": 10,
        "confidence_threshold": 0.7,
        "cache_ttl_seconds": 300,
        "max_recommendations": 50
    },
    "ai_models": {
        "user_segmentation": {
            "min_cluster_size": 10,
            "max_clusters": 10,
            "feature_scaling": True
        },
        "recommendation_engine": {
            "content_based": True,
            "collaborative_filtering": True,
            "hybrid_approach": True
        },
        "learning_system": {
            "adaptive_learning_rate": True,
            "feedback_weight": 0.3,
            "implicit_weight": 0.7
        }
    }
}