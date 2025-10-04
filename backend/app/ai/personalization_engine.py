"""
Advanced AI Personalization Engine for Planning Explorer
Generates personalized recommendations, content, and user experiences
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import asyncio

from .user_analytics import UserBehaviorAnalyzer, UserSegment, InteractionType

logger = logging.getLogger(__name__)


class RecommendationType(str, Enum):
    """Types of recommendations to generate"""
    OPPORTUNITIES = "opportunities"
    SEARCHES = "searches"
    APPLICATIONS = "applications"
    MARKET_INTELLIGENCE = "market_intelligence"
    TRAINING_CONTENT = "training_content"
    FEATURES = "features"
    TIMING = "timing"
    GEOGRAPHIC = "geographic"


class PersonalizationLevel(str, Enum):
    """Levels of personalization"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class Recommendation:
    """Individual recommendation item"""
    recommendation_id: str
    user_id: str
    type: RecommendationType
    title: str
    description: str
    confidence: float
    relevance_score: float
    reasoning: List[str]
    action_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class PersonalizedContent:
    """Personalized content with user-specific adaptations"""
    content_id: str
    user_id: str
    original_content: Dict[str, Any]
    personalized_content: Dict[str, Any]
    personalization_factors: List[str]
    adaptation_level: PersonalizationLevel
    confidence: float
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class UserPreferences:
    """Comprehensive user preferences for personalization"""
    user_id: str
    content_preferences: Dict[str, float]
    feature_preferences: Dict[str, float]
    interaction_preferences: Dict[str, float]
    geographic_preferences: List[Dict[str, Any]]
    temporal_preferences: Dict[str, Any]
    risk_preferences: Dict[str, float]
    complexity_preference: float  # 0-1 scale
    notification_preferences: Dict[str, Any]
    privacy_preferences: Dict[str, bool]
    last_updated: datetime = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()


