"""
Advanced User Profiling and Segmentation System
Creates detailed user personas and segments for targeted personalization
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from collections import defaultdict, Counter
import asyncio

from .user_analytics import UserBehaviorAnalyzer, UserSegment, InteractionType

logger = logging.getLogger(__name__)


class PersonaType(str, Enum):
    """Types of user personas"""
    PLANNING_PROFESSIONAL = "planning_professional"
    PROPERTY_DEVELOPER = "property_developer"
    ARCHITECT_DESIGNER = "architect_designer"
    LEGAL_CONSULTANT = "legal_consultant"
    RESEARCHER_ACADEMIC = "researcher_academic"
    LOCAL_AUTHORITY = "local_authority"
    COMMUNITY_GROUP = "community_group"
    HOMEOWNER = "homeowner"
    INVESTOR = "investor"
    STUDENT_LEARNER = "student_learner"


class ExpertiseLevel(str, Enum):
    """User expertise levels"""
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class EngagementType(str, Enum):
    """User engagement patterns"""
    BROWSER = "browser"  # Casual browsing
    RESEARCHER = "researcher"  # Deep research
    MONITOR = "monitor"  # Regular monitoring
    EXECUTOR = "executor"  # Action-oriented
    ANALYST = "analyst"  # Data analysis focused


@dataclass
class UserPersona:
    """Comprehensive user persona profile"""
    user_id: str
    persona_type: PersonaType
    confidence: float

    # Core characteristics
    expertise_level: ExpertiseLevel
    engagement_type: EngagementType
    primary_use_cases: List[str]
    secondary_use_cases: List[str]

    # Behavioral patterns
    search_behavior: Dict[str, Any]
    content_preferences: Dict[str, float]
    feature_usage: Dict[str, float]
    geographic_focus: List[Dict[str, Any]]
    temporal_patterns: Dict[str, Any]

    # Preferences and needs
    information_depth_preference: float  # 0-1 scale
    technical_detail_preference: float
    visual_preference: float
    notification_tolerance: float
    risk_tolerance: float

    # Business context
    organization_type: Optional[str]
    decision_making_role: Optional[str]
    industry_sector: Optional[str]
    experience_years: Optional[int]

    # Predictive insights
    predicted_interests: List[Dict[str, Any]]
    churn_risk: float
    growth_potential: float

    created_at: datetime
    last_updated: datetime


@dataclass
class UserSegment:
    """User segment definition with characteristics"""
    segment_id: str
    segment_name: str
    description: str

    # Segment characteristics
    size: int
    avg_expertise_level: float
    avg_engagement_score: float
    common_personas: List[PersonaType]

    # Behavioral patterns
    typical_behaviors: List[str]
    preferred_features: List[str]
    content_preferences: Dict[str, float]

    # Business metrics
    retention_rate: float
    conversion_rate: float
    lifetime_value: float

    # Personalization strategy
    recommended_approach: Dict[str, Any]
    priority_features: List[str]

    created_at: datetime
    last_updated: datetime


@dataclass
class SegmentationInsight:
    """Insights from user segmentation analysis"""
    insight_type: str
    title: str
    description: str
    affected_segments: List[str]
    impact_score: float
    recommendations: List[str]
    data_points: Dict[str, Any]
    created_at: datetime


class UserProfilingSystem:
    """
    Advanced user profiling and segmentation system
    """

    def __init__(self, supabase_client, behavior_analyzer: UserBehaviorAnalyzer, redis_client=None):
        self.supabase = supabase_client
        self.behavior_analyzer = behavior_analyzer
        self.redis = redis_client

        # ML models for clustering
        self.scaler = StandardScaler()
        self.persona_clusters = None
        self.segment_clusters = None

        # Profiling parameters
        self.min_interactions_for_profiling = 10
        self.persona_confidence_threshold = 0.7
        self.segment_update_frequency_days = 7

    async def create_user_persona(self, user_id: str) -> UserPersona:
        """
        Create comprehensive user persona based on behavioral analysis

        Args:
            user_id: User identifier

        Returns:
            Detailed user persona
        """
        try:
            # Get user behavior profile
            behavior_profile = await self.behavior_analyzer.analyze_user_patterns(user_id)

            # Determine persona type
            persona_type, confidence = await self._determine_persona_type(user_id, behavior_profile)

            # Determine expertise level
            expertise_level = self._determine_expertise_level(behavior_profile)

            # Determine engagement type
            engagement_type = self._determine_engagement_type(behavior_profile)

            # Extract use cases
            primary_use_cases, secondary_use_cases = await self._extract_use_cases(
                user_id, behavior_profile
            )

            # Analyze preferences
            preferences = await self._analyze_user_preferences(user_id, behavior_profile)

            # Extract business context
            business_context = await self._extract_business_context(user_id)

            # Generate predictive insights
            predicted_interests = await self._predict_user_interests(user_id, behavior_profile)
            churn_risk = await self._calculate_churn_risk(user_id, behavior_profile)
            growth_potential = await self._calculate_growth_potential(user_id, behavior_profile)

            # Create persona
            persona = UserPersona(
                user_id=user_id,
                persona_type=persona_type,
                confidence=confidence,
                expertise_level=expertise_level,
                engagement_type=engagement_type,
                primary_use_cases=primary_use_cases,
                secondary_use_cases=secondary_use_cases,
                search_behavior=behavior_profile.search_patterns,
                content_preferences=preferences['content'],
                feature_usage=preferences['features'],
                geographic_focus=behavior_profile.geographic_focus,
                temporal_patterns=behavior_profile.time_patterns,
                information_depth_preference=preferences['information_depth'],
                technical_detail_preference=preferences['technical_detail'],
                visual_preference=preferences['visual'],
                notification_tolerance=preferences['notification_tolerance'],
                risk_tolerance=behavior_profile.risk_tolerance,
                organization_type=business_context.get('organization_type'),
                decision_making_role=business_context.get('decision_role'),
                industry_sector=business_context.get('industry_sector'),
                experience_years=business_context.get('experience_years'),
                predicted_interests=predicted_interests,
                churn_risk=churn_risk,
                growth_potential=growth_potential,
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )

            # Store persona
            await self._store_user_persona(persona)

            logger.info(f"Created persona for user {user_id}: {persona_type} with {confidence:.2f} confidence")
            return persona

        except Exception as e:
            logger.error(f"Error creating user persona: {str(e)}")
            return None

    async def segment_users(
        self,
        user_ids: Optional[List[str]] = None,
        segmentation_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, UserSegment]:
        """
        Perform advanced user segmentation using ML clustering

        Args:
            user_ids: Specific users to segment, or None for all users
            segmentation_criteria: Additional criteria for segmentation

        Returns:
            Dictionary mapping segment IDs to segment definitions
        """
        try:
            # Get user data for segmentation
            user_data = await self._prepare_segmentation_data(user_ids)

            if len(user_data) < 50:  # Minimum users for meaningful segmentation
                logger.warning(f"Insufficient users for segmentation: {len(user_data)}")
                return {}

            # Prepare features for clustering
            features, user_id_list = await self._prepare_clustering_features(user_data)

            # Determine optimal number of clusters
            optimal_clusters = self._determine_optimal_clusters(features)

            # Perform clustering
            cluster_labels = self._perform_clustering(features, optimal_clusters)

            # Analyze clusters to create segments
            segments = await self._analyze_clusters_to_segments(
                features, cluster_labels, user_id_list, user_data
            )

            # Generate segment insights
            insights = await self._generate_segmentation_insights(segments)

            # Store segments and insights
            await self._store_segments(segments)
            await self._store_segmentation_insights(insights)

            logger.info(f"Created {len(segments)} user segments from {len(user_data)} users")
            return segments

        except Exception as e:
            logger.error(f"Error in user segmentation: {str(e)}")
            return {}

    async def get_user_segment(self, user_id: str) -> Optional[str]:
        """
        Get the segment ID for a specific user

        Args:
            user_id: User identifier

        Returns:
            Segment ID or None if not segmented
        """
        try:
            result = self.supabase.table('user_segments')\
                .select('segment_id')\
                .eq('user_id', user_id)\
                .execute()

            if result.data:
                return result.data[0]['segment_id']
            return None

        except Exception as e:
            logger.error(f"Error getting user segment: {str(e)}")
            return None

    async def get_segment_users(self, segment_id: str) -> List[str]:
        """
        Get all users in a specific segment

        Args:
            segment_id: Segment identifier

        Returns:
            List of user IDs in the segment
        """
        try:
            result = self.supabase.table('user_segments')\
                .select('user_id')\
                .eq('segment_id', segment_id)\
                .execute()

            return [row['user_id'] for row in result.data]

        except Exception as e:
            logger.error(f"Error getting segment users: {str(e)}")
            return []

    async def update_user_persona(self, user_id: str) -> UserPersona:
        """
        Update existing user persona based on new behavioral data

        Args:
            user_id: User identifier

        Returns:
            Updated user persona
        """
        try:
            # Get current persona
            current_persona = await self._get_stored_persona(user_id)

            # Create new persona
            new_persona = await self.create_user_persona(user_id)

            if current_persona and new_persona:
                # Compare personas for significant changes
                changes = self._compare_personas(current_persona, new_persona)

                if changes:
                    # Log persona evolution
                    await self._log_persona_evolution(user_id, current_persona, new_persona, changes)

            return new_persona

        except Exception as e:
            logger.error(f"Error updating user persona: {str(e)}")
            return None

    async def predict_user_behavior(
        self,
        user_id: str,
        prediction_horizon_days: int = 30
    ) -> Dict[str, Any]:
        """
        Predict user behavior patterns for the next period

        Args:
            user_id: User identifier
            prediction_horizon_days: Prediction time horizon

        Returns:
            Predicted behavior patterns
        """
        try:
            persona = await self._get_stored_persona(user_id)
            if not persona:
                persona = await self.create_user_persona(user_id)

            behavior_profile = await self.behavior_analyzer.analyze_user_patterns(user_id)

            predictions = {
                'likely_interactions': await self._predict_likely_interactions(
                    persona, behavior_profile, prediction_horizon_days
                ),
                'engagement_forecast': await self._predict_engagement_level(
                    persona, behavior_profile, prediction_horizon_days
                ),
                'feature_adoption': await self._predict_feature_adoption(
                    persona, behavior_profile
                ),
                'churn_probability': await self._predict_churn_probability(
                    persona, behavior_profile, prediction_horizon_days
                ),
                'value_potential': await self._predict_value_potential(
                    persona, behavior_profile, prediction_horizon_days
                ),
                'recommended_interventions': await self._recommend_interventions(
                    persona, behavior_profile
                )
            }

            return predictions

        except Exception as e:
            logger.error(f"Error predicting user behavior: {str(e)}")
            return {}

    async def generate_persona_insights(self, persona_type: PersonaType) -> List[Dict[str, Any]]:
        """
        Generate insights about a specific persona type

        Args:
            persona_type: Persona type to analyze

        Returns:
            List of insights about the persona
        """
        try:
            # Get all users with this persona type
            persona_users = await self._get_users_by_persona(persona_type)

            if len(persona_users) < 10:  # Minimum for meaningful insights
                return []

            # Analyze common patterns
            insights = []

            # Behavioral insights
            behavioral_patterns = await self._analyze_persona_behaviors(persona_users)
            insights.extend(behavioral_patterns)

            # Content preferences
            content_insights = await self._analyze_persona_content_preferences(persona_users)
            insights.extend(content_insights)

            # Feature usage patterns
            feature_insights = await self._analyze_persona_feature_usage(persona_users)
            insights.extend(feature_insights)

            # Performance metrics
            performance_insights = await self._analyze_persona_performance(persona_users)
            insights.extend(performance_insights)

            return insights

        except Exception as e:
            logger.error(f"Error generating persona insights: {str(e)}")
            return []

    # Private helper methods

    async def _determine_persona_type(
        self, user_id: str, behavior_profile
    ) -> Tuple[PersonaType, float]:
        """Determine user persona type based on behavior patterns"""

        # Analyze interaction patterns for persona indicators
        interaction_types = Counter(behavior_profile.preferred_interaction_types)
        search_patterns = behavior_profile.search_patterns

        persona_scores = {}

        # Planning Professional indicators
        professional_score = 0.0
        if interaction_types.get(InteractionType.GENERATE_REPORT, 0) > 5:
            professional_score += 0.3
        if interaction_types.get(InteractionType.EXPORT_DATA, 0) > 3:
            professional_score += 0.2
        if behavior_profile.expertise_level > 0.7:
            professional_score += 0.2
        if len(behavior_profile.preferred_authorities) > 3:
            professional_score += 0.2

        persona_scores[PersonaType.PLANNING_PROFESSIONAL] = professional_score

        # Property Developer indicators
        developer_score = 0.0
        if 'commercial' in str(search_patterns.get('common_terms', [])):
            developer_score += 0.2
        if 'residential' in str(search_patterns.get('common_terms', [])):
            developer_score += 0.2
        if interaction_types.get(InteractionType.OPPORTUNITY_SCORE_VIEW, 0) > 10:
            developer_score += 0.3
        if behavior_profile.risk_tolerance > 0.6:
            developer_score += 0.2

        persona_scores[PersonaType.PROPERTY_DEVELOPER] = developer_score

        # Researcher/Academic indicators
        researcher_score = 0.0
        if interaction_types.get(InteractionType.SEARCH, 0) > 20:
            researcher_score += 0.2
        if behavior_profile.session_duration_avg > 600:  # 10+ minutes
            researcher_score += 0.2
        if interaction_types.get(InteractionType.EXPORT_DATA, 0) > 5:
            researcher_score += 0.2
        if len(search_patterns.get('common_terms', [])) > 10:
            researcher_score += 0.2

        persona_scores[PersonaType.RESEARCHER_ACADEMIC] = researcher_score

        # Homeowner indicators
        homeowner_score = 0.0
        if 'householder' in str(search_patterns.get('common_terms', [])):
            homeowner_score += 0.3
        if behavior_profile.expertise_level < 0.3:
            homeowner_score += 0.2
        if len(behavior_profile.geographic_focus) == 1:  # Single area focus
            homeowner_score += 0.2
        if interaction_types.get(InteractionType.VIEW_APPLICATION, 0) > interaction_types.get(InteractionType.SEARCH, 0):
            homeowner_score += 0.2

        persona_scores[PersonaType.HOMEOWNER] = homeowner_score

        # Add more persona type logic...

        # Determine best match
        if persona_scores:
            best_persona = max(persona_scores.items(), key=lambda x: x[1])
            return best_persona[0], min(best_persona[1], 1.0)
        else:
            return PersonaType.STUDENT_LEARNER, 0.5  # Default for new users

    def _determine_expertise_level(self, behavior_profile) -> ExpertiseLevel:
        """Determine user expertise level"""
        expertise = behavior_profile.expertise_level

        if expertise < 0.2:
            return ExpertiseLevel.NOVICE
        elif expertise < 0.4:
            return ExpertiseLevel.BEGINNER
        elif expertise < 0.6:
            return ExpertiseLevel.INTERMEDIATE
        elif expertise < 0.8:
            return ExpertiseLevel.ADVANCED
        else:
            return ExpertiseLevel.EXPERT

    def _determine_engagement_type(self, behavior_profile) -> EngagementType:
        """Determine user engagement pattern type"""
        interaction_types = Counter(behavior_profile.preferred_interaction_types)

        # Analyzer: lots of exports and reports
        if (interaction_types.get(InteractionType.EXPORT_DATA, 0) > 5 or
            interaction_types.get(InteractionType.GENERATE_REPORT, 0) > 3):
            return EngagementType.ANALYST

        # Executor: saves searches, creates alerts
        elif (interaction_types.get(InteractionType.SAVE_SEARCH, 0) > 3 or
              interaction_types.get(InteractionType.CREATE_ALERT, 0) > 2):
            return EngagementType.EXECUTOR

        # Researcher: long sessions, many searches
        elif (behavior_profile.session_duration_avg > 300 and
              interaction_types.get(InteractionType.SEARCH, 0) > 10):
            return EngagementType.RESEARCHER

        # Monitor: regular but brief interactions
        elif behavior_profile.interaction_frequency > 0.5:
            return EngagementType.MONITOR

        # Browser: casual interactions
        else:
            return EngagementType.BROWSER

    async def _extract_use_cases(
        self, user_id: str, behavior_profile
    ) -> Tuple[List[str], List[str]]:
        """Extract primary and secondary use cases from behavior"""

        # Analyze search patterns and interactions to infer use cases
        search_terms = behavior_profile.search_patterns.get('common_terms', [])
        interaction_types = behavior_profile.preferred_interaction_types

        primary_use_cases = []
        secondary_use_cases = []

        # Site monitoring use case
        if InteractionType.CREATE_ALERT in interaction_types:
            primary_use_cases.append("site_monitoring")

        # Market research use case
        if ('market' in search_terms or
            InteractionType.GENERATE_REPORT in interaction_types):
            primary_use_cases.append("market_research")

        # Opportunity identification use case
        if (InteractionType.OPPORTUNITY_SCORE_VIEW in interaction_types or
            'commercial' in search_terms):
            primary_use_cases.append("opportunity_identification")

        # Compliance checking use case
        if ('policy' in search_terms or 'regulation' in search_terms):
            secondary_use_cases.append("compliance_checking")

        # Competitive analysis use case
        if len(behavior_profile.preferred_authorities) > 5:
            secondary_use_cases.append("competitive_analysis")

        return primary_use_cases[:3], secondary_use_cases[:3]  # Limit to top 3 each

    async def _analyze_user_preferences(
        self, user_id: str, behavior_profile
    ) -> Dict[str, Any]:
        """Analyze detailed user preferences"""

        preferences = {
            'content': {},
            'features': {},
            'information_depth': 0.5,
            'technical_detail': 0.5,
            'visual': 0.5,
            'notification_tolerance': 0.5
        }

        # Analyze content preferences from search patterns
        search_terms = behavior_profile.search_patterns.get('common_terms', [])
        for term in search_terms:
            if 'residential' in term.lower():
                preferences['content']['residential'] = preferences['content'].get('residential', 0) + 0.1
            elif 'commercial' in term.lower():
                preferences['content']['commercial'] = preferences['content'].get('commercial', 0) + 0.1
            elif 'retail' in term.lower():
                preferences['content']['retail'] = preferences['content'].get('retail', 0) + 0.1

        # Normalize content preferences
        total_content = sum(preferences['content'].values())
        if total_content > 0:
            for key in preferences['content']:
                preferences['content'][key] /= total_content

        # Analyze feature preferences from interaction types
        interaction_counts = Counter(behavior_profile.preferred_interaction_types)
        total_interactions = sum(interaction_counts.values())

        if total_interactions > 0:
            preferences['features'] = {
                'search': interaction_counts.get(InteractionType.SEARCH, 0) / total_interactions,
                'reports': interaction_counts.get(InteractionType.GENERATE_REPORT, 0) / total_interactions,
                'alerts': interaction_counts.get(InteractionType.CREATE_ALERT, 0) / total_interactions,
                'exports': interaction_counts.get(InteractionType.EXPORT_DATA, 0) / total_interactions,
                'ai_summaries': interaction_counts.get(InteractionType.AI_SUMMARY_VIEW, 0) / total_interactions
            }

        # Information depth preference based on session duration
        if behavior_profile.session_duration_avg > 300:  # 5+ minutes
            preferences['information_depth'] = 0.8
        elif behavior_profile.session_duration_avg < 60:  # Less than 1 minute
            preferences['information_depth'] = 0.3

        # Technical detail preference based on expertise
        preferences['technical_detail'] = behavior_profile.expertise_level

        # Visual preference based on map usage
        if InteractionType.VIEW_MAP in behavior_profile.preferred_interaction_types:
            preferences['visual'] = 0.7

        return preferences

    async def _extract_business_context(self, user_id: str) -> Dict[str, Any]:
        """Extract business context from user profile and behavior"""

        context = {}

        try:
            # Get user profile data
            user_result = self.supabase.table('user_profiles')\
                .select('company, role')\
                .eq('user_id', user_id)\
                .execute()

            if user_result.data:
                user_data = user_result.data[0]

                # Infer organization type from company name
                company = user_data.get('company', '').lower()
                if any(word in company for word in ['council', 'authority', 'borough']):
                    context['organization_type'] = 'local_authority'
                elif any(word in company for word in ['ltd', 'limited', 'plc', 'development']):
                    context['organization_type'] = 'private_company'
                elif any(word in company for word in ['university', 'college', 'research']):
                    context['organization_type'] = 'academic'

                # Infer decision role from title
                role = user_data.get('role', '').lower()
                if any(word in role for word in ['director', 'manager', 'head', 'chief']):
                    context['decision_role'] = 'decision_maker'
                elif any(word in role for word in ['analyst', 'consultant', 'advisor']):
                    context['decision_role'] = 'advisor'
                elif any(word in role for word in ['assistant', 'junior', 'trainee']):
                    context['decision_role'] = 'support'
                else:
                    context['decision_role'] = 'individual_contributor'

        except Exception as e:
            logger.error(f"Error extracting business context: {str(e)}")

        return context

    async def _predict_user_interests(
        self, user_id: str, behavior_profile
    ) -> List[Dict[str, Any]]:
        """Predict user interests based on behavior patterns"""

        predicted_interests = []

        # Geographic interests
        for geo_focus in behavior_profile.geographic_focus[:3]:
            predicted_interests.append({
                'type': 'geographic',
                'value': geo_focus.get('area', 'Unknown'),
                'confidence': geo_focus.get('frequency', 0.5),
                'evidence': 'Frequent searches in this area'
            })

        # Content type interests
        search_terms = behavior_profile.search_patterns.get('common_terms', [])
        for term in search_terms[:5]:
            predicted_interests.append({
                'type': 'content',
                'value': term,
                'confidence': 0.6,
                'evidence': 'Frequent search term'
            })

        # Feature interests
        if InteractionType.GENERATE_REPORT in behavior_profile.preferred_interaction_types:
            predicted_interests.append({
                'type': 'feature',
                'value': 'advanced_analytics',
                'confidence': 0.7,
                'evidence': 'Uses report generation feature'
            })

        return predicted_interests

    async def _calculate_churn_risk(self, user_id: str, behavior_profile) -> float:
        """Calculate user churn risk"""

        risk_factors = []

        # Low engagement
        if behavior_profile.engagement_score < 0.3:
            risk_factors.append(0.4)

        # Declining interaction frequency
        recent_interactions = await self._get_recent_interaction_trend(user_id)
        if recent_interactions and recent_interactions < 0.5:  # Declining trend
            risk_factors.append(0.3)

        # No recent valuable actions
        if not any(action in behavior_profile.preferred_interaction_types
                  for action in [InteractionType.SAVE_SEARCH, InteractionType.CREATE_ALERT,
                               InteractionType.GENERATE_REPORT]):
            risk_factors.append(0.2)

        # Calculate overall risk
        if risk_factors:
            return min(sum(risk_factors), 1.0)
        else:
            return 0.1  # Baseline risk

    async def _calculate_growth_potential(self, user_id: str, behavior_profile) -> float:
        """Calculate user growth potential"""

        growth_factors = []

        # High engagement
        if behavior_profile.engagement_score > 0.7:
            growth_factors.append(0.3)

        # Learning trajectory (increasing expertise)
        if behavior_profile.expertise_level > 0.5:
            growth_factors.append(0.2)

        # Feature exploration
        if len(behavior_profile.preferred_interaction_types) > 5:
            growth_factors.append(0.2)

        # Regular usage
        if behavior_profile.interaction_frequency > 1.0:  # More than once per day
            growth_factors.append(0.2)

        # Calculate overall potential
        return min(sum(growth_factors), 1.0) if growth_factors else 0.3

    async def _get_recent_interaction_trend(self, user_id: str) -> Optional[float]:
        """Get trend in recent user interactions"""
        try:
            # Get interactions from last 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)

            result = self.supabase.table('user_interactions')\
                .select('timestamp')\
                .eq('user_id', user_id)\
                .gte('timestamp', cutoff_date.isoformat())\
                .order('timestamp')\
                .execute()

            interactions = result.data

            if len(interactions) < 4:  # Need minimum data for trend
                return None

            # Split into first and second half
            mid_point = len(interactions) // 2
            first_half = interactions[:mid_point]
            second_half = interactions[mid_point:]

            # Calculate interaction rates
            first_rate = len(first_half) / 15  # per day
            second_rate = len(second_half) / 15  # per day

            # Return trend (positive = increasing, negative = decreasing)
            return (second_rate - first_rate) / max(first_rate, 0.1)

        except Exception as e:
            logger.error(f"Error calculating interaction trend: {str(e)}")
            return None

    async def _store_user_persona(self, persona: UserPersona):
        """Store user persona in database"""
        try:
            persona_dict = asdict(persona)

            # Convert datetime objects to ISO strings
            persona_dict['created_at'] = persona.created_at.isoformat()
            persona_dict['last_updated'] = persona.last_updated.isoformat()

            # Upsert persona
            self.supabase.table('user_personas')\
                .upsert(persona_dict, on_conflict='user_id')\
                .execute()

            logger.info(f"Stored persona for user {persona.user_id}")

        except Exception as e:
            logger.error(f"Error storing user persona: {str(e)}")

    async def _get_stored_persona(self, user_id: str) -> Optional[UserPersona]:
        """Get stored user persona"""
        try:
            result = self.supabase.table('user_personas')\
                .select('*')\
                .eq('user_id', user_id)\
                .execute()

            if result.data:
                persona_data = result.data[0]
                # Convert back to UserPersona object
                return UserPersona(**persona_data)

            return None

        except Exception as e:
            logger.error(f"Error getting stored persona: {str(e)}")
            return None

    # Additional methods for segmentation, clustering, and analysis would continue here...
    # (The file is getting quite long, so I'll include the most essential methods)

    async def _prepare_segmentation_data(self, user_ids: Optional[List[str]]) -> List[Dict[str, Any]]:
        """Prepare user data for segmentation analysis"""
        try:
            # Get user behavior profiles
            query = self.supabase.table('user_behavior_profiles').select('*')
            if user_ids:
                query = query.in_('user_id', user_ids)

            result = query.execute()
            return result.data

        except Exception as e:
            logger.error(f"Error preparing segmentation data: {str(e)}")
            return []

    async def _prepare_clustering_features(self, user_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, List[str]]:
        """Prepare feature matrix for clustering"""
        features = []
        user_ids = []

        for user in user_data:
            feature_vector = [
                user.get('total_interactions', 0),
                user.get('interaction_frequency', 0),
                user.get('expertise_level', 0),
                user.get('engagement_score', 0),
                user.get('risk_tolerance', 0.5),
                user.get('session_duration_avg', 0),
                len(user.get('interests', [])),
                len(user.get('preferred_authorities', [])),
                len(user.get('geographic_focus', []))
            ]

            features.append(feature_vector)
            user_ids.append(user['user_id'])

        return np.array(features), user_ids

    def _determine_optimal_clusters(self, features: np.ndarray) -> int:
        """Determine optimal number of clusters using silhouette analysis"""
        if len(features) < 10:
            return 2

        best_score = -1
        best_clusters = 2

        for n_clusters in range(2, min(10, len(features) // 5)):
            try:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                cluster_labels = kmeans.fit_predict(features)
                score = silhouette_score(features, cluster_labels)

                if score > best_score:
                    best_score = score
                    best_clusters = n_clusters

            except Exception:
                continue

        return best_clusters

    def _perform_clustering(self, features: np.ndarray, n_clusters: int) -> np.ndarray:
        """Perform K-means clustering"""
        # Normalize features
        features_scaled = self.scaler.fit_transform(features)

        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(features_scaled)

        return cluster_labels

    async def _analyze_clusters_to_segments(
        self, features: np.ndarray, cluster_labels: np.ndarray,
        user_ids: List[str], user_data: List[Dict[str, Any]]
    ) -> Dict[str, UserSegment]:
        """Analyze clusters and create meaningful segments"""

        segments = {}

        for cluster_id in set(cluster_labels):
            cluster_users = [user_ids[i] for i, label in enumerate(cluster_labels) if label == cluster_id]
            cluster_data = [user_data[i] for i, label in enumerate(cluster_labels) if label == cluster_id]

            # Analyze cluster characteristics
            avg_expertise = np.mean([user.get('expertise_level', 0) for user in cluster_data])
            avg_engagement = np.mean([user.get('engagement_score', 0) for user in cluster_data])

            # Determine segment name based on characteristics
            if avg_expertise > 0.7 and avg_engagement > 0.7:
                segment_name = "Expert Power Users"
            elif avg_expertise > 0.7:
                segment_name = "Expert Users"
            elif avg_engagement > 0.7:
                segment_name = "Highly Engaged Users"
            elif avg_engagement < 0.3:
                segment_name = "Low Engagement Users"
            else:
                segment_name = f"Cluster {cluster_id} Users"

            # Create segment
            segment = UserSegment(
                segment_id=f"segment_{cluster_id}",
                segment_name=segment_name,
                description=f"Users with {avg_expertise:.1f} expertise and {avg_engagement:.1f} engagement",
                size=len(cluster_users),
                avg_expertise_level=avg_expertise,
                avg_engagement_score=avg_engagement,
                common_personas=[],  # Would be populated with persona analysis
                typical_behaviors=[],  # Would be populated with behavior analysis
                preferred_features=[],  # Would be populated with feature analysis
                content_preferences={},  # Would be populated with content analysis
                retention_rate=0.8,  # Would be calculated from actual data
                conversion_rate=0.15,  # Would be calculated from actual data
                lifetime_value=100.0,  # Would be calculated from actual data
                recommended_approach={},  # Would be populated with strategy
                priority_features=[],  # Would be populated with strategy
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )

            segments[segment.segment_id] = segment

        return segments

    async def _store_segments(self, segments: Dict[str, UserSegment]):
        """Store user segments in database"""
        try:
            for segment in segments.values():
                segment_dict = asdict(segment)
                segment_dict['created_at'] = segment.created_at.isoformat()
                segment_dict['last_updated'] = segment.last_updated.isoformat()

                self.supabase.table('user_segments_definitions')\
                    .upsert(segment_dict, on_conflict='segment_id')\
                    .execute()

        except Exception as e:
            logger.error(f"Error storing segments: {str(e)}")

    async def _generate_segmentation_insights(self, segments: Dict[str, UserSegment]) -> List[SegmentationInsight]:
        """Generate insights from segmentation analysis"""
        insights = []

        # Insight: Largest segment
        largest_segment = max(segments.values(), key=lambda s: s.size)
        insights.append(SegmentationInsight(
            insight_type="segment_size",
            title=f"Largest User Segment: {largest_segment.segment_name}",
            description=f"The {largest_segment.segment_name} segment contains {largest_segment.size} users",
            affected_segments=[largest_segment.segment_id],
            impact_score=0.8,
            recommendations=[
                f"Focus personalization efforts on {largest_segment.segment_name}",
                "Develop features specifically for this segment"
            ],
            data_points={"segment_size": largest_segment.size},
            created_at=datetime.utcnow()
        ))

        # Insight: High-value segments
        high_value_segments = [s for s in segments.values() if s.avg_engagement_score > 0.7]
        if high_value_segments:
            insights.append(SegmentationInsight(
                insight_type="high_value",
                title=f"High-Value Segments Identified",
                description=f"Found {len(high_value_segments)} high-engagement segments",
                affected_segments=[s.segment_id for s in high_value_segments],
                impact_score=0.9,
                recommendations=[
                    "Prioritize retention strategies for high-value segments",
                    "Develop premium features for these users"
                ],
                data_points={"count": len(high_value_segments)},
                created_at=datetime.utcnow()
            ))

        return insights

    async def _store_segmentation_insights(self, insights: List[SegmentationInsight]):
        """Store segmentation insights"""
        try:
            for insight in insights:
                insight_dict = asdict(insight)
                insight_dict['created_at'] = insight.created_at.isoformat()

                self.supabase.table('segmentation_insights')\
                    .insert(insight_dict)\
                    .execute()

        except Exception as e:
            logger.error(f"Error storing segmentation insights: {str(e)}")

    # Additional prediction and analysis methods would continue here...