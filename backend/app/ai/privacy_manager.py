"""
Privacy and Consent Management System for AI Personalization
Ensures GDPR compliance and ethical AI practices
"""
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging
import hashlib
import uuid

logger = logging.getLogger(__name__)


class ConsentType(str, Enum):
    """Types of consent for different data processing activities"""
    PERSONALIZATION = "personalization"
    BEHAVIORAL_TRACKING = "behavioral_tracking"
    AI_LEARNING = "ai_learning"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    THIRD_PARTY_SHARING = "third_party_sharing"
    PROFILE_ENHANCEMENT = "profile_enhancement"
    RECOMMENDATION_GENERATION = "recommendation_generation"


class ConsentStatus(str, Enum):
    """Status of user consent"""
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"


class DataCategory(str, Enum):
    """Categories of data for privacy management"""
    BEHAVIORAL_DATA = "behavioral_data"
    SEARCH_HISTORY = "search_history"
    INTERACTION_PATTERNS = "interaction_patterns"
    PREFERENCES = "preferences"
    LOCATION_DATA = "location_data"
    DEVICE_INFO = "device_info"
    DEMOGRAPHIC_DATA = "demographic_data"
    PERFORMANCE_METRICS = "performance_metrics"


class ProcessingPurpose(str, Enum):
    """Purposes for data processing"""
    PERSONALIZATION = "personalization"
    SERVICE_IMPROVEMENT = "service_improvement"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    RESEARCH = "research"
    LEGAL_COMPLIANCE = "legal_compliance"
    SECURITY = "security"


@dataclass
class ConsentRecord:
    """Individual consent record"""
    consent_id: str
    user_id: str
    consent_type: ConsentType
    status: ConsentStatus
    granted_at: Optional[datetime]
    withdrawn_at: Optional[datetime]
    expires_at: Optional[datetime]
    purpose: str
    data_categories: List[DataCategory]
    processing_details: Dict[str, Any]
    legal_basis: str
    consent_version: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    withdrawal_reason: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class PrivacySettings:
    """User privacy settings"""
    user_id: str
    personalization_enabled: bool
    behavioral_tracking_enabled: bool
    ai_learning_enabled: bool
    analytics_enabled: bool
    data_retention_period_days: int
    anonymization_level: str  # 'none', 'partial', 'full'
    export_format_preference: str
    notification_preferences: Dict[str, bool]
    third_party_sharing_allowed: bool
    profile_visibility: str  # 'private', 'anonymous', 'public'
    data_portability_enabled: bool
    automated_decision_making_consent: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class DataProcessingLog:
    """Log of data processing activities"""
    log_id: str
    user_id: str
    processing_purpose: ProcessingPurpose
    data_categories: List[DataCategory]
    processing_details: Dict[str, Any]
    legal_basis: str
    consent_reference: Optional[str]
    retention_period: Optional[int]
    processor_id: str
    processing_location: str
    automated: bool
    timestamp: datetime


@dataclass
class PrivacyImpactAssessment:
    """Privacy impact assessment for AI features"""
    assessment_id: str
    feature_name: str
    data_categories: List[DataCategory]
    processing_purposes: List[ProcessingPurpose]
    risk_level: str  # 'low', 'medium', 'high'
    risk_factors: List[str]
    mitigation_measures: List[str]
    compliance_requirements: List[str]
    assessment_date: datetime
    reviewer: str
    approved: bool


