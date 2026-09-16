"""MCP (Model Context Protocol) client for calling withdrawal tools."""

import json
from typing import Dict, List, Any, Optional


class MCPClient:
    """Client for calling MCP server tools."""

    def __init__(self, base_url: str = "http://127.0.0.1:8104"):
        """Initialize MCP client.

        Args:
            base_url: MCP server URL
        """
        self.base_url = base_url.rstrip("/")

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from server.

        Returns:
            List of tool definitions
        """
        try:
            import requests
            response = requests.get(f"{self.base_url}/mcp/tools", timeout=5)
            response.raise_for_status()
            return response.json().get("tools", [])
        except Exception as e:
            print(f"Error fetching tools: {e}")
            return []

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the server.

        Args:
            tool_name: Name of tool to call
            arguments: Tool arguments

        Returns:
            Tool result
        """
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/mcp/call",
                    params={"tool_name": tool_name},
                    json=arguments,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {"error": f"HTTP {response.status}: {error_text}"}
                    return await response.json()
        except ImportError:
            # Fallback to sync
            return self.call_tool_sync(tool_name, arguments)
        except Exception as e:
            return {"error": str(e)}

    def call_tool_sync(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool synchronously.

        Args:
            tool_name: Name of tool to call
            arguments: Tool arguments

        Returns:
            Tool result
        """
        try:
            import requests
            response = requests.post(
                f"{self.base_url}/mcp/call",
                params={"tool_name": tool_name},
                json=arguments,
                timeout=30,
            )
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def health_check(self) -> bool:
        """Check if MCP server is healthy.

        Returns:
            True if server is up
        """
        try:
            import requests
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


def create_mcp_client(base_url: str = "http://127.0.0.1:8104") -> MCPClient:
    """Create MCP client.

    Args:
        base_url: MCP server URL

    Returns:
        MCPClient instance
    """
    return MCPClient(base_url)
