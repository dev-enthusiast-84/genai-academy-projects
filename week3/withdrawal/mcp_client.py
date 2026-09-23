"""Synchronous adapter over the optional official MCP streamable HTTP client."""
import asyncio
import json
from urllib.parse import urlparse
from .core import BoundaryError

READS = {'discover_records', 'trace_lineage', 'inspect_service'}


class MCPReads:
    def __init__(self, url):
        parsed = urlparse(url)
        if parsed.scheme != 'http' or parsed.hostname not in {'127.0.0.1', 'localhost', '::1'} or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise BoundaryError('The synthetic MCP endpoint must be a local HTTP URL without credentials or query strings.')
        self.url = url

    async def _run(self, name=None, arguments=None):
        try:
            from mcp import ClientSession
            from mcp.client.streamable_http import streamable_http_client
        except ImportError:
            raise BoundaryError('Install requirements-mcp.txt before selecting MCP transport.') from None
        async with streamable_http_client(self.url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                if name is None:
                    result = await session.list_tools()
                    return [tool.name for tool in result.tools]
                result = await session.call_tool(name, arguments)
                if result.isError:
                    raise BoundaryError('MCP rejected the scoped read.')
                payload = result.structuredContent
                if payload is None:
                    text = next((part.text for part in result.content if part.type == 'text'), '')
                    payload = json.loads(text)
                return payload

    def _sync(self, name=None, arguments=None):
        try:
            return asyncio.run(asyncio.wait_for(self._run(name, arguments), timeout=20))
        except BoundaryError:
            raise
        except Exception:
            raise BoundaryError('MCP read unavailable or returned invalid data. No deletion occurred.') from None

    def list_tools(self):
        return self._sync()

    def call_tool(self, name, arguments):
        if name not in READS:
            raise BoundaryError('Only investigator read tools are allowed through this adapter.')
        result = self._sync(name, arguments)
        if name == 'discover_records':
            if not isinstance(result, dict) or not isinstance(result.get('records'), list):
                raise BoundaryError('MCP discovery returned invalid metadata.')
            return result['records']
        if not isinstance(result, dict):
            raise BoundaryError('MCP read returned invalid metadata.')
        return result
