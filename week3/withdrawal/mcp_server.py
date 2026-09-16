"""Optional official MCP SDK server exposing scoped, read-only tools."""
from .core import Engine


def build_server(directory, port=8104):
    """Expose only scoped reads through the optional official SDK."""
    from mcp.server.fastmcp import FastMCP
    from .services import configured_services
    server = FastMCP('Recall scoped reads', host='127.0.0.1', port=port, stateless_http=True)

    def read(method, **arguments):
        engine = Engine(directory, configured_services())
        try:
            return getattr(engine, method)('U1', **arguments)
        finally:
            engine.close()

    @server.tool()
    def discover_records(query: str = '') -> dict:
        return {'records': read('discover_records', query=query)}

    @server.tool()
    def trace_lineage(root_id: str) -> dict:
        return read('trace_lineage', root_id=root_id)

    @server.tool()
    def inspect_service(record_id: str) -> dict:
        return read('inspect_service', record_id=record_id)

    @server.tool()
    def inspect_customer_experience() -> dict:
        engine = Engine(directory, configured_services())
        try:
            req = engine.latest('U1')
            return {'checks': engine.behavior_checks('U1', req) if req and engine.services else []}
        finally:
            engine.close()
    return server


if __name__ == '__main__':
    import os
    server = build_server(os.environ.get('RECALL_DATA_DIR', '.runtime/fitness/recall'),
                          int(os.environ.get('RECALL_MCP_PORT', '8104')))
    server.run(transport='streamable-http')