class PrivacyManager:
    """
    Comprehensive privacy and consent management system
    """

    def __init__(self, supabase_client, redis_client=None):
        self.supabase = supabase_client
        self.redis = redis_client

        # Privacy configuration
        self.default_retention_period_days = 365
        self.consent_expiry_period_days = 365
        self.anonymization_threshold_days = 730
        self.minimum_age_requirement = 13

        # GDPR compliance settings
        self.gdpr_enabled = True
        self.ccpa_enabled = True
        self.cookie_consent_required = True

    async def request_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        purpose: str,
        data_categories: List[DataCategory],
        processing_details: Dict[str, Any],
        legal_basis: str = "consent",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Request user consent for data processing

        Args:
            user_id: User identifier
            consent_type: Type of consent being requested
            purpose: Purpose of data processing
            data_categories: Categories of data to be processed
            processing_details: Details about processing activities
            legal_basis: Legal basis for processing
            ip_address: User's IP address
            user_agent: User's browser agent

        Returns:
            Consent request ID
        """
        try:
            consent_id = str(uuid.uuid4())

            # Create consent record
            consent_record = ConsentRecord(
                consent_id=consent_id,
                user_id=user_id,
                consent_type=consent_type,
                status=ConsentStatus.PENDING,
                granted_at=None,
                withdrawn_at=None,
                expires_at=datetime.utcnow() + timedelta(days=self.consent_expiry_period_days),
                purpose=purpose,
                data_categories=data_categories,
                processing_details=processing_details,
                legal_basis=legal_basis,
                consent_version="1.0",
                ip_address=ip_address,
                user_agent=user_agent,
                withdrawal_reason=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Store consent record
            await self._store_consent_record(consent_record)

            # Log consent request
            await self._log_privacy_event(user_id, "consent_requested", {
                'consent_id': consent_id,
                'consent_type': consent_type.value,
                'purpose': purpose
            })

            logger.info(f"Consent requested for user {user_id}: {consent_type}")
            return consent_id

        except Exception as e:
            logger.error(f"Error requesting consent: {str(e)}")
            raise

    async def grant_consent(
        self,
        consent_id: str,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Grant user consent for data processing

        Args:
            consent_id: Consent record identifier
            user_id: User identifier
            ip_address: User's IP address
            user_agent: User's browser agent

        Returns:
            Success status
        """
        try:
            # Get consent record
            consent_record = await self._get_consent_record(consent_id)

            if not consent_record or consent_record.user_id != user_id:
                logger.warning(f"Invalid consent record: {consent_id}")
                return False

            # Update consent status
            consent_record.status = ConsentStatus.GRANTED
            consent_record.granted_at = datetime.utcnow()
            consent_record.updated_at = datetime.utcnow()

            if ip_address:
                consent_record.ip_address = ip_address
            if user_agent:
                consent_record.user_agent = user_agent

            # Store updated record
            await self._store_consent_record(consent_record)

            # Update user privacy settings
            await self._update_privacy_settings_from_consent(user_id, consent_record)

            # Log consent granted
            await self._log_privacy_event(user_id, "consent_granted", {
                'consent_id': consent_id,
                'consent_type': consent_record.consent_type.value
            })

            # Enable corresponding AI features
            await self._enable_ai_features(user_id, consent_record)

            logger.info(f"Consent granted for user {user_id}: {consent_record.consent_type}")
            return True

        except Exception as e:
            logger.error(f"Error granting consent: {str(e)}")
            return False

    async def withdraw_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        withdrawal_reason: Optional[str] = None
    ) -> bool:
        """
        Withdraw user consent and stop related processing

        Args:
            user_id: User identifier
            consent_type: Type of consent to withdraw
            withdrawal_reason: Optional reason for withdrawal

        Returns:
            Success status
        """
        try:
            # Get active consent records for this type
            consent_records = await self._get_user_consents(user_id, consent_type, ConsentStatus.GRANTED)

            for consent_record in consent_records:
                # Update consent status
                consent_record.status = ConsentStatus.WITHDRAWN
                consent_record.withdrawn_at = datetime.utcnow()
                consent_record.withdrawal_reason = withdrawal_reason
                consent_record.updated_at = datetime.utcnow()

                # Store updated record
                await self._store_consent_record(consent_record)

                # Log withdrawal
                await self._log_privacy_event(user_id, "consent_withdrawn", {
                    'consent_id': consent_record.consent_id,
                    'consent_type': consent_type.value,
                    'reason': withdrawal_reason
                })

            # Update privacy settings
            await self._disable_features_for_withdrawn_consent(user_id, consent_type)

            # Stop related data processing
            await self._stop_data_processing(user_id, consent_type)

            # Anonymize or delete data if required
            await self._handle_data_after_consent_withdrawal(user_id, consent_type)

            logger.info(f"Consent withdrawn for user {user_id}: {consent_type}")
            return True

        except Exception as e:
            logger.error(f"Error withdrawing consent: {str(e)}")
            return False

    async def check_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        purpose: Optional[str] = None
    ) -> bool:
        """
        Check if user has valid consent for specific processing

        Args:
            user_id: User identifier
            consent_type: Type of consent to check
            purpose: Optional specific purpose to check

        Returns:
            True if valid consent exists
        """
        try:
            # Get active consent records
            consent_records = await self._get_user_consents(user_id, consent_type, ConsentStatus.GRANTED)

            for consent_record in consent_records:
                # Check if consent is still valid (not expired)
                if consent_record.expires_at and consent_record.expires_at < datetime.utcnow():
                    # Mark as expired
                    consent_record.status = ConsentStatus.EXPIRED
                    consent_record.updated_at = datetime.utcnow()
                    await self._store_consent_record(consent_record)
                    continue

                # Check purpose if specified
                if purpose and purpose not in consent_record.purpose:
                    continue

                # Valid consent found
                return True

            return False

        except Exception as e:
            logger.error(f"Error checking consent: {str(e)}")
            return False

    async def get_user_privacy_settings(self, user_id: str) -> PrivacySettings:
        """
        Get user's privacy settings

        Args:
            user_id: User identifier

        Returns:
            User's privacy settings
        """
        try:
            result = self.supabase.table('user_privacy_settings')\
                .select('*')\
                .eq('user_id', user_id)\
                .execute()

            if result.data:
                settings_data = result.data[0]
                return PrivacySettings(**settings_data)
            else:
                # Return default settings
                return await self._create_default_privacy_settings(user_id)

        except Exception as e:
            logger.error(f"Error getting privacy settings: {str(e)}")
            return await self._create_default_privacy_settings(user_id)

    async def update_privacy_settings(
        self,
        user_id: str,
        settings_updates: Dict[str, Any]
    ) -> PrivacySettings:
        """
        Update user's privacy settings

        Args:
            user_id: User identifier
            settings_updates: Settings to update

        Returns:
            Updated privacy settings
        """
        try:
            # Get current settings
            current_settings = await self.get_user_privacy_settings(user_id)

            # Apply updates
            for key, value in settings_updates.items():
                if hasattr(current_settings, key):
                    setattr(current_settings, key, value)

            current_settings.updated_at = datetime.utcnow()

            # Store updated settings
            await self._store_privacy_settings(current_settings)

            # Log settings update
            await self._log_privacy_event(user_id, "privacy_settings_updated", settings_updates)

            # Apply settings changes to AI features
            await self._apply_privacy_settings_to_ai(user_id, current_settings)

            return current_settings

        except Exception as e:
            logger.error(f"Error updating privacy settings: {str(e)}")
            raise

    async def export_user_data(
        self,
        user_id: str,
        data_categories: Optional[List[DataCategory]] = None,
        format_type: str = "json"
    ) -> Dict[str, Any]:
        """
        Export user's personal data (GDPR Article 20)

        Args:
            user_id: User identifier
            data_categories: Specific data categories to export
            format_type: Export format (json, csv, xml)

        Returns:
            Exported user data
        """
        try:
            export_data = {
                'user_id': user_id,
                'export_date': datetime.utcnow().isoformat(),
                'format': format_type,
                'data': {}
            }

            # Export behavioral data
            if not data_categories or DataCategory.BEHAVIORAL_DATA in data_categories:
                export_data['data']['behavioral_data'] = await self._export_behavioral_data(user_id)

            # Export search history
            if not data_categories or DataCategory.SEARCH_HISTORY in data_categories:
                export_data['data']['search_history'] = await self._export_search_history(user_id)

            # Export interactions
            if not data_categories or DataCategory.INTERACTION_PATTERNS in data_categories:
                export_data['data']['interaction_patterns'] = await self._export_interaction_patterns(user_id)

            # Export preferences
            if not data_categories or DataCategory.PREFERENCES in data_categories:
                export_data['data']['preferences'] = await self._export_preferences(user_id)

            # Export consent records
            export_data['data']['consent_records'] = await self._export_consent_records(user_id)

            # Log data export
            await self._log_privacy_event(user_id, "data_exported", {
                'categories': [cat.value for cat in data_categories] if data_categories else 'all',
                'format': format_type
            })

            return export_data

        except Exception as e:
            logger.error(f"Error exporting user data: {str(e)}")
            raise

    async def delete_user_data(
        self,
        user_id: str,
        data_categories: Optional[List[DataCategory]] = None,
        anonymize_instead: bool = False
    ) -> bool:
        """
        Delete or anonymize user's personal data (GDPR Article 17)

        Args:
            user_id: User identifier
            data_categories: Specific data categories to delete
            anonymize_instead: Anonymize data instead of deleting

        Returns:
            Success status
        """
        try:
            deletion_log = {
                'user_id': user_id,
                'deletion_date': datetime.utcnow().isoformat(),
                'anonymize_instead': anonymize_instead,
                'categories': [cat.value for cat in data_categories] if data_categories else 'all'
            }

            # Delete/anonymize behavioral data
            if not data_categories or DataCategory.BEHAVIORAL_DATA in data_categories:
                if anonymize_instead:
                    await self._anonymize_behavioral_data(user_id)
                else:
                    await self._delete_behavioral_data(user_id)

            # Delete/anonymize search history
            if not data_categories or DataCategory.SEARCH_HISTORY in data_categories:
                if anonymize_instead:
                    await self._anonymize_search_history(user_id)
                else:
                    await self._delete_search_history(user_id)

            # Delete/anonymize interactions
            if not data_categories or DataCategory.INTERACTION_PATTERNS in data_categories:
                if anonymize_instead:
                    await self._anonymize_interaction_patterns(user_id)
                else:
                    await self._delete_interaction_patterns(user_id)

            # Delete/anonymize preferences
            if not data_categories or DataCategory.PREFERENCES in data_categories:
                if anonymize_instead:
                    await self._anonymize_preferences(user_id)
                else:
                    await self._delete_preferences(user_id)

            # Log deletion/anonymization
            await self._log_privacy_event(user_id, "data_deleted" if not anonymize_instead else "data_anonymized", deletion_log)

            logger.info(f"User data {'anonymized' if anonymize_instead else 'deleted'} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting user data: {str(e)}")
            return False

    async def audit_data_processing(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[DataProcessingLog]:
        """
        Audit data processing activities

        Args:
            user_id: Optional user to audit
            start_date: Start date for audit period
            end_date: End date for audit period

        Returns:
            List of data processing logs
        """
        try:
            query = self.supabase.table('data_processing_logs').select('*')

            if user_id:
                query = query.eq('user_id', user_id)

            if start_date:
                query = query.gte('timestamp', start_date.isoformat())

            if end_date:
                query = query.lte('timestamp', end_date.isoformat())

            result = query.order('timestamp', desc=True).execute()

            processing_logs = []
            for log_data in result.data:
                processing_logs.append(DataProcessingLog(**log_data))

            return processing_logs

        except Exception as e:
            logger.error(f"Error auditing data processing: {str(e)}")
            return []

    async def log_data_processing(
        self,
        user_id: str,
        processing_purpose: ProcessingPurpose,
        data_categories: List[DataCategory],
        processing_details: Dict[str, Any],
        legal_basis: str,
        consent_reference: Optional[str] = None,
        retention_period: Optional[int] = None,
        processor_id: str = "planning_explorer_ai",
        processing_location: str = "EU",
        automated: bool = True
    ) -> str:
        """
        Log data processing activity for audit trail

        Args:
            user_id: User identifier
            processing_purpose: Purpose of processing
            data_categories: Categories of data being processed
            processing_details: Details about the processing
            legal_basis: Legal basis for processing
            consent_reference: Reference to consent record
            retention_period: Data retention period in days
            processor_id: Identifier of the processor
            processing_location: Location where processing occurs
            automated: Whether processing is automated

        Returns:
            Processing log ID
        """
        try:
            log_id = str(uuid.uuid4())

            processing_log = DataProcessingLog(
                log_id=log_id,
                user_id=user_id,
                processing_purpose=processing_purpose,
                data_categories=data_categories,
                processing_details=processing_details,
                legal_basis=legal_basis,
                consent_reference=consent_reference,
                retention_period=retention_period or self.default_retention_period_days,
                processor_id=processor_id,
                processing_location=processing_location,
                automated=automated,
                timestamp=datetime.utcnow()
            )

            # Store processing log
            await self._store_processing_log(processing_log)

            return log_id

        except Exception as e:
            logger.error(f"Error logging data processing: {str(e)}")
            raise

    # Private helper methods

    async def _store_consent_record(self, consent_record: ConsentRecord):
        """Store consent record in database"""
        try:
            consent_dict = asdict(consent_record)

            # Convert datetime objects to ISO strings
            for field in ['granted_at', 'withdrawn_at', 'expires_at', 'created_at', 'updated_at']:
                if consent_dict[field]:
                    consent_dict[field] = consent_dict[field].isoformat()

            # Convert enums to strings
            consent_dict['consent_type'] = consent_record.consent_type.value
            consent_dict['status'] = consent_record.status.value
            consent_dict['data_categories'] = [cat.value for cat in consent_record.data_categories]

            self.supabase.table('user_consent_records')\
                .upsert(consent_dict, on_conflict='consent_id')\
                .execute()

        except Exception as e:
            logger.error(f"Error storing consent record: {str(e)}")
            raise

    async def _get_consent_record(self, consent_id: str) -> Optional[ConsentRecord]:
        """Get consent record by ID"""
        try:
            result = self.supabase.table('user_consent_records')\
                .select('*')\
                .eq('consent_id', consent_id)\
                .execute()

            if result.data:
                record_data = result.data[0]

                # Convert back to ConsentRecord object
                record_data['consent_type'] = ConsentType(record_data['consent_type'])
                record_data['status'] = ConsentStatus(record_data['status'])
                record_data['data_categories'] = [DataCategory(cat) for cat in record_data['data_categories']]

                # Convert datetime strings back to datetime objects
                for field in ['granted_at', 'withdrawn_at', 'expires_at', 'created_at', 'updated_at']:
                    if record_data[field]:
                        record_data[field] = datetime.fromisoformat(record_data[field].replace('Z', '+00:00'))

                return ConsentRecord(**record_data)

            return None

        except Exception as e:
            logger.error(f"Error getting consent record: {str(e)}")
            return None

    async def _get_user_consents(
        self, user_id: str, consent_type: ConsentType, status: ConsentStatus
    ) -> List[ConsentRecord]:
        """Get user consent records by type and status"""
        try:
            result = self.supabase.table('user_consent_records')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('consent_type', consent_type.value)\
                .eq('status', status.value)\
                .execute()

            consent_records = []
            for record_data in result.data:
                # Convert back to ConsentRecord object
                record_data['consent_type'] = ConsentType(record_data['consent_type'])
                record_data['status'] = ConsentStatus(record_data['status'])
                record_data['data_categories'] = [DataCategory(cat) for cat in record_data['data_categories']]

                # Convert datetime strings
                for field in ['granted_at', 'withdrawn_at', 'expires_at', 'created_at', 'updated_at']:
                    if record_data[field]:
                        record_data[field] = datetime.fromisoformat(record_data[field].replace('Z', '+00:00'))

                consent_records.append(ConsentRecord(**record_data))

            return consent_records

        except Exception as e:
            logger.error(f"Error getting user consents: {str(e)}")
            return []

    async def _create_default_privacy_settings(self, user_id: str) -> PrivacySettings:
        """Create default privacy settings for new user"""
        settings = PrivacySettings(
            user_id=user_id,
            personalization_enabled=False,  # Opt-in by default
            behavioral_tracking_enabled=False,
            ai_learning_enabled=False,
            analytics_enabled=True,  # Essential analytics
            data_retention_period_days=self.default_retention_period_days,
            anonymization_level='partial',
            export_format_preference='json',
            notification_preferences={
                'privacy_updates': True,
                'data_processing': True,
                'consent_expiry': True
            },
            third_party_sharing_allowed=False,
            profile_visibility='private',
            data_portability_enabled=True,
            automated_decision_making_consent=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        await self._store_privacy_settings(settings)
        return settings

    async def _store_privacy_settings(self, settings: PrivacySettings):
        """Store privacy settings in database"""
        try:
            settings_dict = asdict(settings)
            settings_dict['created_at'] = settings.created_at.isoformat()
            settings_dict['updated_at'] = settings.updated_at.isoformat()

            self.supabase.table('user_privacy_settings')\
                .upsert(settings_dict, on_conflict='user_id')\
                .execute()

        except Exception as e:
            logger.error(f"Error storing privacy settings: {str(e)}")
            raise

    async def _log_privacy_event(self, user_id: str, event_type: str, event_data: Dict[str, Any]):
        """Log privacy-related events"""
        try:
            event_record = {
                'event_id': str(uuid.uuid4()),
                'user_id': user_id,
                'event_type': event_type,
                'event_data': event_data,
                'timestamp': datetime.utcnow().isoformat()
            }

            self.supabase.table('privacy_events').insert(event_record).execute()

        except Exception as e:
            logger.error(f"Error logging privacy event: {str(e)}")

    async def _store_processing_log(self, processing_log: DataProcessingLog):
        """Store data processing log"""
        try:
            log_dict = asdict(processing_log)
            log_dict['processing_purpose'] = processing_log.processing_purpose.value
            log_dict['data_categories'] = [cat.value for cat in processing_log.data_categories]
            log_dict['timestamp'] = processing_log.timestamp.isoformat()

            self.supabase.table('data_processing_logs').insert(log_dict).execute()

        except Exception as e:
            logger.error(f"Error storing processing log: {str(e)}")
            raise

    # Data export helper methods
    async def _export_behavioral_data(self, user_id: str) -> Dict[str, Any]:
        """Export user behavioral data"""
        try:
            result = self.supabase.table('user_behavior_profiles')\
                .select('*')\
                .eq('user_id', user_id)\
                .execute()

            return result.data[0] if result.data else {}

        except Exception as e:
            logger.error(f"Error exporting behavioral data: {str(e)}")
            return {}

    async def _export_search_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Export user search history"""
        try:
            result = self.supabase.table('user_interactions')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('interaction_type', 'search')\
                .order('timestamp', desc=True)\
                .execute()

            return result.data

        except Exception as e:
            logger.error(f"Error exporting search history: {str(e)}")
            return []

    async def _export_interaction_patterns(self, user_id: str) -> List[Dict[str, Any]]:
        """Export user interaction patterns"""
        try:
            result = self.supabase.table('user_interactions')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('timestamp', desc=True)\
                .execute()

            return result.data

        except Exception as e:
            logger.error(f"Error exporting interaction patterns: {str(e)}")
            return []

    async def _export_preferences(self, user_id: str) -> Dict[str, Any]:
        """Export user preferences"""
        try:
            result = self.supabase.table('user_preferences')\
                .select('*')\
                .eq('user_id', user_id)\
                .execute()

            return result.data[0] if result.data else {}

        except Exception as e:
            logger.error(f"Error exporting preferences: {str(e)}")
            return {}

    async def _export_consent_records(self, user_id: str) -> List[Dict[str, Any]]:
        """Export user consent records"""
        try:
            result = self.supabase.table('user_consent_records')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .execute()

            return result.data

        except Exception as e:
            logger.error(f"Error exporting consent records: {str(e)}")
            return []

    # Data deletion/anonymization helper methods
    async def _delete_behavioral_data(self, user_id: str):
        """Delete user behavioral data"""
        try:
            self.supabase.table('user_behavior_profiles')\
                .delete()\
                .eq('user_id', user_id)\
                .execute()

        except Exception as e:
            logger.error(f"Error deleting behavioral data: {str(e)}")
            raise

    async def _anonymize_behavioral_data(self, user_id: str):
        """Anonymize user behavioral data"""
        try:
            # Generate anonymous ID
            anonymous_id = hashlib.sha256(f"{user_id}_{datetime.utcnow()}".encode()).hexdigest()[:16]

            self.supabase.table('user_behavior_profiles')\
                .update({'user_id': f"anon_{anonymous_id}"})\
                .eq('user_id', user_id)\
                .execute()

        except Exception as e:
            logger.error(f"Error anonymizing behavioral data: {str(e)}")
            raise

    # Additional deletion/anonymization methods would follow similar patterns...

    async def _update_privacy_settings_from_consent(self, user_id: str, consent_record: ConsentRecord):
        """Update privacy settings based on granted consent"""
        try:
            settings = await self.get_user_privacy_settings(user_id)

            if consent_record.consent_type == ConsentType.PERSONALIZATION:
                settings.personalization_enabled = True
            elif consent_record.consent_type == ConsentType.BEHAVIORAL_TRACKING:
                settings.behavioral_tracking_enabled = True
            elif consent_record.consent_type == ConsentType.AI_LEARNING:
                settings.ai_learning_enabled = True

            await self._store_privacy_settings(settings)

        except Exception as e:
            logger.error(f"Error updating privacy settings from consent: {str(e)}")

    async def _enable_ai_features(self, user_id: str, consent_record: ConsentRecord):
        """Enable AI features based on granted consent"""
        try:
            # This would enable specific AI features based on consent type
            # Implementation would depend on how AI features are configured
            pass

        except Exception as e:
            logger.error(f"Error enabling AI features: {str(e)}")

    async def _disable_features_for_withdrawn_consent(self, user_id: str, consent_type: ConsentType):
        """Disable features when consent is withdrawn"""
        try:
            settings = await self.get_user_privacy_settings(user_id)

            if consent_type == ConsentType.PERSONALIZATION:
                settings.personalization_enabled = False
            elif consent_type == ConsentType.BEHAVIORAL_TRACKING:
                settings.behavioral_tracking_enabled = False
            elif consent_type == ConsentType.AI_LEARNING:
                settings.ai_learning_enabled = False

            await self._store_privacy_settings(settings)

        except Exception as e:
            logger.error(f"Error disabling features for withdrawn consent: {str(e)}")

    async def _stop_data_processing(self, user_id: str, consent_type: ConsentType):
        """Stop data processing activities for withdrawn consent"""
        try:
            # This would stop specific data processing based on consent type
            # Implementation would depend on how processing is managed
            pass

        except Exception as e:
            logger.error(f"Error stopping data processing: {str(e)}")

    async def _handle_data_after_consent_withdrawal(self, user_id: str, consent_type: ConsentType):
        """Handle data after consent withdrawal (delete or anonymize)"""
        try:
            settings = await self.get_user_privacy_settings(user_id)

            if settings.anonymization_level == 'full':
                # Anonymize data
                if consent_type == ConsentType.BEHAVIORAL_TRACKING:
                    await self._anonymize_behavioral_data(user_id)
            elif settings.anonymization_level == 'none':
                # Delete data
                if consent_type == ConsentType.BEHAVIORAL_TRACKING:
                    await self._delete_behavioral_data(user_id)

        except Exception as e:
            logger.error(f"Error handling data after consent withdrawal: {str(e)}")

    async def _apply_privacy_settings_to_ai(self, user_id: str, settings: PrivacySettings):
        """Apply privacy settings to AI features"""
        try:
            # This would configure AI features based on privacy settings
            # Implementation would depend on AI feature architecture
            pass

        except Exception as e:
            logger.error(f"Error applying privacy settings to AI: {str(e)}")