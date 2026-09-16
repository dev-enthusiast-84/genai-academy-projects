"""MCP (Model Context Protocol) server for withdrawal tools."""

import json
import asyncio
from typing import Dict, List, Any, Optional

from .core import Engine, BoundaryError


class MCPServer:
    """MCP server exposing withdrawal engine tools."""

    def __init__(self, engine: Engine, user_id: str, port: int = 8104):
        """Initialize MCP server.

        Args:
            engine: Withdrawal engine instance
            user_id: User ID for scoped operations
            port: Server port
        """
        self.engine = engine
        self.user_id = user_id
        self.port = port

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools in MCP format.

        Returns:
            List of tool definitions
        """
        return [
            {
                "name": "discover_records",
                "description": "Discover authorized record metadata",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search filter",
                        }
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "trace_lineage",
                "description": "Trace dependencies for a root record",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "root_id": {
                            "type": "string",
                            "description": "Root record ID",
                        }
                    },
                    "required": ["root_id"],
                },
            },
            {
                "name": "inspect_service",
                "description": "Check record state and version",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "record_id": {
                            "type": "string",
                            "description": "Record ID to inspect",
                        }
                    },
                    "required": ["record_id"],
                },
            },
        ]

    async def handle_call(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Handle tool call.

        Args:
            tool_name: Name of tool to call
            arguments: Tool arguments

        Returns:
            Tool result
        """
        try:
            if tool_name == "discover_records":
                query = arguments.get("query", "")
                return self.engine.discover_records(self.user_id, query)

            elif tool_name == "trace_lineage":
                root_id = arguments.get("root_id")
                if not root_id:
                    return {"error": "root_id required"}
                return self.engine.trace_lineage(self.user_id, root_id)

            elif tool_name == "inspect_service":
                record_id = arguments.get("record_id")
                if not record_id:
                    return {"error": "record_id required"}
                return self.engine.inspect_service(self.user_id, record_id)

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except BoundaryError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"Tool error: {str(e)}"}

    async def start(self) -> None:
        """Start MCP server.

        This is a minimal implementation. In production, would use
        a proper MCP protocol implementation.
        """
        try:
            import uvicorn
            from fastapi import FastAPI, HTTPException

            app = FastAPI(title="Recall MCP Server")

            @app.get("/mcp/tools")
            async def list_tools():
                return {"tools": self.get_tools()}

            @app.post("/mcp/call")
            async def call_tool(tool_name: str, arguments: Dict[str, Any]):
                result = await self.handle_call(tool_name, arguments)
                if "error" in result:
                    raise HTTPException(status_code=400, detail=result["error"])
                return result

            @app.get("/health")
            async def health():
                return {"status": "ok"}

            # Start server
            config = uvicorn.Config(
                app=app,
                host="127.0.0.1",
                port=self.port,
                log_level="info",
            )
            server = uvicorn.Server(config)
            await server.serve()

        except ImportError:
            raise RuntimeError(
                "FastAPI and Uvicorn required for MCP server. "
                "pip install fastapi uvicorn"
            )

    def run(self) -> None:
        """Run MCP server (blocking).

        Note: Use start() for async operation.
        """
        asyncio.run(self.start())


def create_mcp_server(
    engine: Engine,
    user_id: str,
    port: int = 8104,
) -> MCPServer:
    """Create and return MCP server.

    Args:
        engine: Withdrawal engine
        user_id: User ID
        port: Server port

    Returns:
        MCPServer instance
    """
    return MCPServer(engine, user_id, port)
