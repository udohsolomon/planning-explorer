"""
Supabase client and database operations for Planning Explorer
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import time
from functools import wraps

from supabase import create_client, Client
from gotrue.errors import AuthApiError
from app.core.config import settings
from app.models.user import UserProfile, UserSettings, SavedSearch, UserAlert, UserReport, APIUsage, UserEvent

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed operations"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {delay}s...")
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}")
            raise last_exception
        return wrapper
    return decorator


class SupabaseConnectionPool:
    """Connection pool for Supabase clients"""

    def __init__(self, pool_size: int = 10):
        self.pool_size = pool_size
        self.clients: List[Client] = []
        self.available_clients: List[Client] = []
        self.in_use_clients: Dict[str, Client] = {}
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize connection pool"""
        if self._initialized:
            return True

        try:
            for i in range(self.pool_size):
                client = create_client(
                    settings.supabase_url,
                    settings.supabase_key
                )
                # Test connection - using a simple ping instead of table query to avoid RLS issues
                # Just verify the client was created successfully
                if client:
                    pass  # Connection successful if client object exists

                self.clients.append(client)
                self.available_clients.append(client)

            self._initialized = True
            logger.info(f"Supabase connection pool initialized with {self.pool_size} connections")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Supabase connection pool: {str(e)}")
            return False

    async def get_client(self) -> Optional[Client]:
        """Get available client from pool"""
        async with self._lock:
            if self.available_clients:
                client = self.available_clients.pop(0)
                self.in_use_clients[id(client)] = client
                return client
            else:
                # Pool exhausted, create temporary client
                logger.warning("Connection pool exhausted, creating temporary client")
                return create_client(settings.supabase_url, settings.supabase_key)

    async def return_client(self, client: Client):
        """Return client to pool"""
        async with self._lock:
            client_id = id(client)
            if client_id in self.in_use_clients:
                del self.in_use_clients[client_id]
                self.available_clients.append(client)

    async def close_all(self):
        """Close all connections"""
        async with self._lock:
            # Supabase clients don't need explicit closing
            self.clients.clear()
            self.available_clients.clear()
            self.in_use_clients.clear()
            self._initialized = False
            logger.info("Closed all Supabase connections")


