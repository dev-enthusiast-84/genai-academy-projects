import json
import importlib.util
import socket
import threading
import time
from pathlib import Path
import pytest
from withdrawal.agent import investigate
from withdrawal.core import Engine, BoundaryError
from withdrawal.mcp_client import MCPReads

FIXTURE=json.loads((Path(__file__).resolve().parents[1]/'data/fitness.json').read_text())

class Reader:
    def __init__(self, engine): self.engine, self.calls = engine, []
    def list_tools(self): self.calls.append('list_tools'); return ['discover_records','trace_lineage','inspect_service','delete_everything']
    def call_tool(self,name,args):
        self.calls.append(name)
        return getattr(self.engine,name)('U1',**args)

class Model:
    def __init__(self): self.turn=0
    def complete(self,messages,tools):
        self.turn+=1
        if self.turn < 3:
            name,args=('discover_records',{'query':''}) if self.turn==1 else ('trace_lineage',{'root_id':'D1'})
            return {'tool_calls':[{'id':str(self.turn),'function':{'name':name,'arguments':json.dumps(args)}}]}
        return {'content':json.dumps({'action':'propose','roots':['D1'],'targets':['D1','T1','V1','V2','P1','C1','Q1'],'message':'Read MCP evidence.'})}

def test_investigator_routes_actual_reads_to_mcp(tmp_path):
    engine=Engine(tmp_path);engine.seed(FIXTURE)
    reader=Reader(engine)
    result=investigate(engine,Model(),'U1','Withdraw D1.',mcp_client=reader)
    assert result['action']=='propose'
    assert reader.calls==['list_tools','discover_records','trace_lineage']
    assert engine.inspect_service('U1','D1')['state']=='present'
    with pytest.raises(BoundaryError): investigate(engine,Model(),'U2','Withdraw D3.',mcp_client=reader)
    engine.close()

def test_mcp_rejects_remote_endpoint_and_write_tool():
    with pytest.raises(BoundaryError): MCPReads('https://external.example/mcp')
    with pytest.raises(BoundaryError): MCPReads('http://127.0.0.1:8104/mcp').call_tool('delete_everything',{})

@pytest.mark.skipif(importlib.util.find_spec('mcp') is None, reason='Optional MCP SDK not installed')
def test_sdk_http_roundtrip_and_scope(tmp_path):
    import uvicorn
    from withdrawal.mcp_server import build_server
    engine=Engine(tmp_path);engine.seed(FIXTURE);engine.close()
    sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
    server=uvicorn.Server(uvicorn.Config(build_server(tmp_path,port=port).streamable_http_app(),host='127.0.0.1',port=port,log_level='error'))
    thread=threading.Thread(target=server.run,daemon=True);thread.start()
    try:
        for _ in range(100):
            if server.started: break
            time.sleep(.02)
        assert server.started
        client=MCPReads(f'http://127.0.0.1:{port}/mcp')
        assert set(client.list_tools())=={'discover_records','trace_lineage','inspect_service','inspect_customer_experience'}
        records=client.call_tool('discover_records',{'query':''})
        assert all(r['user_id']=='U1' and 'content' not in r for r in records)
        assert client.call_tool('trace_lineage',{'root_id':'D1'})['root']=='D1'
        assert client.call_tool('inspect_service',{'record_id':'D1'})['state']=='present'
        with pytest.raises(BoundaryError): client.call_tool('inspect_service',{'record_id':'D3'})
        engine=Engine(tmp_path)
        result=investigate(engine,Model(),'U1','Withdraw D1.',mcp_client=client)
        assert result['action']=='propose' and result['plan']['approval'] is None
        engine.close()
    finally:
        server.should_exit=True;thread.join(timeout=5)
