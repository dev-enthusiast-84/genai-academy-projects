"""Optional notification system for withdrawal events."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum


class NotificationEvent(Enum):
    """Withdrawal events that trigger notifications."""
    AWAITING_APPROVAL = "awaiting_approval"
    REVIEW_BLOCKED = "review_blocked"
    APPROVED = "approved"
    EXECUTING = "executing"
    PARTIAL = "partial"
    COMPLETE = "complete"


class NotificationProvider:
    """Base class for notification providers."""

    def send(self, event: NotificationEvent, message: str, context: Dict[str, Any]) -> bool:
        """Send a notification.

        Args:
            event: Event type
            message: Notification message
            context: Additional context (user_id, request_id, etc.)

        Returns:
            True if successful
        """
        raise NotImplementedError


class EmailNotificationProvider(NotificationProvider):
    """Email notification provider."""

    def __init__(self):
        """Initialize email provider."""
        self.enabled = os.getenv("NOTIFICATION_ENABLED", "false").lower() == "true"
        self.smtp_host = os.getenv("NOTIFICATION_SMTP_HOST", "")
        self.smtp_port = int(os.getenv("NOTIFICATION_SMTP_PORT", "587"))
        self.smtp_username = os.getenv("NOTIFICATION_SMTP_USERNAME", "")
        self.smtp_password = os.getenv("NOTIFICATION_SMTP_PASSWORD", "")
        self.from_email = os.getenv("NOTIFICATION_FROM_EMAIL", "")
        self.to_email = os.getenv("NOTIFICATION_TO_EMAIL", "")

    def send(self, event: NotificationEvent, message: str, context: Dict[str, Any]) -> bool:
        """Send email notification.

        Args:
            event: Event type
            message: Email message
            context: Context data

        Returns:
            True if successful
        """
        if not self.enabled or not all([
            self.smtp_host,
            self.smtp_username,
            self.smtp_password,
            self.from_email,
            self.to_email,
        ]):
            return False

        try:
            import smtplib
            from email.mime.text import MIMEText

            msg = MIMEText(message)
            msg["Subject"] = f"Recall: {event.value}"
            msg["From"] = self.from_email
            msg["To"] = self.to_email

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Email notification failed: {e}")
            return False


class SlackNotificationProvider(NotificationProvider):
    """Slack notification provider."""

    def __init__(self):
        """Initialize Slack provider."""
        self.enabled = os.getenv("NOTIFICATION_ENABLED", "false").lower() == "true"
        self.webhook_url = os.getenv("NOTIFICATION_WEBHOOK_URL", "")

    def send(self, event: NotificationEvent, message: str, context: Dict[str, Any]) -> bool:
        """Send Slack notification.

        Args:
            event: Event type
            message: Message text
            context: Context data

        Returns:
            True if successful
        """
        if not self.enabled or not self.webhook_url:
            return False

        try:
            import requests

            payload = {
                "text": f"*Recall: {event.value}*",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{event.value}*\n{message}",
                        },
                    },
                ],
            }

            response = requests.post(self.webhook_url, json=payload, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Slack notification failed: {e}")
            return False


class NotificationManager:
    """Manages notification delivery."""

    def __init__(self):
        """Initialize notification manager."""
        self.enabled = os.getenv("NOTIFICATION_ENABLED", "false").lower() == "true"
        self.providers: Dict[str, NotificationProvider] = {}

        if self.enabled:
            provider = os.getenv("NOTIFICATION_PROVIDER", "email").lower()

            if provider == "email":
                self.providers["email"] = EmailNotificationProvider()
            elif provider == "slack":
                self.providers["slack"] = SlackNotificationProvider()

    def notify(
        self,
        event: NotificationEvent,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send notification.

        Args:
            event: Event type
            message: Message text
            context: Optional context data

        Returns:
            True if any provider succeeded
        """
        if not self.enabled or not self.providers:
            return False

        context = context or {}
        success = False

        for provider in self.providers.values():
            if provider.send(event, message, context):
                success = True

        return success


# Global instance
_manager: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    """Get global notification manager.

    Returns:
        NotificationManager instance
    """
    global _manager
    if _manager is None:
        _manager = NotificationManager()
    return _manager


def notify(
    event: NotificationEvent,
    message: str,
    context: Optional[Dict[str, Any]] = None,
) -> bool:
    """Send notification (convenience function).

    Args:
        event: Event type
        message: Message text
        context: Optional context

    Returns:
        True if sent
    """
    return get_notification_manager().notify(event, message, context)


def notification_settings(env_file: Path) -> Dict[str, Any]:
    """Load notification settings from .env file.

    Args:
        env_file: Path to .env file

    Returns:
        Settings dictionary
    """
    config = {
        'enabled': os.getenv('NOTIFICATION_ENABLED', 'false').lower() == 'true',
        'provider': os.getenv('NOTIFICATION_PROVIDER', 'email').lower(),
        'smtp_host': os.getenv('NOTIFICATION_SMTP_HOST', ''),
        'smtp_port': int(os.getenv('NOTIFICATION_SMTP_PORT', '587')),
        'smtp_username': os.getenv('NOTIFICATION_SMTP_USERNAME', ''),
        'smtp_password': os.getenv('NOTIFICATION_SMTP_PASSWORD', ''),
        'from_email': os.getenv('NOTIFICATION_FROM_EMAIL', ''),
        'to_email': os.getenv('NOTIFICATION_TO_EMAIL', ''),
        'webhook_url': os.getenv('NOTIFICATION_WEBHOOK_URL', ''),
    }
    return config


def notify_withdrawal_status(
    status: str,
    user: str,
    request_id: str,
    context: Optional[Dict[str, Any]] = None,
) -> bool:
    """Send withdrawal status notification.

    Args:
        status: Status (awaiting_approval, approved, executing, complete, etc.)
        user: User ID
        request_id: Request ID
        context: Optional context data

    Returns:
        True if notification sent
    """
    event_map = {
        'awaiting_approval': NotificationEvent.AWAITING_APPROVAL,
        'approved': NotificationEvent.APPROVED,
        'executing': NotificationEvent.EXECUTING,
        'complete': NotificationEvent.COMPLETE,
        'partial': NotificationEvent.PARTIAL,
    }

    event = event_map.get(status, NotificationEvent.COMPLETE)
    message = f"Withdrawal request {request_id} status: {status}"

    ctx = context or {}
    ctx.update({'user': user, 'request_id': request_id})

    return notify(event, message, ctx)
