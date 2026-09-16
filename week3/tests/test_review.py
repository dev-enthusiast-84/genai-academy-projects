import json
from pathlib import Path
import pytest
from withdrawal.core import Engine, BoundaryError
from withdrawal.review import review_plan, hard_checks, deterministic_rehearsal, audit_outcome
from withdrawal.agent import settings

FIXTURE=json.loads((Path(__file__).resolve().parents[1]/'data/fitness.json').read_text())

class Script:
    def __init__(self, responses): self.responses=iter(responses)
    def complete(self, messages, tools): return next(self.responses)

def tool(name,args):
    return {'tool_calls':[{'id':'call','type':'function','function':{'name':name,'arguments':json.dumps(args)}}]}

def investigation():
    return [tool('discover_records',{'query':''}),tool('trace_lineage',{'root_id':'D1'}),
            {'content':json.dumps({'action':'propose','roots':['D1'],'targets':['D1','T1','V1','V2','P1','C1','Q1'],'message':'Trace ready.'})}]

def review(status='pass',refs=None):
    return {'content':json.dumps({'status':status,'explanation':'Checked the evidence.',
           'findings':[] if status=='pass' else [{'explanation':'Recheck source purpose.','references':refs or ['D1']}],
           'preserved_ids':['B1','V3']})}

@pytest.fixture
def engine(tmp_path):
    e=Engine(tmp_path); e.seed(FIXTURE)
    yield e
    e.close()

def test_review_gate_preserves_booking_and_never_writes(engine):
    result=review_plan(engine,Script(investigation()+[review(),review()]),'U1','Withdraw D1.')
    req=result['plan']
    assert result['action']=='propose' and req['evaluation']['verdict']=='pass'
    assert req['telemetry']['model_calls']==5
    assert 'B1' not in {t['id'] for t in req['targets']}
    assert engine.inspect_service('U1','B1')['state']=='present'
    assert all(engine.inspect_service('U1',t['id'])['state']=='present' for t in req['targets'])
    assert req['approval'] is None
    engine.approve(req['id'],'U1')

@pytest.mark.parametrize('bad',[{'content':'not json'},review('revise',['FOREIGN-RECORD'])])
def test_invalid_review_fails_closed(engine,bad):
    req=review_plan(engine,Script(investigation()+[bad]),'U1','Withdraw D1.')['plan']
    assert req['status']=='blocked'
    with pytest.raises(BoundaryError): engine.approve(req['id'],'U1')

def test_judge_disagreement_clarifies_before_approval(engine):
    req=review_plan(engine,Script(investigation()+[review(),review('clarify')]),'U1','Withdraw D1.')['plan']
    assert req['evaluation']['verdict']=='clarify'
    with pytest.raises(BoundaryError): engine.approve(req['id'],'U1')

def test_repair_reevaluates_new_plan(engine):
    responses=investigation()+[review(),review('revise')]+investigation()+[review(),review()]
    req=review_plan(engine,Script(responses),'U1','Withdraw D1.')['plan']
    assert req['evaluation']['rounds']==2 and req['status']=='awaiting_approval'
    old=[json.loads(r[0]) for r in engine.db.execute('SELECT payload FROM requests') if json.loads(r[0])['id']!=req['id']]
    assert len(old)==1 and old[0]['status']=='blocked'

def test_repairs_are_bounded(engine):
    req=review_plan(engine,Script((investigation()+[review(),review('revise')])*3),'U1','Withdraw D1.')['plan']
    assert req['status']=='blocked' and req['evaluation']['rounds']==3

def test_stale_evidence_invalidates_pass(engine):
    req=deterministic_rehearsal(engine,'U1')['plan']
    engine.db.execute("INSERT INTO edges VALUES ('D2','Q1','NEW')");engine.db.commit()
    assert hard_checks(engine,req)
    with pytest.raises(BoundaryError): engine.approve(req['id'],'U1')

def test_auditor_cannot_upgrade_failed_absence(engine):
    req=deterministic_rehearsal(engine,'U1')['plan']
    engine.approve(req['id'],'U1')
    req=audit_outcome(engine,Script([review()]),'U1',req['id'])
    assert req['status']=='partial' and req['outcome_audit']['verdict']=='unresolved'

def test_role_settings_defaults_and_legacy(tmp_path,monkeypatch):
    keys=['LLM_PROVIDER','LLM_MODEL','LLM_INVESTIGATOR_MODEL','LLM_SCOPE_REVIEWER_MODEL','LLM_JUDGE_MODEL','LLM_AUDITOR_MODEL']
    for key in keys: monkeypatch.delenv(key,raising=False)
    config=tmp_path/'config.env'
    config.write_text('LLM_PROVIDER=openrouter\n')
    assert settings(config)['models']['scope_reviewer']=='anthropic/claude-sonnet-4.6'
    config.write_text('LLM_PROVIDER=litellm\nLLM_MODEL=proxy-alias\nLLM_JUDGE_MODEL=judge-alias\n')
    assert settings(config)['models']=={'investigator':'proxy-alias','scope_reviewer':'proxy-alias','judge':'judge-alias','auditor':'proxy-alias'}
