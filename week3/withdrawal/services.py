"""HTTP service integration for three customer apps."""

import json
from typing import Dict, List, Optional, Any


class HttpService:
    """HTTP client for service integration."""

    def __init__(self, base_url: str, service_name: str, token: str = ""):
        """Initialize service client.

        Args:
            base_url: Service base URL
            service_name: Service name (documents, search, personalization)
            token: Optional authentication token
        """
        self.base_url = base_url.rstrip("/")
        self.service_name = service_name
        self.token = token

    def health(self) -> bool:
        """Check service health.

        Returns:
            True if service is healthy
        """
        try:
            import requests
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def catalog(self, user_id: str) -> List[Dict[str, Any]]:
        """List records for user.

        Args:
            user_id: User ID

        Returns:
            List of record metadata
        """
        try:
            import requests
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"

            response = requests.get(
                f"{self.base_url}/catalog",
                params={"user_id": user_id},
                headers=headers,
                timeout=5,
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return []

    def get_record(self, user_id: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Get specific record.

        Args:
            user_id: User ID
            record_id: Record ID

        Returns:
            Record data or None
        """
        try:
            import requests
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"

            response = requests.get(
                f"{self.base_url}/record/{record_id}",
                params={"user_id": user_id},
                headers=headers,
                timeout=5,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def delete_record(self, user_id: str, record_id: str) -> bool:
        """Delete a record.

        Args:
            user_id: User ID
            record_id: Record ID

        Returns:
            True if successful
        """
        try:
            import requests
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"

            response = requests.delete(
                f"{self.base_url}/record/{record_id}",
                params={"user_id": user_id},
                headers=headers,
                timeout=5,
            )
            return response.status_code in [200, 204]
        except Exception:
            return False


class HttpServices:
    """Manager for all connected services."""

    # Service ports for local development
    PORTS = {
        "documents": 8101,
        "search": 8102,
        "personalization": 8103,
    }

    def __init__(self, base_url_pattern: str = "http://127.0.0.1:{port}", token: str = ""):
        """Initialize service manager.

        Args:
            base_url_pattern: URL pattern with {port} placeholder
            token: Optional auth token for all services
        """
        self.services: Dict[str, HttpService] = {}
        self.token = token

        for service_name, port in self.PORTS.items():
            base_url = base_url_pattern.format(port=port)
            self.services[service_name] = HttpService(base_url, service_name, token)

    def health_check(self) -> Dict[str, bool]:
        """Check health of all services.

        Returns:
            Dict of service name -> healthy status
        """
        return {
            name: service.health()
            for name, service in self.services.items()
        }

    def get_service(self, service_name: str) -> Optional[HttpService]:
        """Get service by name.

        Args:
            service_name: Service name

        Returns:
            HttpService or None
        """
        return self.services.get(service_name)

    def catalog_all(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get catalog from all services.

        Args:
            user_id: User ID

        Returns:
            Dict of service_name -> records
        """
        result = {}
        for service_name, service in self.services.items():
            result[service_name] = service.catalog(user_id)
        return result

    def delete_record(self, service_name: str, user_id: str, record_id: str) -> bool:
        """Delete record from specific service.

        Args:
            service_name: Service name
            user_id: User ID
            record_id: Record ID

        Returns:
            True if successful
        """
        service = self.get_service(service_name)
        if not service:
            return False
        return service.delete_record(user_id, record_id)


# Singleton instance
_services: Optional[HttpServices] = None


def init_services(base_url_pattern: str = "http://127.0.0.1:{port}") -> HttpServices:
    """Initialize services singleton.

    Args:
        base_url_pattern: URL pattern with {port} placeholder

    Returns:
        HttpServices instance
    """
    global _services
    _services = HttpServices(base_url_pattern)
    return _services


def get_services() -> Optional[HttpServices]:
    """Get services singleton.

    Returns:
        HttpServices instance or None
    """
    return _services


def configured_services() -> Optional[HttpServices]:
    """Get or initialize configured services.

    Returns:
        HttpServices instance or None if services not initialized
    """
    return get_services()
