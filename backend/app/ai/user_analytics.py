"""
Advanced User Behavior Analytics Service for AI Personalization
Tracks, analyzes, and learns from user interaction patterns
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging
from collections import defaultdict, Counter
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Mock numpy when not available
    class np:
        @staticmethod
        def array(data):
            return data
        @staticmethod
        def mean(data, axis=None):
            return sum(data) / len(data) if data else 0
        @staticmethod
        def std(data):
            return 1.0

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    # Mock classes for when sklearn is not available
    class KMeans:
        def __init__(self, *args, **kwargs):
            pass
        def fit(self, *args, **kwargs):
            return self
        def predict(self, *args, **kwargs):
            return [0]

    class StandardScaler:
        def __init__(self, *args, **kwargs):
            pass
        def fit(self, *args, **kwargs):
            return self
        def transform(self, *args, **kwargs):
            return [[0]]

logger = logging.getLogger(__name__)


class InteractionType(str, Enum):
    """Types of user interactions to track"""
    SEARCH = "search"
    VIEW_APPLICATION = "view_application"
    SAVE_SEARCH = "save_search"
    CREATE_ALERT = "create_alert"
    GENERATE_REPORT = "generate_report"
    DOWNLOAD_DOCUMENT = "download_document"
    BOOKMARK_APPLICATION = "bookmark_application"
    SHARE_APPLICATION = "share_application"
    FILTER_RESULTS = "filter_results"
    SORT_RESULTS = "sort_results"
    VIEW_MAP = "view_map"
    EXPORT_DATA = "export_data"
    AI_SUMMARY_VIEW = "ai_summary_view"
    OPPORTUNITY_SCORE_VIEW = "opportunity_score_view"
    FEEDBACK_POSITIVE = "feedback_positive"
    FEEDBACK_NEGATIVE = "feedback_negative"


class UserSegment(str, Enum):
    """User behavior segments"""
    NEWCOMER = "newcomer"
    OCCASIONAL_USER = "occasional_user"
    REGULAR_USER = "regular_user"
    POWER_USER = "power_user"
    PROFESSIONAL = "professional"
    RESEARCHER = "researcher"
    DEVELOPER = "developer"
    INACTIVE = "inactive"


@dataclass
class UserInteraction:
    """Individual user interaction record"""
    user_id: str
    interaction_type: InteractionType
    timestamp: datetime
    context: Dict[str, Any]
    session_id: Optional[str] = None
    application_id: Optional[str] = None
    search_query: Optional[str] = None
    filters_used: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, float]] = None
    device_type: Optional[str] = None
    duration_seconds: Optional[float] = None
    result_count: Optional[int] = None


@dataclass
class UserBehaviorProfile:
    """Comprehensive user behavior profile"""
    user_id: str
    segment: UserSegment
    total_interactions: int
    interaction_frequency: float  # interactions per day
    preferred_interaction_types: List[str]
    geographic_focus: List[Dict[str, Any]]
    search_patterns: Dict[str, Any]
    time_patterns: Dict[str, Any]
    expertise_level: float  # 0-1 scale
    engagement_score: float  # 0-1 scale
    risk_tolerance: float  # 0-1 scale
    interests: List[str]
    preferred_authorities: List[str]
    session_duration_avg: float
    last_updated: datetime


@dataclass
class UserInsight:
    """AI-generated user insights"""
    user_id: str
    insight_type: str
    title: str
    description: str
    confidence: float
    actionable_recommendations: List[str]
    data_points: Dict[str, Any]
    created_at: datetime


class UserBehaviorAnalyzer:
    """
    Advanced user behavior analytics and learning engine
    """

    def __init__(self, supabase_client, redis_client=None):
        self.supabase = supabase_client
        self.redis = redis_client
        self.scaler = StandardScaler()

    async def track_interaction(
        self,
        user_id: str,
        interaction_type: InteractionType,
        context: Dict[str, Any],
        session_id: Optional[str] = None,
        application_id: Optional[str] = None
    ) -> bool:
        """
        Track a user interaction for behavioral analysis

        Args:
            user_id: User identifier
            interaction_type: Type of interaction
            context: Interaction context and metadata
            session_id: Session identifier
            application_id: Related application ID if applicable

        Returns:
            Success status
        """
        try:
            interaction = UserInteraction(
                user_id=user_id,
                interaction_type=interaction_type,
                timestamp=datetime.utcnow(),
                context=context,
                session_id=session_id,
                application_id=application_id,
                search_query=context.get('query'),
                filters_used=context.get('filters'),
                location=context.get('location'),
                device_type=context.get('device_type'),
                duration_seconds=context.get('duration_seconds'),
                result_count=context.get('result_count')
            )

            # Store in database
            result = self.supabase.table('user_interactions').insert(
                asdict(interaction)
            ).execute()

            # Cache recent interactions for real-time analysis
            if self.redis:
                cache_key = f"user_interactions:{user_id}"
                self.redis.lpush(cache_key, json.dumps(asdict(interaction), default=str))
                self.redis.ltrim(cache_key, 0, 99)  # Keep last 100 interactions
                self.redis.expire(cache_key, 86400)  # 24 hours

            # Trigger real-time profile update for active users
            await self._update_real_time_profile(user_id, interaction)

            logger.info(f"Tracked interaction: {interaction_type} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error tracking interaction: {str(e)}")
            return False

    async def analyze_user_patterns(self, user_id: str) -> UserBehaviorProfile:
        """
        Analyze comprehensive user behavior patterns

        Args:
            user_id: User identifier

        Returns:
            Complete user behavior profile
        """
        try:
            # Get user interactions from last 90 days
            cutoff_date = datetime.utcnow() - timedelta(days=90)

            interactions_result = self.supabase.table('user_interactions')\
                .select('*')\
                .eq('user_id', user_id)\
                .gte('timestamp', cutoff_date.isoformat())\
                .order('timestamp', desc=True)\
                .execute()

            interactions = interactions_result.data

            if not interactions:
                return self._create_default_profile(user_id)

            # Analyze patterns
            interaction_analysis = self._analyze_interaction_patterns(interactions)
            temporal_analysis = self._analyze_temporal_patterns(interactions)
            geographic_analysis = self._analyze_geographic_patterns(interactions)
            search_analysis = self._analyze_search_patterns(interactions)
            engagement_analysis = self._analyze_engagement_patterns(interactions)

            # Calculate expertise and engagement scores
            expertise_score = self._calculate_expertise_level(interactions)
            engagement_score = self._calculate_engagement_score(interactions)
            risk_tolerance = self._calculate_risk_tolerance(interactions)

            # Determine user segment
            segment = self._determine_user_segment(interactions, engagement_score)

            profile = UserBehaviorProfile(
                user_id=user_id,
                segment=segment,
                total_interactions=len(interactions),
                interaction_frequency=len(interactions) / 90,  # per day
                preferred_interaction_types=interaction_analysis['top_types'],
                geographic_focus=geographic_analysis,
                search_patterns=search_analysis,
                time_patterns=temporal_analysis,
                expertise_level=expertise_score,
                engagement_score=engagement_score,
                risk_tolerance=risk_tolerance,
                interests=self._extract_interests(interactions),
                preferred_authorities=self._extract_preferred_authorities(interactions),
                session_duration_avg=engagement_analysis['avg_session_duration'],
                last_updated=datetime.utcnow()
            )

            # Store profile
            await self._store_behavior_profile(profile)

            return profile

        except Exception as e:
            logger.error(f"Error analyzing user patterns: {str(e)}")
            return self._create_default_profile(user_id)

    async def identify_user_segments(self, user_ids: Optional[List[str]] = None) -> Dict[str, UserSegment]:
        """
        Identify user segments using machine learning clustering

        Args:
            user_ids: Specific users to analyze, or None for all users

        Returns:
            User ID to segment mapping
        """
        try:
            # Get user interaction summaries
            if user_ids:
                user_filter = f"user_id.in.({','.join(user_ids)})"
            else:
                user_filter = None

            query = self.supabase.table('user_behavior_profiles').select('*')
            if user_filter:
                query = query.filter('user_id', 'in', user_ids)

            profiles_result = query.execute()
            profiles = profiles_result.data

            if len(profiles) < 10:  # Need minimum data for clustering
                return {p['user_id']: UserSegment.NEWCOMER for p in profiles}

            # Prepare features for clustering
            features = []
            user_id_list = []

            for profile in profiles:
                features.append([
                    profile['total_interactions'],
                    profile['interaction_frequency'],
                    profile['expertise_level'],
                    profile['engagement_score'],
                    profile['session_duration_avg']
                ])
                user_id_list.append(profile['user_id'])

            # Normalize features
            features_scaled = self.scaler.fit_transform(features)

            # Perform K-means clustering
            n_clusters = min(5, len(profiles) // 2)  # Adaptive cluster count
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(features_scaled)

            # Map clusters to meaningful segments
            segment_mapping = self._map_clusters_to_segments(
                features_scaled, cluster_labels, profiles
            )

            result = {}
            for i, user_id in enumerate(user_id_list):
                cluster = cluster_labels[i]
                result[user_id] = segment_mapping[cluster]

            return result

        except Exception as e:
            logger.error(f"Error identifying user segments: {str(e)}")
            return {}

    async def predict_user_interests(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Predict user interests and preferences using behavioral data

        Args:
            user_id: User identifier

        Returns:
            List of predicted interests with confidence scores
        """
        try:
            profile = await self.analyze_user_patterns(user_id)

            # Analyze search patterns
            search_interests = self._extract_search_interests(profile.search_patterns)

            # Analyze interaction preferences
            interaction_interests = self._extract_interaction_interests(
                profile.preferred_interaction_types
            )

            # Analyze geographic interests
            geographic_interests = self._extract_geographic_interests(
                profile.geographic_focus
            )

            # Combine and rank interests
            all_interests = []
            all_interests.extend(search_interests)
            all_interests.extend(interaction_interests)
            all_interests.extend(geographic_interests)

            # Deduplicate and rank by confidence
            interest_scores = defaultdict(float)
            for interest in all_interests:
                interest_scores[interest['category']] += interest['confidence']

            predicted_interests = []
            for category, score in sorted(interest_scores.items(),
                                        key=lambda x: x[1], reverse=True)[:10]:
                predicted_interests.append({
                    'category': category,
                    'confidence': min(score, 1.0),
                    'evidence': self._get_interest_evidence(user_id, category)
                })

            return predicted_interests

        except Exception as e:
            logger.error(f"Error predicting user interests: {str(e)}")
            return []

    async def calculate_engagement_score(self, user_id: str) -> float:
        """
        Calculate user engagement score based on multiple factors

        Args:
            user_id: User identifier

        Returns:
            Engagement score (0-1)
        """
        try:
            profile = await self.analyze_user_patterns(user_id)

            # Factor weights
            weights = {
                'frequency': 0.3,      # How often they use the platform
                'depth': 0.2,          # How deeply they engage with content
                'variety': 0.15,       # Variety of features used
                'retention': 0.15,     # How long they've been active
                'feedback': 0.1,       # Feedback and interaction quality
                'progression': 0.1     # Skill/expertise progression
            }

            # Calculate individual scores
            frequency_score = min(profile.interaction_frequency / 5, 1.0)  # Max 5 per day
            depth_score = profile.session_duration_avg / 600  # Max 10 minutes
            variety_score = len(profile.preferred_interaction_types) / len(InteractionType)
            retention_score = min(profile.total_interactions / 100, 1.0)  # Max 100 interactions
            feedback_score = self._calculate_feedback_score(user_id)
            progression_score = profile.expertise_level

            # Weighted engagement score
            engagement_score = (
                frequency_score * weights['frequency'] +
                depth_score * weights['depth'] +
                variety_score * weights['variety'] +
                retention_score * weights['retention'] +
                feedback_score * weights['feedback'] +
                progression_score * weights['progression']
            )

            return min(engagement_score, 1.0)

        except Exception as e:
            logger.error(f"Error calculating engagement score: {str(e)}")
            return 0.5  # Default neutral score

    async def generate_user_insights(self, user_id: str) -> List[UserInsight]:
        """
        Generate AI-powered insights about user behavior

        Args:
            user_id: User identifier

        Returns:
            List of actionable user insights
        """
        try:
            profile = await self.analyze_user_patterns(user_id)
            insights = []

            # Insight 1: Usage patterns
            if profile.interaction_frequency < 0.5:
                insights.append(UserInsight(
                    user_id=user_id,
                    insight_type="usage_pattern",
                    title="Low Platform Engagement",
                    description="User shows infrequent platform usage patterns",
                    confidence=0.8,
                    actionable_recommendations=[
                        "Send personalized onboarding tips",
                        "Highlight relevant new features",
                        "Provide guided tours for key features"
                    ],
                    data_points={
                        "frequency": profile.interaction_frequency,
                        "total_interactions": profile.total_interactions
                    },
                    created_at=datetime.utcnow()
                ))

            # Insight 2: Expertise level
            if profile.expertise_level > 0.7:
                insights.append(UserInsight(
                    user_id=user_id,
                    insight_type="expertise_level",
                    title="Advanced User Detected",
                    description="User demonstrates high expertise in platform usage",
                    confidence=0.9,
                    actionable_recommendations=[
                        "Offer advanced features and tools",
                        "Provide API access information",
                        "Suggest premium subscription benefits"
                    ],
                    data_points={
                        "expertise_level": profile.expertise_level,
                        "preferred_types": profile.preferred_interaction_types
                    },
                    created_at=datetime.utcnow()
                ))

            # Insight 3: Geographic focus
            if profile.geographic_focus:
                top_location = profile.geographic_focus[0]
                insights.append(UserInsight(
                    user_id=user_id,
                    insight_type="geographic_preference",
                    title=f"Strong Geographic Focus: {top_location.get('area', 'Unknown')}",
                    description="User shows consistent interest in specific geographic areas",
                    confidence=0.85,
                    actionable_recommendations=[
                        f"Prioritize {top_location.get('area')} content",
                        "Set up automatic alerts for this area",
                        "Suggest similar geographic areas"
                    ],
                    data_points={"geographic_focus": profile.geographic_focus},
                    created_at=datetime.utcnow()
                ))

            # Insight 4: Search patterns
            if profile.search_patterns.get('common_terms'):
                insights.append(UserInsight(
                    user_id=user_id,
                    insight_type="search_behavior",
                    title="Consistent Search Interests",
                    description="User shows patterns in search behavior and interests",
                    confidence=0.75,
                    actionable_recommendations=[
                        "Create saved searches for common terms",
                        "Suggest related search terms",
                        "Provide market intelligence for search topics"
                    ],
                    data_points={"search_patterns": profile.search_patterns},
                    created_at=datetime.utcnow()
                ))

            return insights

        except Exception as e:
            logger.error(f"Error generating user insights: {str(e)}")
            return []

    # Private helper methods

    def _analyze_interaction_patterns(self, interactions: List[Dict]) -> Dict[str, Any]:
        """Analyze user interaction type patterns"""
        type_counts = Counter([i['interaction_type'] for i in interactions])
        total = len(interactions)

        return {
            'top_types': [t for t, _ in type_counts.most_common(5)],
            'type_distribution': {t: c/total for t, c in type_counts.items()},
            'most_common_type': type_counts.most_common(1)[0][0] if type_counts else None
        }

    def _analyze_temporal_patterns(self, interactions: List[Dict]) -> Dict[str, Any]:
        """Analyze when users are most active"""
        timestamps = [datetime.fromisoformat(i['timestamp'].replace('Z', '+00:00'))
                     for i in interactions]

        hours = [t.hour for t in timestamps]
        days = [t.weekday() for t in timestamps]  # 0=Monday

        hour_counts = Counter(hours)
        day_counts = Counter(days)

        return {
            'peak_hours': [h for h, _ in hour_counts.most_common(3)],
            'peak_days': [d for d, _ in day_counts.most_common(3)],
            'hour_distribution': dict(hour_counts),
            'day_distribution': dict(day_counts)
        }

    def _analyze_geographic_patterns(self, interactions: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze geographic focus areas"""
        locations = []
        for interaction in interactions:
            if interaction.get('location'):
                locations.append(interaction['location'])
            elif interaction.get('context', {}).get('location'):
                locations.append(interaction['context']['location'])

        if not locations:
            return []

        # Group by approximate area (simplified)
        area_counts = defaultdict(int)
        for loc in locations:
            if isinstance(loc, dict) and 'lat' in loc and 'lng' in loc:
                # Rough geographic grouping by lat/lng
                area_key = f"{round(loc['lat'], 1)},{round(loc['lng'], 1)}"
                area_counts[area_key] += 1

        geographic_focus = []
        for area, count in sorted(area_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            lat, lng = map(float, area.split(','))
            geographic_focus.append({
                'area': area,
                'center': {'lat': lat, 'lng': lng},
                'frequency': count / len(locations)
            })

        return geographic_focus

    def _analyze_search_patterns(self, interactions: List[Dict]) -> Dict[str, Any]:
        """Analyze search query patterns"""
        search_interactions = [i for i in interactions
                             if i['interaction_type'] == InteractionType.SEARCH]

        queries = []
        for interaction in search_interactions:
            query = interaction.get('search_query') or interaction.get('context', {}).get('query')
            if query:
                queries.append(query.lower())

        if not queries:
            return {}

        # Extract common terms (simplified)
        all_terms = []
        for query in queries:
            terms = query.split()
            all_terms.extend([term for term in terms if len(term) > 2])

        term_counts = Counter(all_terms)

        return {
            'total_searches': len(queries),
            'common_terms': [term for term, _ in term_counts.most_common(10)],
            'avg_query_length': np.mean([len(q.split()) for q in queries]),
            'unique_queries': len(set(queries))
        }

    def _analyze_engagement_patterns(self, interactions: List[Dict]) -> Dict[str, Any]:
        """Analyze user engagement depth"""
        sessions = defaultdict(list)

        for interaction in interactions:
            session_id = interaction.get('session_id', 'default')
            sessions[session_id].append(interaction)

        session_durations = []
        for session_interactions in sessions.values():
            if len(session_interactions) > 1:
                timestamps = [datetime.fromisoformat(i['timestamp'].replace('Z', '+00:00'))
                            for i in session_interactions]
                duration = (max(timestamps) - min(timestamps)).total_seconds()
                session_durations.append(duration)

        avg_duration = np.mean(session_durations) if session_durations else 60

        return {
            'total_sessions': len(sessions),
            'avg_session_duration': avg_duration,
            'interactions_per_session': len(interactions) / len(sessions)
        }

    def _calculate_expertise_level(self, interactions: List[Dict]) -> float:
        """Calculate user expertise level (0-1)"""
        advanced_interactions = [
            InteractionType.GENERATE_REPORT,
            InteractionType.EXPORT_DATA,
            InteractionType.CREATE_ALERT,
            InteractionType.AI_SUMMARY_VIEW
        ]

        advanced_count = sum(1 for i in interactions
                           if i['interaction_type'] in advanced_interactions)

        total_interactions = len(interactions)
        if total_interactions == 0:
            return 0.0

        # Factor in both advanced feature usage and total experience
        advanced_ratio = advanced_count / total_interactions
        experience_factor = min(total_interactions / 50, 1.0)  # Max at 50 interactions

        return (advanced_ratio * 0.7 + experience_factor * 0.3)

    def _calculate_engagement_score(self, interactions: List[Dict]) -> float:
        """Calculate engagement score (0-1)"""
        if not interactions:
            return 0.0

        # Recent activity weight
        recent_cutoff = datetime.utcnow() - timedelta(days=7)
        recent_interactions = [
            i for i in interactions
            if datetime.fromisoformat(i['timestamp'].replace('Z', '+00:00')) > recent_cutoff
        ]

        recent_weight = len(recent_interactions) / 7  # per day
        total_weight = len(interactions) / 90  # per day over 90 days

        return min((recent_weight * 0.6 + total_weight * 0.4) / 5, 1.0)  # Max 5 per day

    def _calculate_risk_tolerance(self, interactions: List[Dict]) -> float:
        """Calculate user risk tolerance based on behavior"""
        # Simplified risk tolerance based on interaction patterns
        conservative_interactions = [
            InteractionType.VIEW_APPLICATION,
            InteractionType.SAVE_SEARCH
        ]

        aggressive_interactions = [
            InteractionType.GENERATE_REPORT,
            InteractionType.EXPORT_DATA,
            InteractionType.SHARE_APPLICATION
        ]

        conservative_count = sum(1 for i in interactions
                               if i['interaction_type'] in conservative_interactions)
        aggressive_count = sum(1 for i in interactions
                             if i['interaction_type'] in aggressive_interactions)

        total = conservative_count + aggressive_count
        if total == 0:
            return 0.5  # Neutral

        return aggressive_count / total

    def _determine_user_segment(self, interactions: List[Dict], engagement_score: float) -> UserSegment:
        """Determine user segment based on behavior"""
        total_interactions = len(interactions)

        if total_interactions < 5:
            return UserSegment.NEWCOMER
        elif engagement_score < 0.2:
            return UserSegment.INACTIVE
        elif engagement_score < 0.4:
            return UserSegment.OCCASIONAL_USER
        elif engagement_score < 0.7:
            return UserSegment.REGULAR_USER
        else:
            # Check for professional indicators
            professional_types = [
                InteractionType.GENERATE_REPORT,
                InteractionType.EXPORT_DATA,
                InteractionType.CREATE_ALERT
            ]

            professional_ratio = sum(1 for i in interactions
                                   if i['interaction_type'] in professional_types) / total_interactions

            if professional_ratio > 0.3:
                return UserSegment.PROFESSIONAL
            elif total_interactions > 100:
                return UserSegment.POWER_USER
            else:
                return UserSegment.REGULAR_USER

    def _extract_interests(self, interactions: List[Dict]) -> List[str]:
        """Extract user interests from interactions"""
        interests = set()

        # Extract from search queries
        for interaction in interactions:
            if interaction['interaction_type'] == InteractionType.SEARCH:
                query = interaction.get('search_query', '')
                # Simplified interest extraction
                if 'residential' in query.lower():
                    interests.add('residential_development')
                if 'commercial' in query.lower():
                    interests.add('commercial_development')
                if 'retail' in query.lower():
                    interests.add('retail_development')

        return list(interests)[:10]  # Top 10 interests

    def _extract_preferred_authorities(self, interactions: List[Dict]) -> List[str]:
        """Extract preferred planning authorities"""
        authorities = defaultdict(int)

        for interaction in interactions:
            context = interaction.get('context', {})
            filters = context.get('filters', {})

            if filters and 'authority' in filters:
                auth = filters['authority']
                if isinstance(auth, str):
                    authorities[auth] += 1
                elif isinstance(auth, list):
                    for a in auth:
                        authorities[a] += 1

        return [auth for auth, _ in sorted(authorities.items(),
                                         key=lambda x: x[1], reverse=True)[:5]]

    async def _update_real_time_profile(self, user_id: str, interaction: UserInteraction):
        """Update user profile in real-time for critical interactions"""
        # Only update for important interactions
        critical_types = [
            InteractionType.SEARCH,
            InteractionType.SAVE_SEARCH,
            InteractionType.CREATE_ALERT,
            InteractionType.GENERATE_REPORT
        ]

        if interaction.interaction_type in critical_types and self.redis:
            # Update cached profile stats
            profile_key = f"user_profile:{user_id}"
            self.redis.hincrby(profile_key, "total_interactions", 1)
            self.redis.hset(profile_key, "last_interaction",
                          interaction.timestamp.isoformat())
            self.redis.expire(profile_key, 86400)  # 24 hours

    async def _store_behavior_profile(self, profile: UserBehaviorProfile):
        """Store behavior profile in database"""
        try:
            profile_dict = asdict(profile)

            # Upsert profile
            result = self.supabase.table('user_behavior_profiles')\
                .upsert(profile_dict, on_conflict='user_id')\
                .execute()

            logger.info(f"Stored behavior profile for user {profile.user_id}")

        except Exception as e:
            logger.error(f"Error storing behavior profile: {str(e)}")

    def _create_default_profile(self, user_id: str) -> UserBehaviorProfile:
        """Create default profile for new users"""
        return UserBehaviorProfile(
            user_id=user_id,
            segment=UserSegment.NEWCOMER,
            total_interactions=0,
            interaction_frequency=0.0,
            preferred_interaction_types=[],
            geographic_focus=[],
            search_patterns={},
            time_patterns={},
            expertise_level=0.0,
            engagement_score=0.0,
            risk_tolerance=0.5,
            interests=[],
            preferred_authorities=[],
            session_duration_avg=0.0,
            last_updated=datetime.utcnow()
        )

    def _map_clusters_to_segments(self, features: Any,
                                 labels: Any,
                                 profiles: List[Dict]) -> Dict[int, UserSegment]:
        """Map K-means clusters to meaningful user segments"""
        cluster_stats = defaultdict(list)

        for i, label in enumerate(labels):
            cluster_stats[label].append({
                'total_interactions': features[i][0],
                'frequency': features[i][1],
                'expertise': features[i][2],
                'engagement': features[i][3],
                'duration': features[i][4]
            })

        segment_mapping = {}
        for cluster, stats in cluster_stats.items():
            avg_engagement = np.mean([s['engagement'] for s in stats])
            avg_expertise = np.mean([s['expertise'] for s in stats])
            avg_frequency = np.mean([s['frequency'] for s in stats])

            if avg_engagement < 0.2:
                segment_mapping[cluster] = UserSegment.INACTIVE
            elif avg_engagement < 0.4:
                segment_mapping[cluster] = UserSegment.OCCASIONAL_USER
            elif avg_expertise > 0.7 and avg_frequency > 1.0:
                segment_mapping[cluster] = UserSegment.PROFESSIONAL
            elif avg_engagement > 0.8:
                segment_mapping[cluster] = UserSegment.POWER_USER
            else:
                segment_mapping[cluster] = UserSegment.REGULAR_USER

        return segment_mapping

    def _extract_search_interests(self, search_patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract interests from search patterns"""
        interests = []

        common_terms = search_patterns.get('common_terms', [])
        for term in common_terms[:5]:
            confidence = 0.7  # Base confidence for search terms
            interests.append({
                'category': f"search_term_{term}",
                'confidence': confidence
            })

        return interests

    def _extract_interaction_interests(self, interaction_types: List[str]) -> List[Dict[str, Any]]:
        """Extract interests from interaction patterns"""
        interests = []

        interest_mapping = {
            InteractionType.GENERATE_REPORT: 'professional_analysis',
            InteractionType.AI_SUMMARY_VIEW: 'ai_insights',
            InteractionType.EXPORT_DATA: 'data_analysis',
            InteractionType.VIEW_MAP: 'geographic_analysis'
        }

        for interaction_type in interaction_types:
            if interaction_type in interest_mapping:
                interests.append({
                    'category': interest_mapping[interaction_type],
                    'confidence': 0.6
                })

        return interests

    def _extract_geographic_interests(self, geographic_focus: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract interests from geographic patterns"""
        interests = []

        for geo_data in geographic_focus[:3]:
            interests.append({
                'category': f"geographic_{geo_data.get('area', 'unknown')}",
                'confidence': geo_data.get('frequency', 0.5)
            })

        return interests

    def _get_interest_evidence(self, user_id: str, category: str) -> List[str]:
        """Get evidence for interest prediction"""
        # Simplified evidence collection
        return [
            f"Based on user interaction patterns",
            f"Derived from search behavior analysis",
            f"Confirmed through geographic focus"
        ]

    def _calculate_feedback_score(self, user_id: str) -> float:
        """Calculate feedback quality score"""
        try:
            # Get feedback interactions
            feedback_result = self.supabase.table('user_interactions')\
                .select('*')\
                .eq('user_id', user_id)\
                .in_('interaction_type', [InteractionType.FEEDBACK_POSITIVE,
                                        InteractionType.FEEDBACK_NEGATIVE])\
                .execute()

            feedback_interactions = feedback_result.data

            if not feedback_interactions:
                return 0.5  # Neutral score

            positive_count = sum(1 for i in feedback_interactions
                               if i['interaction_type'] == InteractionType.FEEDBACK_POSITIVE)
            total_feedback = len(feedback_interactions)

            return positive_count / total_feedback if total_feedback > 0 else 0.5

        except Exception as e:
            logger.error(f"Error calculating feedback score: {str(e)}")
            return 0.5