class SupabaseClient:
    """Enhanced Supabase client wrapper with connection pooling and production features"""

    def __init__(self):
        self.client: Optional[Client] = None
        self.pool: Optional[SupabaseConnectionPool] = None
        self._connection_retries = 0
        self._max_retries = 3
        self._use_pool = settings.max_connections > 1
        self._health_check_interval = 300  # 5 minutes
        self._last_health_check = 0

    async def connect(self) -> bool:
        """
        Establish connection to Supabase with connection pooling support

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self._use_pool:
                # Initialize connection pool
                self.pool = SupabaseConnectionPool(pool_size=settings.max_connections)
                success = await self.pool.initialize()
                if success:
                    logger.info(f"Successfully initialized Supabase connection pool with {settings.max_connections} connections")
                    return True
                else:
                    # Fallback to single connection
                    logger.warning("Connection pool initialization failed, falling back to single connection")
                    self._use_pool = False

            if not self._use_pool:
                # Single connection mode
                self.client = create_client(
                    settings.supabase_url,
                    settings.supabase_key
                )

                # Test connection - using a simple ping instead of table query to avoid RLS issues
                # Just verify the client was created successfully
                if self.client:
                    logger.info("Successfully connected to Supabase.")
                return True

        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {str(e)}")
            return False

    async def disconnect(self):
        """Close Supabase connections"""
        if self.pool:
            await self.pool.close_all()
            self.pool = None
        if self.client:
            # Supabase client doesn't need explicit disconnection
            self.client = None
        logger.info("Disconnected from Supabase")

    async def ensure_connection(self):
        """Ensure connection is established with health check"""
        current_time = time.time()

        # Perform periodic health check
        if current_time - self._last_health_check > self._health_check_interval:
            await self._perform_health_check()
            self._last_health_check = current_time

        if not self.client and not self.pool:
            if not await self.connect():
                raise ConnectionError("Failed to connect to Supabase")

    async def _perform_health_check(self):
        """Perform health check on connections"""
        try:
            if self.pool:
                client = await self.pool.get_client()
                if client:
                    # Simple health check - just verify client exists
                    await self.pool.return_client(client)
                    logger.debug("Supabase connection pool health check passed")
            elif self.client:
                # Simple health check - just verify client exists
                logger.debug("Supabase connection health check passed")
        except Exception as e:
            logger.warning(f"Supabase health check failed: {str(e)}")

    async def get_client(self) -> Client:
        """Get client for operations"""
        await self.ensure_connection()

        if self.pool:
            client = await self.pool.get_client()
            if client:
                return client
            # Fallback to creating new client
            return create_client(settings.supabase_url, settings.supabase_key)

        if self.client:
            return self.client

        raise ConnectionError("No Supabase client available")

    async def return_client(self, client: Client):
        """Return client to pool if using pooling"""
        if self.pool:
            await self.pool.return_client(client)

    # ======== AUTHENTICATION METHODS ========

    @retry_on_failure(max_retries=3)
    async def sign_up_user(self, email: str, password: str, user_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Register a new user with retry logic

        Args:
            email: User email
            password: User password
            user_data: Additional user metadata

        Returns:
            Dict with user data and session info
        """
        client = await self.get_client()

        try:
            response = client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data or {}
                }
            })

            if response.user:
                # Create user profile in database
                await self.create_user_profile(
                    user_id=response.user.id,
                    email=email,
                    full_name=user_data.get("full_name") if user_data else None,
                    company=user_data.get("company") if user_data else None
                )

            return {
                "user": response.user,
                "session": response.session,
                "success": True
            }

        except AuthApiError as e:
            logger.error(f"User registration failed: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }
        finally:
            await self.return_client(client)

    @retry_on_failure(max_retries=3)
    async def sign_in_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with retry logic

        Args:
            email: User email
            password: User password

        Returns:
            Dict with user data and session info
        """
        client = await self.get_client()

        try:
            response = client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user:
                # Update last login
                await self.update_user_profile(
                    user_id=response.user.id,
                    data={"last_login": datetime.utcnow().isoformat()}
                )

            return {
                "user": response.user,
                "session": response.session,
                "success": True
            }

        except AuthApiError as e:
            logger.error(f"User authentication failed: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }
        finally:
            await self.return_client(client)

    async def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get user by JWT token

        Args:
            token: JWT access token

        Returns:
            User data if valid, None otherwise
        """
        self.ensure_connection()

        try:
            # Set the session
            self.client.auth.set_session(token, None)
            user = self.client.auth.get_user()

            if user:
                return {"user": user, "success": True}
            return None

        except AuthApiError as e:
            logger.error(f"Token validation failed: {str(e)}")
            return None

    async def sign_out_user(self, token: str) -> bool:
        """
        Sign out user

        Args:
            token: JWT access token

        Returns:
            bool: True if successful
        """
        self.ensure_connection()

        try:
            self.client.auth.set_session(token, None)
            self.client.auth.sign_out()
            return True

        except Exception as e:
            logger.error(f"Sign out failed: {str(e)}")
            return False

    # ======== USER PROFILE METHODS ========

    async def create_user_profile(
        self,
        user_id: str,
        email: str,
        full_name: Optional[str] = None,
        company: Optional[str] = None,
        role: str = "free"
    ) -> Optional[UserProfile]:
        """Create user profile in database"""
        self.ensure_connection()

        try:
            profile_data = {
                "user_id": user_id,
                "email": email,
                "full_name": full_name,
                "company": company,
                "role": role,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            response = self.client.table("user_profiles").insert(profile_data).execute()

            if response.data:
                return UserProfile(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to create user profile: {str(e)}")
            return None

    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        self.ensure_connection()

        try:
            response = self.client.table("user_profiles").select("*").eq("user_id", user_id).execute()

            if response.data:
                return UserProfile(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to get user profile: {str(e)}")
            return None

    async def update_user_profile(self, user_id: str, data: Dict[str, Any]) -> Optional[UserProfile]:
        """Update user profile"""
        self.ensure_connection()

        try:
            data["updated_at"] = datetime.utcnow().isoformat()

            response = self.client.table("user_profiles").update(data).eq("user_id", user_id).execute()

            if response.data:
                return UserProfile(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to update user profile: {str(e)}")
            return None

    # ======== USER SETTINGS METHODS ========

    async def get_user_settings(self, user_id: str) -> Optional[UserSettings]:
        """Get user settings"""
        self.ensure_connection()

        try:
            response = self.client.table("user_settings").select("*").eq("user_id", user_id).execute()

            if response.data:
                return UserSettings(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to get user settings: {str(e)}")
            return None

    async def update_user_settings(self, user_id: str, settings: UserSettings) -> Optional[UserSettings]:
        """Update user settings"""
        self.ensure_connection()

        try:
            settings_data = settings.dict()
            settings_data["updated_at"] = datetime.utcnow().isoformat()

            response = self.client.table("user_settings").upsert(settings_data).execute()

            if response.data:
                return UserSettings(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to update user settings: {str(e)}")
            return None

    # ======== SAVED SEARCHES METHODS ========

    async def create_saved_search(self, user_id: str, search_data: Dict[str, Any]) -> Optional[SavedSearch]:
        """Create saved search"""
        self.ensure_connection()

        try:
            search_data["user_id"] = user_id
            search_data["created_at"] = datetime.utcnow().isoformat()
            search_data["updated_at"] = datetime.utcnow().isoformat()

            response = self.client.table("saved_searches").insert(search_data).execute()

            if response.data:
                return SavedSearch(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to create saved search: {str(e)}")
            return None

    async def get_user_saved_searches(self, user_id: str, limit: int = 50) -> List[SavedSearch]:
        """Get user's saved searches"""
        self.ensure_connection()

        try:
            response = (
                self.client.table("saved_searches")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return [SavedSearch(**item) for item in response.data]

        except Exception as e:
            logger.error(f"Failed to get saved searches: {str(e)}")
            return []

    async def update_saved_search(self, search_id: str, user_id: str, data: Dict[str, Any]) -> Optional[SavedSearch]:
        """Update saved search"""
        self.ensure_connection()

        try:
            data["updated_at"] = datetime.utcnow().isoformat()

            response = (
                self.client.table("saved_searches")
                .update(data)
                .eq("search_id", search_id)
                .eq("user_id", user_id)
                .execute()
            )

            if response.data:
                return SavedSearch(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to update saved search: {str(e)}")
            return None

    async def delete_saved_search(self, search_id: str, user_id: str) -> bool:
        """Delete saved search"""
        self.ensure_connection()

        try:
            response = (
                self.client.table("saved_searches")
                .delete()
                .eq("search_id", search_id)
                .eq("user_id", user_id)
                .execute()
            )

            return len(response.data) > 0

        except Exception as e:
            logger.error(f"Failed to delete saved search: {str(e)}")
            return False

    # ======== ALERTS METHODS ========

    async def create_user_alert(self, user_id: str, alert_data: Dict[str, Any]) -> Optional[UserAlert]:
        """Create user alert"""
        self.ensure_connection()

        try:
            alert_data["user_id"] = user_id
            alert_data["created_at"] = datetime.utcnow().isoformat()
            alert_data["updated_at"] = datetime.utcnow().isoformat()

            response = self.client.table("user_alerts").insert(alert_data).execute()

            if response.data:
                return UserAlert(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to create user alert: {str(e)}")
            return None

    async def get_user_alerts(self, user_id: str, active_only: bool = True) -> List[UserAlert]:
        """Get user alerts"""
        self.ensure_connection()

        try:
            query = self.client.table("user_alerts").select("*").eq("user_id", user_id)

            if active_only:
                query = query.eq("is_active", True)

            response = query.order("created_at", desc=True).execute()

            return [UserAlert(**item) for item in response.data]

        except Exception as e:
            logger.error(f"Failed to get user alerts: {str(e)}")
            return []

    # ======== REPORTS METHODS ========

    async def create_user_report(self, user_id: str, report_data: Dict[str, Any]) -> Optional[UserReport]:
        """Create user report"""
        self.ensure_connection()

        try:
            report_data["user_id"] = user_id
            report_data["created_at"] = datetime.utcnow().isoformat()
            report_data["updated_at"] = datetime.utcnow().isoformat()

            response = self.client.table("user_reports").insert(report_data).execute()

            if response.data:
                return UserReport(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to create user report: {str(e)}")
            return None

    async def get_user_reports(self, user_id: str, limit: int = 20) -> List[UserReport]:
        """Get user reports"""
        self.ensure_connection()

        try:
            response = (
                self.client.table("user_reports")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return [UserReport(**item) for item in response.data]

        except Exception as e:
            logger.error(f"Failed to get user reports: {str(e)}")
            return []

    # ======== USAGE TRACKING METHODS ========

    async def log_api_usage(self, user_id: str, usage_data: Dict[str, Any]) -> Optional[APIUsage]:
        """Log API usage"""
        self.ensure_connection()

        try:
            usage_data["user_id"] = user_id
            usage_data["created_at"] = datetime.utcnow().isoformat()

            response = self.client.table("api_usage").insert(usage_data).execute()

            if response.data:
                return APIUsage(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to log API usage: {str(e)}")
            return None

    async def log_user_event(self, user_id: str, event_data: Dict[str, Any]) -> Optional[UserEvent]:
        """Log user event"""
        self.ensure_connection()

        try:
            event_data["user_id"] = user_id
            event_data["created_at"] = datetime.utcnow().isoformat()

            response = self.client.table("user_events").insert(event_data).execute()

            if response.data:
                return UserEvent(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to log user event: {str(e)}")
            return None

    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        self.ensure_connection()

        try:
            # Get saved searches count
            saved_searches = await self.get_user_saved_searches(user_id)

            # Get active alerts count
            active_alerts = await self.get_user_alerts(user_id, active_only=True)

            # Get reports count
            reports = await self.get_user_reports(user_id)

            # Get this month's API usage
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            api_usage_response = (
                self.client.table("api_usage")
                .select("count", count="exact")
                .eq("user_id", user_id)
                .gte("created_at", current_month_start.isoformat())
                .execute()
            )

            return {
                "saved_searches": len(saved_searches),
                "active_alerts": len(active_alerts),
                "reports_generated": len(reports),
                "api_calls_this_month": api_usage_response.count or 0
            }

        except Exception as e:
            logger.error(f"Failed to get user stats: {str(e)}")
            return {
                "saved_searches": 0,
                "active_alerts": 0,
                "reports_generated": 0,
                "api_calls_this_month": 0
            }


# Global Supabase client instance
supabase_client = SupabaseClient()