class PersonalizationEngine:
    """
    Advanced AI personalization engine that creates tailored user experiences
    """

    def __init__(self, supabase_client, behavior_analyzer: UserBehaviorAnalyzer,
                 redis_client=None):
        self.supabase = supabase_client
        self.behavior_analyzer = behavior_analyzer
        self.redis = redis_client
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')

    async def generate_recommendations(
        self,
        user_id: str,
        recommendation_type: RecommendationType,
        limit: int = 10,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Recommendation]:
        """
        Generate personalized recommendations for a user

        Args:
            user_id: User identifier
            recommendation_type: Type of recommendations to generate
            limit: Maximum number of recommendations
            context: Additional context for recommendations

        Returns:
            List of personalized recommendations
        """
        try:
            # Get user behavior profile
            user_profile = await self.behavior_analyzer.analyze_user_patterns(user_id)
            user_preferences = await self._get_user_preferences(user_id)

            # Generate recommendations based on type
            if recommendation_type == RecommendationType.OPPORTUNITIES:
                recommendations = await self._generate_opportunity_recommendations(
                    user_id, user_profile, user_preferences, context, limit
                )
            elif recommendation_type == RecommendationType.SEARCHES:
                recommendations = await self._generate_search_recommendations(
                    user_id, user_profile, user_preferences, context, limit
                )
            elif recommendation_type == RecommendationType.APPLICATIONS:
                recommendations = await self._generate_application_recommendations(
                    user_id, user_profile, user_preferences, context, limit
                )
            elif recommendation_type == RecommendationType.MARKET_INTELLIGENCE:
                recommendations = await self._generate_market_intelligence_recommendations(
                    user_id, user_profile, user_preferences, context, limit
                )
            elif recommendation_type == RecommendationType.FEATURES:
                recommendations = await self._generate_feature_recommendations(
                    user_id, user_profile, user_preferences, context, limit
                )
            elif recommendation_type == RecommendationType.TIMING:
                recommendations = await self._generate_timing_recommendations(
                    user_id, user_profile, user_preferences, context, limit
                )
            else:
                recommendations = []

            # Filter and rank recommendations
            filtered_recommendations = await self._filter_and_rank_recommendations(
                recommendations, user_profile, user_preferences
            )

            # Store recommendations for future analysis
            await self._store_recommendations(filtered_recommendations)

            logger.info(f"Generated {len(filtered_recommendations)} {recommendation_type} recommendations for user {user_id}")
            return filtered_recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []

    async def personalize_search_results(
        self,
        user_id: str,
        search_results: List[Dict[str, Any]],
        search_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Personalize search results based on user preferences and behavior

        Args:
            user_id: User identifier
            search_results: Original search results
            search_context: Search context and parameters

        Returns:
            Personalized and reranked search results
        """
        try:
            user_profile = await self.behavior_analyzer.analyze_user_patterns(user_id)
            user_preferences = await self._get_user_preferences(user_id)

            personalized_results = []

            for result in search_results:
                # Calculate personalization score
                personalization_score = await self._calculate_result_personalization_score(
                    result, user_profile, user_preferences, search_context
                )

                # Add personalization metadata
                result['personalization_score'] = personalization_score
                result['personalization_factors'] = await self._get_personalization_factors(
                    result, user_profile, user_preferences
                )

                # Enhance result with personalized content
                if personalization_score > 0.7:  # High relevance
                    result['personalized_summary'] = await self._generate_personalized_summary(
                        result, user_profile, user_preferences
                    )

                personalized_results.append(result)

            # Rerank based on personalization scores
            personalized_results.sort(
                key=lambda x: (x.get('personalization_score', 0) * 0.4 +
                             x.get('relevance_score', 0) * 0.6),
                reverse=True
            )

            # Track personalization effectiveness
            await self._track_personalization_usage(user_id, "search_personalization",
                                                  len(personalized_results))

            return personalized_results

        except Exception as e:
            logger.error(f"Error personalizing search results: {str(e)}")
            return search_results

    async def customize_ai_summaries(
        self,
        user_id: str,
        application_data: Dict[str, Any],
        summary_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized AI summaries based on user expertise and interests

        Args:
            user_id: User identifier
            application_data: Planning application data
            summary_context: Additional context for summary generation

        Returns:
            Personalized AI summary
        """
        try:
            user_profile = await self.behavior_analyzer.analyze_user_patterns(user_id)
            user_preferences = await self._get_user_preferences(user_id)

            # Determine personalization level
            personalization_level = self._determine_personalization_level(
                user_profile.expertise_level
            )

            # Generate base summary
            base_summary = await self._generate_base_summary(application_data)

            # Customize based on user characteristics
            customized_summary = await self._customize_summary_content(
                base_summary, user_profile, user_preferences, personalization_level
            )

            # Add personalized insights
            personalized_insights = await self._generate_personalized_insights(
                application_data, user_profile, user_preferences
            )

            # Combine into final personalized summary
            final_summary = {
                'summary': customized_summary,
                'personalized_insights': personalized_insights,
                'personalization_level': personalization_level,
                'confidence': await self._calculate_summary_confidence(
                    user_profile, application_data
                ),
                'adaptation_factors': await self._get_summary_adaptation_factors(
                    user_profile, user_preferences
                )
            }

            return final_summary

        except Exception as e:
            logger.error(f"Error customizing AI summary: {str(e)}")
            return {'summary': 'Error generating personalized summary'}

    async def adapt_opportunity_scoring(
        self,
        user_id: str,
        scoring_factors: Dict[str, float],
        application_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Adapt opportunity scoring weights based on user preferences and risk tolerance

        Args:
            user_id: User identifier
            scoring_factors: Base scoring factors
            application_data: Application data for context

        Returns:
            Personalized scoring factors
        """
        try:
            user_profile = await self.behavior_analyzer.analyze_user_patterns(user_id)
            user_preferences = await self._get_user_preferences(user_id)

            # Get user-specific scoring preferences
            scoring_preferences = user_preferences.risk_preferences

            # Adapt weights based on user characteristics
            adapted_factors = scoring_factors.copy()

            # Risk tolerance adaptations
            if user_profile.risk_tolerance > 0.7:  # High risk tolerance
                adapted_factors['innovation_factor'] *= 1.2
                adapted_factors['size_factor'] *= 1.1
                adapted_factors['complexity_factor'] *= 0.9
            elif user_profile.risk_tolerance < 0.3:  # Low risk tolerance
                adapted_factors['stability_factor'] *= 1.2
                adapted_factors['precedent_factor'] *= 1.1
                adapted_factors['complexity_factor'] *= 0.8

            # Expertise level adaptations
            if user_profile.expertise_level > 0.8:  # Expert user
                adapted_factors['technical_detail_factor'] *= 1.15
                adapted_factors['regulatory_complexity_factor'] *= 1.1
            elif user_profile.expertise_level < 0.3:  # Beginner user
                adapted_factors['simplicity_factor'] *= 1.2
                adapted_factors['guidance_availability_factor'] *= 1.15

            # Geographic preference adaptations
            if user_profile.geographic_focus:
                top_location = user_profile.geographic_focus[0]
                if application_data.get('location_similarity', 0) > 0.8:
                    adapted_factors['location_factor'] *= 1.3

            # Interest-based adaptations
            user_interests = user_profile.interests
            for interest in user_interests:
                if interest in application_data.get('categories', []):
                    adapted_factors['interest_alignment_factor'] = adapted_factors.get(
                        'interest_alignment_factor', 1.0
                    ) * 1.2

            # Normalize weights to sum to original total
            original_sum = sum(scoring_factors.values())
            adapted_sum = sum(adapted_factors.values())
            normalization_factor = original_sum / adapted_sum

            for key in adapted_factors:
                adapted_factors[key] *= normalization_factor

            return adapted_factors

        except Exception as e:
            logger.error(f"Error adapting opportunity scoring: {str(e)}")
            return scoring_factors

    async def personalize_market_intelligence(
        self,
        user_id: str,
        market_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized market intelligence based on user interests and focus areas

        Args:
            user_id: User identifier
            market_data: Raw market intelligence data
            context: Additional context for personalization

        Returns:
            Personalized market intelligence
        """
        try:
            user_profile = await self.behavior_analyzer.analyze_user_patterns(user_id)
            user_preferences = await self._get_user_preferences(user_id)

            # Filter market data based on user interests
            filtered_data = await self._filter_market_data_by_interests(
                market_data, user_profile, user_preferences
            )

            # Prioritize data based on user geographic focus
            prioritized_data = await self._prioritize_market_data_by_geography(
                filtered_data, user_profile.geographic_focus
            )

            # Generate personalized insights
            personalized_insights = await self._generate_personalized_market_insights(
                prioritized_data, user_profile, user_preferences
            )

            # Customize presentation based on expertise level
            presentation_style = self._determine_presentation_style(
                user_profile.expertise_level
            )

            personalized_intelligence = {
                'market_data': prioritized_data,
                'personalized_insights': personalized_insights,
                'presentation_style': presentation_style,
                'focus_areas': user_profile.geographic_focus,
                'relevance_score': await self._calculate_market_relevance_score(
                    prioritized_data, user_profile
                ),
                'recommended_actions': await self._generate_recommended_actions(
                    prioritized_data, user_profile, user_preferences
                )
            }

            return personalized_intelligence

        except Exception as e:
            logger.error(f"Error personalizing market intelligence: {str(e)}")
            return market_data

    async def update_user_preferences_from_interactions(
        self,
        user_id: str,
        interactions: List[Dict[str, Any]]
    ) -> UserPreferences:
        """
        Update user preferences based on recent interactions and implicit feedback

        Args:
            user_id: User identifier
            interactions: Recent user interactions

        Returns:
            Updated user preferences
        """
        try:
            current_preferences = await self._get_user_preferences(user_id)
            user_profile = await self.behavior_analyzer.analyze_user_patterns(user_id)

            # Analyze content preferences from interactions
            content_preferences = await self._analyze_content_preferences(interactions)

            # Analyze feature preferences
            feature_preferences = await self._analyze_feature_preferences(interactions)

            # Analyze interaction patterns
            interaction_preferences = await self._analyze_interaction_preferences(interactions)

            # Update geographic preferences
            geographic_preferences = await self._update_geographic_preferences(
                current_preferences.geographic_preferences, interactions
            )

            # Update temporal preferences
            temporal_preferences = await self._update_temporal_preferences(
                current_preferences.temporal_preferences, interactions
            )

            # Update risk preferences based on user behavior
            risk_preferences = await self._update_risk_preferences(
                current_preferences.risk_preferences, interactions, user_profile
            )

            # Calculate complexity preference
            complexity_preference = await self._calculate_complexity_preference(
                interactions, user_profile
            )

            # Create updated preferences
            updated_preferences = UserPreferences(
                user_id=user_id,
                content_preferences=content_preferences,
                feature_preferences=feature_preferences,
                interaction_preferences=interaction_preferences,
                geographic_preferences=geographic_preferences,
                temporal_preferences=temporal_preferences,
                risk_preferences=risk_preferences,
                complexity_preference=complexity_preference,
                notification_preferences=current_preferences.notification_preferences,
                privacy_preferences=current_preferences.privacy_preferences,
                last_updated=datetime.utcnow()
            )

            # Store updated preferences
            await self._store_user_preferences(updated_preferences)

            return updated_preferences

        except Exception as e:
            logger.error(f"Error updating user preferences: {str(e)}")
            return current_preferences

    # Private helper methods

    async def _get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get user preferences from database or create defaults"""
        try:
            result = self.supabase.table('user_preferences')\
                .select('*')\
                .eq('user_id', user_id)\
                .execute()

            if result.data:
                prefs_data = result.data[0]
                return UserPreferences(**prefs_data)
            else:
                return self._create_default_preferences(user_id)

        except Exception as e:
            logger.error(f"Error getting user preferences: {str(e)}")
            return self._create_default_preferences(user_id)

    def _create_default_preferences(self, user_id: str) -> UserPreferences:
        """Create default user preferences"""
        return UserPreferences(
            user_id=user_id,
            content_preferences={
                'residential': 0.5, 'commercial': 0.5, 'industrial': 0.3,
                'retail': 0.4, 'mixed_use': 0.6, 'infrastructure': 0.3
            },
            feature_preferences={
                'ai_summaries': 0.8, 'opportunity_scores': 0.7, 'map_view': 0.6,
                'detailed_analysis': 0.5, 'export_features': 0.4
            },
            interaction_preferences={
                'search': 0.9, 'browse': 0.6, 'alerts': 0.7,
                'reports': 0.5, 'sharing': 0.3
            },
            geographic_preferences=[],
            temporal_preferences={
                'preferred_hours': [9, 10, 11, 14, 15, 16],
                'preferred_days': [1, 2, 3, 4, 5]  # Monday to Friday
            },
            risk_preferences={
                'conservative': 0.5, 'moderate': 0.7, 'aggressive': 0.3
            },
            complexity_preference=0.5,
            notification_preferences={
                'email': True, 'push': True, 'frequency': 'daily'
            },
            privacy_preferences={
                'data_collection': True, 'personalization': True, 'analytics': True
            }
        )

    async def _generate_opportunity_recommendations(
        self, user_id: str, user_profile, user_preferences: UserPreferences,
        context: Optional[Dict[str, Any]], limit: int
    ) -> List[Recommendation]:
        """Generate opportunity-based recommendations"""
        recommendations = []

        # Get recent opportunities in user's areas of interest
        geographic_areas = [geo['area'] for geo in user_profile.geographic_focus[:3]]

        if geographic_areas:
            # Query for recent opportunities in user's geographic focus
            cutoff_date = datetime.utcnow() - timedelta(days=30)

            opportunities_result = self.supabase.table('planning_applications')\
                .select('*')\
                .in_('local_authority', user_profile.preferred_authorities[:5])\
                .gte('submission_date', cutoff_date.isoformat())\
                .limit(limit * 2)\
                .execute()

            opportunities = opportunities_result.data

            for i, opp in enumerate(opportunities[:limit]):
                confidence = self._calculate_opportunity_confidence(
                    opp, user_profile, user_preferences
                )

                if confidence > 0.6:  # Only recommend high-confidence opportunities
                    recommendations.append(Recommendation(
                        recommendation_id=f"opp_{opp['id']}_{user_id}",
                        user_id=user_id,
                        type=RecommendationType.OPPORTUNITIES,
                        title=f"New Opportunity: {opp.get('proposal_description', 'Planning Application')[:50]}",
                        description=f"High-potential opportunity in {opp.get('local_authority', 'your area')}",
                        confidence=confidence,
                        relevance_score=confidence,
                        reasoning=[
                            f"Matches your geographic focus on {opp.get('local_authority')}",
                            f"Aligns with your interests in {opp.get('development_type', 'development')}",
                            f"Recent submission on {opp.get('submission_date', 'unknown date')}"
                        ],
                        action_url=f"/applications/{opp['id']}",
                        metadata={'application_id': opp['id']},
                        expires_at=datetime.utcnow() + timedelta(days=7)
                    ))

        return recommendations

    async def _generate_search_recommendations(
        self, user_id: str, user_profile, user_preferences: UserPreferences,
        context: Optional[Dict[str, Any]], limit: int
    ) -> List[Recommendation]:
        """Generate search-based recommendations"""
        recommendations = []

        # Recommend searches based on user patterns
        common_terms = user_profile.search_patterns.get('common_terms', [])

        for i, term in enumerate(common_terms[:limit]):
            confidence = 0.8 - (i * 0.1)  # Decreasing confidence

            recommendations.append(Recommendation(
                recommendation_id=f"search_{term}_{user_id}",
                user_id=user_id,
                type=RecommendationType.SEARCHES,
                title=f"Suggested Search: {term.title()}",
                description=f"Based on your search history, you might be interested in recent {term} applications",
                confidence=confidence,
                relevance_score=confidence,
                reasoning=[
                    f"You've searched for '{term}' multiple times",
                    "New applications matching this term are available",
                    "High success rate for similar searches"
                ],
                action_url=f"/search?q={term}",
                metadata={'search_term': term},
                expires_at=datetime.utcnow() + timedelta(days=3)
            ))

        return recommendations

    async def _generate_application_recommendations(
        self, user_id: str, user_profile, user_preferences: UserPreferences,
        context: Optional[Dict[str, Any]], limit: int
    ) -> List[Recommendation]:
        """Generate similar application recommendations"""
        recommendations = []

        # Get user's recently viewed applications
        recent_views = self.supabase.table('user_interactions')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('interaction_type', InteractionType.VIEW_APPLICATION)\
            .order('timestamp', desc=True)\
            .limit(5)\
            .execute()

        if recent_views.data:
            # Find similar applications using content-based filtering
            for view in recent_views.data[:3]:
                app_id = view.get('application_id')
                if app_id:
                    similar_apps = await self._find_similar_applications(
                        app_id, user_preferences, limit=3
                    )

                    for similar_app in similar_apps:
                        recommendations.append(Recommendation(
                            recommendation_id=f"similar_{similar_app['id']}_{user_id}",
                            user_id=user_id,
                            type=RecommendationType.APPLICATIONS,
                            title=f"Similar to Your Recent View",
                            description=f"Application in {similar_app.get('local_authority', 'similar area')}",
                            confidence=0.7,
                            relevance_score=0.7,
                            reasoning=[
                                "Similar to applications you've viewed recently",
                                "Matches your area of interest",
                                "High relevance based on your preferences"
                            ],
                            action_url=f"/applications/{similar_app['id']}",
                            metadata={'application_id': similar_app['id']},
                            expires_at=datetime.utcnow() + timedelta(days=5)
                        ))

        return recommendations[:limit]

    async def _generate_market_intelligence_recommendations(
        self, user_id: str, user_profile, user_preferences: UserPreferences,
        context: Optional[Dict[str, Any]], limit: int
    ) -> List[Recommendation]:
        """Generate market intelligence recommendations"""
        recommendations = []

        # Recommend market reports based on user's geographic focus
        for geo_area in user_profile.geographic_focus[:limit]:
            area_name = geo_area.get('area', 'Unknown Area')

            recommendations.append(Recommendation(
                recommendation_id=f"market_{area_name}_{user_id}",
                user_id=user_id,
                type=RecommendationType.MARKET_INTELLIGENCE,
                title=f"Market Report: {area_name}",
                description=f"Latest market trends and insights for {area_name}",
                confidence=0.8,
                relevance_score=geo_area.get('frequency', 0.5),
                reasoning=[
                    f"You frequently search in {area_name}",
                    "New market data available for this area",
                    "Trending developments in your area of interest"
                ],
                action_url=f"/market-intelligence?area={area_name}",
                metadata={'geographic_area': area_name},
                expires_at=datetime.utcnow() + timedelta(days=14)
            ))

        return recommendations

    async def _generate_feature_recommendations(
        self, user_id: str, user_profile, user_preferences: UserPreferences,
        context: Optional[Dict[str, Any]], limit: int
    ) -> List[Recommendation]:
        """Generate feature usage recommendations"""
        recommendations = []

        # Recommend underutilized features based on user segment
        if user_profile.segment in [UserSegment.REGULAR_USER, UserSegment.POWER_USER]:
            if user_preferences.feature_preferences.get('reports', 0) < 0.5:
                recommendations.append(Recommendation(
                    recommendation_id=f"feature_reports_{user_id}",
                    user_id=user_id,
                    type=RecommendationType.FEATURES,
                    title="Try Report Generation",
                    description="Generate detailed analysis reports for your searches",
                    confidence=0.7,
                    relevance_score=0.7,
                    reasoning=[
                        "You haven't tried report generation yet",
                        "Perfect for your level of platform usage",
                        "Can help analyze your search results better"
                    ],
                    action_url="/reports/new",
                    metadata={'feature': 'reports'},
                    expires_at=datetime.utcnow() + timedelta(days=7)
                ))

        return recommendations

    async def _generate_timing_recommendations(
        self, user_id: str, user_profile, user_preferences: UserPreferences,
        context: Optional[Dict[str, Any]], limit: int
    ) -> List[Recommendation]:
        """Generate timing-based recommendations"""
        recommendations = []

        # Analyze user's activity patterns
        peak_hours = user_profile.time_patterns.get('peak_hours', [])

        if peak_hours:
            current_hour = datetime.utcnow().hour
            if current_hour in peak_hours:
                recommendations.append(Recommendation(
                    recommendation_id=f"timing_peak_{user_id}",
                    user_id=user_id,
                    type=RecommendationType.TIMING,
                    title="Peak Activity Time",
                    description="This is typically your most productive search time",
                    confidence=0.6,
                    relevance_score=0.6,
                    reasoning=[
                        "Based on your activity patterns",
                        "You typically find more relevant results now",
                        "High engagement time for you"
                    ],
                    action_url="/search",
                    metadata={'optimal_time': True},
                    expires_at=datetime.utcnow() + timedelta(hours=2)
                ))

        return recommendations

    async def _filter_and_rank_recommendations(
        self, recommendations: List[Recommendation], user_profile, user_preferences: UserPreferences
    ) -> List[Recommendation]:
        """Filter and rank recommendations based on user preferences"""
        # Filter out expired recommendations
        valid_recommendations = [
            rec for rec in recommendations
            if not rec.expires_at or rec.expires_at > datetime.utcnow()
        ]

        # Filter by confidence threshold
        min_confidence = 0.5 if user_profile.segment in [UserSegment.NEWCOMER] else 0.6
        confident_recommendations = [
            rec for rec in valid_recommendations
            if rec.confidence >= min_confidence
        ]

        # Rank by combined score (confidence + relevance)
        ranked_recommendations = sorted(
            confident_recommendations,
            key=lambda x: (x.confidence * 0.6 + x.relevance_score * 0.4),
            reverse=True
        )

        return ranked_recommendations

    def _calculate_opportunity_confidence(
        self, opportunity: Dict[str, Any], user_profile, user_preferences: UserPreferences
    ) -> float:
        """Calculate confidence score for opportunity recommendation"""
        confidence = 0.5  # Base confidence

        # Geographic relevance
        if opportunity.get('local_authority') in user_profile.preferred_authorities:
            confidence += 0.2

        # Content relevance based on user interests
        development_type = opportunity.get('development_type', '').lower()
        for interest in user_profile.interests:
            if interest in development_type:
                confidence += 0.1

        # Recency boost
        submission_date = opportunity.get('submission_date')
        if submission_date:
            try:
                submit_dt = datetime.fromisoformat(submission_date.replace('Z', '+00:00'))
                days_ago = (datetime.utcnow() - submit_dt).days
                if days_ago <= 7:
                    confidence += 0.15
                elif days_ago <= 30:
                    confidence += 0.1
            except:
                pass

        return min(confidence, 1.0)

    async def _calculate_result_personalization_score(
        self, result: Dict[str, Any], user_profile, user_preferences: UserPreferences,
        search_context: Dict[str, Any]
    ) -> float:
        """Calculate personalization score for a search result"""
        score = 0.5  # Base score

        # Geographic preference match
        result_authority = result.get('local_authority', '')
        if result_authority in user_profile.preferred_authorities:
            score += 0.2

        # Content preference match
        result_type = result.get('development_type', '').lower()
        for content_type, preference in user_preferences.content_preferences.items():
            if content_type in result_type:
                score += preference * 0.1

        # User expertise level adjustment
        if user_profile.expertise_level > 0.7:
            # Expert users prefer detailed, complex applications
            if result.get('proposal_description', ''):
                description_length = len(result['proposal_description'])
                if description_length > 500:  # Detailed application
                    score += 0.1
        else:
            # Beginners prefer simpler applications
            if result.get('application_type') in ['householder', 'certificate_of_lawfulness']:
                score += 0.1

        return min(score, 1.0)

    async def _get_personalization_factors(
        self, result: Dict[str, Any], user_profile, user_preferences: UserPreferences
    ) -> List[str]:
        """Get factors that influenced personalization"""
        factors = []

        if result.get('local_authority') in user_profile.preferred_authorities:
            factors.append(f"Matches your geographic focus on {result['local_authority']}")

        if user_profile.expertise_level > 0.7:
            factors.append("Detailed content suitable for your expertise level")

        return factors

    def _determine_personalization_level(self, expertise_level: float) -> PersonalizationLevel:
        """Determine appropriate personalization level"""
        if expertise_level < 0.25:
            return PersonalizationLevel.BASIC
        elif expertise_level < 0.5:
            return PersonalizationLevel.INTERMEDIATE
        elif expertise_level < 0.75:
            return PersonalizationLevel.ADVANCED
        else:
            return PersonalizationLevel.EXPERT

    async def _store_recommendations(self, recommendations: List[Recommendation]):
        """Store recommendations in database"""
        try:
            for rec in recommendations:
                rec_dict = asdict(rec)
                self.supabase.table('user_recommendations').insert(rec_dict).execute()
        except Exception as e:
            logger.error(f"Error storing recommendations: {str(e)}")

    async def _store_user_preferences(self, preferences: UserPreferences):
        """Store user preferences in database"""
        try:
            prefs_dict = asdict(preferences)
            self.supabase.table('user_preferences')\
                .upsert(prefs_dict, on_conflict='user_id')\
                .execute()
        except Exception as e:
            logger.error(f"Error storing user preferences: {str(e)}")

    async def _track_personalization_usage(self, user_id: str, feature: str, count: int):
        """Track usage of personalization features"""
        try:
            await self.behavior_analyzer.track_interaction(
                user_id=user_id,
                interaction_type=InteractionType.AI_SUMMARY_VIEW,  # Generic AI feature usage
                context={
                    'feature': feature,
                    'count': count,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error tracking personalization usage: {str(e)}")

    # Additional helper methods would continue here...
    # (The file is getting quite long, so I'll include the most important methods)

    async def _find_similar_applications(
        self, app_id: str, user_preferences: UserPreferences, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar applications using content-based filtering"""
        try:
            # Get the reference application
            ref_app_result = self.supabase.table('planning_applications')\
                .select('*')\
                .eq('id', app_id)\
                .execute()

            if not ref_app_result.data:
                return []

            ref_app = ref_app_result.data[0]

            # Find similar applications based on authority and type
            similar_apps_result = self.supabase.table('planning_applications')\
                .select('*')\
                .eq('local_authority', ref_app.get('local_authority'))\
                .neq('id', app_id)\
                .limit(limit)\
                .execute()

            return similar_apps_result.data

        except Exception as e:
            logger.error(f"Error finding similar applications: {str(e)}")
            return []

    async def _generate_base_summary(self, application_data: Dict[str, Any]) -> str:
        """Generate base AI summary for application"""
        # This would integrate with the existing summarizer
        proposal = application_data.get('proposal_description', 'Planning application')
        authority = application_data.get('local_authority', 'Local authority')

        return f"Planning application submitted to {authority}. {proposal[:200]}..."

    async def _customize_summary_content(
        self, base_summary: str, user_profile, user_preferences: UserPreferences,
        personalization_level: PersonalizationLevel
    ) -> str:
        """Customize summary content based on user characteristics"""
        if personalization_level == PersonalizationLevel.EXPERT:
            return f"[Expert Analysis] {base_summary} Advanced technical details and regulatory implications are available."
        elif personalization_level == PersonalizationLevel.BASIC:
            return f"[Simplified] {base_summary} This application involves standard development procedures."
        else:
            return base_summary

    async def _generate_personalized_insights(
        self, application_data: Dict[str, Any], user_profile, user_preferences: UserPreferences
    ) -> List[str]:
        """Generate personalized insights for the application"""
        insights = []

        # Geographic insight
        if application_data.get('local_authority') in user_profile.preferred_authorities:
            insights.append(f"This application is in your area of interest: {application_data['local_authority']}")

        # Expertise-based insight
        if user_profile.expertise_level > 0.7:
            insights.append("Complex regulatory considerations may apply - review full documentation")

        # Risk-based insight
        if user_profile.risk_tolerance > 0.7:
            insights.append("High potential opportunity with innovative development approach")

        return insights

    async def _calculate_summary_confidence(
        self, user_profile, application_data: Dict[str, Any]
    ) -> float:
        """Calculate confidence in personalized summary"""
        confidence = 0.7  # Base confidence

        # Higher confidence for areas user is familiar with
        if application_data.get('local_authority') in user_profile.preferred_authorities:
            confidence += 0.2

        # Higher confidence for experienced users
        confidence += user_profile.expertise_level * 0.1

        return min(confidence, 1.0)

    async def _get_summary_adaptation_factors(
        self, user_profile, user_preferences: UserPreferences
    ) -> List[str]:
        """Get factors that influenced summary adaptation"""
        factors = []

        factors.append(f"Adapted for {user_profile.segment.value} user level")

        if user_profile.expertise_level > 0.7:
            factors.append("Enhanced with technical details for expert user")

        if user_profile.geographic_focus:
            factors.append("Emphasized geographic relevance based on your focus areas")

        return factors

    # Content preference analysis methods
    async def _analyze_content_preferences(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze content preferences from interactions"""
        content_scores = {
            'residential': 0.5, 'commercial': 0.5, 'industrial': 0.3,
            'retail': 0.4, 'mixed_use': 0.6, 'infrastructure': 0.3
        }

        # Analyze search queries and viewed applications
        for interaction in interactions:
            if interaction.get('interaction_type') == InteractionType.SEARCH:
                query = interaction.get('search_query', '').lower()
                for content_type in content_scores:
                    if content_type in query:
                        content_scores[content_type] = min(content_scores[content_type] + 0.1, 1.0)

        return content_scores

    async def _analyze_feature_preferences(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze feature preferences from interactions"""
        feature_scores = {
            'ai_summaries': 0.5, 'opportunity_scores': 0.5, 'map_view': 0.5,
            'detailed_analysis': 0.5, 'export_features': 0.5
        }

        interaction_counts = Counter([i.get('interaction_type') for i in interactions])

        # Map interaction types to feature preferences
        if interaction_counts.get(InteractionType.AI_SUMMARY_VIEW, 0) > 5:
            feature_scores['ai_summaries'] = min(feature_scores['ai_summaries'] + 0.2, 1.0)

        if interaction_counts.get(InteractionType.VIEW_MAP, 0) > 10:
            feature_scores['map_view'] = min(feature_scores['map_view'] + 0.2, 1.0)

        if interaction_counts.get(InteractionType.EXPORT_DATA, 0) > 2:
            feature_scores['export_features'] = min(feature_scores['export_features'] + 0.3, 1.0)

        return feature_scores

    async def _analyze_interaction_preferences(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze interaction pattern preferences"""
        interaction_scores = {
            'search': 0.5, 'browse': 0.5, 'alerts': 0.5,
            'reports': 0.5, 'sharing': 0.5
        }

        interaction_counts = Counter([i.get('interaction_type') for i in interactions])
        total_interactions = len(interactions)

        if total_interactions > 0:
            search_ratio = interaction_counts.get(InteractionType.SEARCH, 0) / total_interactions
            interaction_scores['search'] = min(search_ratio * 2, 1.0)

            alert_ratio = interaction_counts.get(InteractionType.CREATE_ALERT, 0) / total_interactions
            interaction_scores['alerts'] = min(alert_ratio * 10, 1.0)  # Alerts are less frequent

            report_ratio = interaction_counts.get(InteractionType.GENERATE_REPORT, 0) / total_interactions
            interaction_scores['reports'] = min(report_ratio * 20, 1.0)  # Reports are rare

        return interaction_scores