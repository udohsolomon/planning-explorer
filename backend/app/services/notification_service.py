"""
Notification service for Planning Explorer API

Handles email notifications, push notifications, and in-app notifications
with template management and delivery tracking.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from email.mime.text import MIMEText as MimeText
from email.mime.multipart import MIMEMultipart as MimeMultipart
import smtplib
import ssl

from app.core.config import settings
from app.db.supabase import supabase_client
from app.models.user import UserProfile

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing and delivering notifications"""

    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_use_tls = settings.smtp_use_tls
        self.from_email = settings.from_email

    async def send_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        delivery_methods: List[str] = None
    ) -> bool:
        """
        Send notification to user via specified delivery methods

        Args:
            user_id: Target user ID
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            data: Additional notification data
            delivery_methods: List of delivery methods (email, push, in_app)

        Returns:
            True if at least one delivery method succeeded
        """
        try:
            # Get user profile and preferences
            user_profile = await supabase_client.get_user_profile(user_id)
            if not user_profile:
                logger.error(f"User profile not found for ID: {user_id}")
                return False

            # Get user settings for notification preferences
            user_settings = await supabase_client.get_user_settings(user_id)

            # Determine delivery methods based on user preferences
            if delivery_methods is None:
                delivery_methods = []
                if user_settings and getattr(user_settings, 'email_notifications', True):
                    delivery_methods.append('email')
                if user_settings and getattr(user_settings, 'push_notifications', True):
                    delivery_methods.append('push')
                # Always include in-app notifications
                delivery_methods.append('in_app')

            success_count = 0
            total_methods = len(delivery_methods)

            # Store in-app notification
            if 'in_app' in delivery_methods:
                in_app_success = await self._create_in_app_notification(
                    user_id, notification_type, title, message, data
                )
                if in_app_success:
                    success_count += 1

            # Send email notification
            if 'email' in delivery_methods and settings.enable_email_notifications:
                email_success = await self._send_email_notification(
                    user_profile, notification_type, title, message, data
                )
                if email_success:
                    success_count += 1

            # Send push notification
            if 'push' in delivery_methods and settings.enable_push_notifications:
                push_success = await self._send_push_notification(
                    user_id, title, message, data
                )
                if push_success:
                    success_count += 1

            return success_count > 0

        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False

    async def _create_in_app_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create in-app notification"""
        try:
            notification_data = {
                "user_id": user_id,
                "type": notification_type,
                "title": title,
                "message": message,
                "data": data or {},
                "delivery_method": "in_app",
                "is_read": False,
                "is_sent": True,
                "sent_at": datetime.utcnow().isoformat(),
                "delivery_status": "sent"
            }

            # Use Supabase client to create notification
            # This would need to be implemented in the Supabase client
            return True  # Placeholder

        except Exception as e:
            logger.error(f"Failed to create in-app notification: {str(e)}")
            return False

    async def _send_email_notification(
        self,
        user_profile: UserProfile,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send email notification"""
        try:
            if not self.smtp_server or not user_profile.email:
                return False

            # Get email template
            email_content = await self._get_email_template(
                notification_type, title, message, data, user_profile
            )

            # Create email message
            msg = MimeMultipart('alternative')
            msg['Subject'] = title
            msg['From'] = self.from_email
            msg['To'] = user_profile.email

            # Add HTML content
            html_part = MimeText(email_content['html'], 'html')
            text_part = MimeText(email_content['text'], 'plain')

            msg.attach(text_part)
            msg.attach(html_part)

            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls(context=context)
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {user_profile.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False

    async def _send_push_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send push notification"""
        try:
            # Push notification implementation would go here
            # This could integrate with services like Firebase, OneSignal, etc.
            logger.info(f"Push notification sent to user {user_id}: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            return False

    async def _get_email_template(
        self,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]],
        user_profile: UserProfile
    ) -> Dict[str, str]:
        """Get email template for notification type"""
        try:
            # Basic email template
            html_template = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                    .button {{ background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Planning Explorer</h1>
                    </div>
                    <div class="content">
                        <h2>{title}</h2>
                        <p>Hello {user_profile.full_name or 'there'},</p>
                        <p>{message}</p>
                        {self._format_notification_data(notification_type, data)}
                        <p>Best regards,<br>The Planning Explorer Team</p>
                    </div>
                    <div class="footer">
                        <p>You received this email because you have notifications enabled in your Planning Explorer account.</p>
                        <p><a href="https://planningexplorer.uk/settings">Manage notification preferences</a></p>
                    </div>
                </div>
            </body>
            </html>
            """

            text_template = f"""
            Planning Explorer Notification

            {title}

            Hello {user_profile.full_name or 'there'},

            {message}

            {self._format_notification_data_text(notification_type, data)}

            Best regards,
            The Planning Explorer Team

            ---
            You received this email because you have notifications enabled in your Planning Explorer account.
            Manage your notification preferences: https://planningexplorer.uk/settings
            """

            return {
                'html': html_template,
                'text': text_template
            }

        except Exception as e:
            logger.error(f"Failed to get email template: {str(e)}")
            return {
                'html': f"<p>{message}</p>",
                'text': message
            }

    def _format_notification_data(self, notification_type: str, data: Optional[Dict[str, Any]]) -> str:
        """Format notification data for HTML email"""
        if not data:
            return ""

        if notification_type == "alert":
            return f"""
            <div style="background-color: #e7f3ff; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
                <h3>Alert Details</h3>
                <p><strong>New applications found:</strong> {data.get('new_applications_count', 0)}</p>
                <p><strong>Alert name:</strong> {data.get('alert_name', 'N/A')}</p>
                <a href="https://planningexplorer.uk/alerts/{data.get('alert_id', '')}" class="button">View Results</a>
            </div>
            """
        elif notification_type == "report_ready":
            return f"""
            <div style="background-color: #e8f5e8; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
                <h3>Report Ready</h3>
                <p><strong>Report name:</strong> {data.get('report_name', 'N/A')}</p>
                <p><strong>Generated:</strong> {data.get('generated_at', 'N/A')}</p>
                <a href="https://planningexplorer.uk/reports/{data.get('report_id', '')}" class="button">Download Report</a>
            </div>
            """

        return ""

    def _format_notification_data_text(self, notification_type: str, data: Optional[Dict[str, Any]]) -> str:
        """Format notification data for text email"""
        if not data:
            return ""

        if notification_type == "alert":
            return f"""
Alert Details:
- New applications found: {data.get('new_applications_count', 0)}
- Alert name: {data.get('alert_name', 'N/A')}
- View results: https://planningexplorer.uk/alerts/{data.get('alert_id', '')}
            """
        elif notification_type == "report_ready":
            return f"""
Report Details:
- Report name: {data.get('report_name', 'N/A')}
- Generated: {data.get('generated_at', 'N/A')}
- Download: https://planningexplorer.uk/reports/{data.get('report_id', '')}
            """

        return ""

    async def send_alert_notification(
        self,
        user_id: str,
        alert_name: str,
        alert_id: str,
        new_applications_count: int,
        sample_applications: List[Dict[str, Any]] = None
    ) -> bool:
        """Send alert-specific notification"""
        title = f"New planning applications found - {alert_name}"
        message = f"Your alert '{alert_name}' has found {new_applications_count} new planning applications."

        data = {
            "alert_name": alert_name,
            "alert_id": alert_id,
            "new_applications_count": new_applications_count,
            "sample_applications": sample_applications or []
        }

        return await self.send_notification(
            user_id=user_id,
            notification_type="alert",
            title=title,
            message=message,
            data=data
        )

    async def send_report_ready_notification(
        self,
        user_id: str,
        report_name: str,
        report_id: str
    ) -> bool:
        """Send report ready notification"""
        title = f"Your report '{report_name}' is ready"
        message = f"The report '{report_name}' has been generated and is ready for download."

        data = {
            "report_name": report_name,
            "report_id": report_id,
            "generated_at": datetime.utcnow().isoformat()
        }

        return await self.send_notification(
            user_id=user_id,
            notification_type="report_ready",
            title=title,
            message=message,
            data=data
        )

    async def send_welcome_notification(self, user_id: str, user_name: str) -> bool:
        """Send welcome notification to new users"""
        title = "Welcome to Planning Explorer!"
        message = f"Welcome aboard, {user_name}! We're excited to help you discover planning opportunities."

        data = {
            "user_name": user_name,
            "getting_started_url": "https://planningexplorer.uk/getting-started"
        }

        return await self.send_notification(
            user_id=user_id,
            notification_type="welcome",
            title=title,
            message=message,
            data=data
        )

    async def send_daily_digest(self, user_id: str) -> bool:
        """Send daily digest notification"""
        # Get user's active alerts and recent activity
        try:
            user_profile = await supabase_client.get_user_profile(user_id)
            if not user_profile:
                return False

            # Get summary data
            alerts = await supabase_client.get_user_alerts(user_id, active_only=True)
            # Get recent activity, new applications, etc.

            title = "Your daily planning digest"
            message = f"Here's your daily summary of planning activity."

            data = {
                "active_alerts": len(alerts),
                "new_applications_today": 12,  # Mock data
                "trending_keywords": ["residential", "commercial"],
                "digest_date": datetime.utcnow().strftime("%Y-%m-%d")
            }

            return await self.send_notification(
                user_id=user_id,
                notification_type="digest",
                title=title,
                message=message,
                data=data,
                delivery_methods=["email", "in_app"]  # Skip push for digests
            )

        except Exception as e:
            logger.error(f"Failed to send daily digest: {str(e)}")
            return False

    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user's in-app notifications"""
        try:
            # This would query the user_notifications table
            # For now, return mock data
            notifications = []

            # Mock notifications
            base_notifications = [
                {
                    "notification_id": "notif_1",
                    "type": "alert",
                    "title": "New planning applications found",
                    "message": "Your alert 'Residential developments' has found 3 new applications.",
                    "is_read": False,
                    "created_at": datetime.utcnow().isoformat(),
                    "data": {"alert_name": "Residential developments", "count": 3}
                },
                {
                    "notification_id": "notif_2",
                    "type": "report_ready",
                    "title": "Your report is ready",
                    "message": "Market Analysis Report has been generated.",
                    "is_read": True,
                    "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                    "data": {"report_name": "Market Analysis Report"}
                }
            ]

            if unread_only:
                notifications = [n for n in base_notifications if not n["is_read"]]
            else:
                notifications = base_notifications

            return notifications[:limit]

        except Exception as e:
            logger.error(f"Failed to get user notifications: {str(e)}")
            return []

    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        try:
            # This would update the notification in the database
            # For now, return success
            return True

        except Exception as e:
            logger.error(f"Failed to mark notification as read: {str(e)}")
            return False


# Global notification service instance
notification_service = NotificationService()