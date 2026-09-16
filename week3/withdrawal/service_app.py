"""Utilities for service app integration."""

from typing import Dict, List, Any, Optional


class ServiceApp:
    """Represents a connected service app."""

    def __init__(
        self,
        name: str,
        port: int,
        description: str = "",
    ):
        """Initialize service app.

        Args:
            name: Service name (documents, search, personalization)
            port: Service port
            description: Service description
        """
        self.name = name
        self.port = port
        self.description = description

    def base_url(self, host: str = "127.0.0.1") -> str:
        """Get service base URL.

        Args:
            host: Host name

        Returns:
            Full URL
        """
        return f"http://{host}:{self.port}"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict.

        Returns:
            Dict representation
        """
        return {
            "name": self.name,
            "port": self.port,
            "description": self.description,
        }


# Built-in service apps
BUILT_IN_APPS = {
    "documents": ServiceApp(
        name="documents",
        port=8101,
        description="Club Portal - Fitness interest questionnaire",
    ),
    "search": ServiceApp(
        name="search",
        port=8102,
        description="Class Booking - Class search and booking history",
    ),
    "personalization": ServiceApp(
        name="personalization",
        port=8103,
        description="Member Offers - Personalized invitations and offers",
    ),
}


class ServiceRegistry:
    """Registry of connected service apps."""

    def __init__(self):
        """Initialize registry."""
        self.apps: Dict[str, ServiceApp] = dict(BUILT_IN_APPS)

    def register(self, app: ServiceApp) -> None:
        """Register a service app.

        Args:
            app: ServiceApp to register
        """
        self.apps[app.name] = app

    def get(self, name: str) -> Optional[ServiceApp]:
        """Get service app by name.

        Args:
            name: Service name

        Returns:
            ServiceApp or None
        """
        return self.apps.get(name)

    def list_apps(self) -> List[ServiceApp]:
        """List all registered apps.

        Returns:
            List of ServiceApp instances
        """
        return list(self.apps.values())

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict.

        Returns:
            Dict of name -> app info
        """
        return {
            name: app.to_dict()
            for name, app in self.apps.items()
        }


# Global registry
_registry: Optional[ServiceRegistry] = None


def get_registry() -> ServiceRegistry:
    """Get global service registry.

    Returns:
        ServiceRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = ServiceRegistry()
    return _registry


def register_app(app: ServiceApp) -> None:
    """Register service app globally.

    Args:
        app: ServiceApp to register
    """
    get_registry().register(app)


def get_app(name: str) -> Optional[ServiceApp]:
    """Get service app globally.

    Args:
        name: Service name

    Returns:
        ServiceApp or None
    """
    return get_registry().get(name)


def list_apps() -> List[ServiceApp]:
    """List all apps globally.

    Returns:
        List of ServiceApp instances
    """
    return get_registry().list_apps()


class ServiceEndpoints:
    """Standard service API endpoints."""

    CATALOG = "/catalog"
    RECORD = "/record/{record_id}"
    DELETE = "/record/{record_id}"
    HEALTH = "/health"

    @staticmethod
    def build_url(base_url: str, endpoint: str, **kwargs) -> str:
        """Build full endpoint URL.

        Args:
            base_url: Service base URL
            endpoint: Endpoint path
            **kwargs: Path parameters

        Returns:
            Full URL
        """
        url = base_url.rstrip("/") + endpoint.format(**kwargs)
        return url
