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


def test_review_receives_lineage_and_unlinked_booking_preservation(engine):
    class EvidenceReview:
        def complete(self, messages, tools):
            payload = json.loads(messages[-1]['content'])
            trail = payload['evidence']['lineage'][0]
            assert trail['root'] == 'D1'
            assert trail['shared_dependencies'] == []
            assert {r['id'] for r in trail['records']} == {'D1', 'T1', 'V1', 'V2', 'P1', 'C1', 'Q1'}
            actions = {r['id']: r['action'] for r in payload['exact_record_actions']}
            assert actions['B1'] == 'KEEP'
            assert all(actions[rid] == 'DELETE' for rid in ['P1', 'C1', 'Q1'])
            return review()

    clients = {'investigator': Script(investigation()),
               'scope_reviewer': EvidenceReview(), 'judge': EvidenceReview()}
    result = review_plan(engine, clients, 'U1',
                         'Withdraw D1 and its shared interests, recommendations and queued offers. Keep my paid booking.')
    assert result['action'] == 'propose'
    assert result['plan']['status'] == 'awaiting_approval'
    assert engine.inspect_service('U1', 'B1')['state'] == 'present'
    assert result['plan']['approval'] is None


def test_external_parent_is_still_a_shared_dependency(engine):
    engine.db.execute("INSERT INTO edges VALUES ('D2','C1','EXTERNAL-PARENT')")
    engine.db.commit()
    assert engine.trace_lineage('U1', 'D1')['shared_dependencies'] == ['C1']
    with pytest.raises(BoundaryError):
        engine.create_plan('U1', ['D1'])

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
    config.write_text('LLM_PROVIDER=openrouter\nLLM_MODEL=proxy-alias\nLLM_JUDGE_MODEL=judge-alias\n')
    assert settings(config)['models']=={'investigator':'proxy-alias','scope_reviewer':'proxy-alias','judge':'judge-alias','auditor':'proxy-alias'}


def test_false_booking_clarification_gets_one_evidence_correction(engine):
    false_question = {'content': json.dumps({'action': 'clarify', 'message': 'Keep Q1 as the paid booking?'})}
    class CorrectedInvestigation(Script):
        def complete(self, messages, tools):
            if 'Application evidence check' in messages[-1]['content']:
                facts = json.loads(messages[-1]['content'].split('\n', 1)[1])
                types = {r['id']: r for r in facts['record_types']}
                assert types['Q1'] == {'id': 'Q1', 'kind': 'queued_message', 'protected': False}
                assert types['B1']['protected'] is True
                assert facts['lineage'][0]['shared_dependencies'] == []
            return super().complete(messages, tools)
    script = investigation()
    result = review_plan(engine, CorrectedInvestigation(script[:2] + [false_question, script[2], review(), review()]),
                         'U1', 'Withdraw D1 and its descendants. Keep my paid booking.')
    assert result['plan']['status'] == 'awaiting_approval'
    assert result['plan']['approval'] is None
    assert 'Q1' in {t['id'] for t in result['plan']['targets']}
    assert 'B1' not in {t['id'] for t in result['plan']['targets']}


def test_genuine_clarification_stays_blocked_after_single_recheck(engine):
    question = {'content': json.dumps({'action': 'clarify', 'message': 'Keeping Q1 conflicts with removing every descendant. Which scope do you intend?'})}
    client = Script(investigation()[:2] + [question, question])
    result = review_plan(engine, client, 'U1', 'Withdraw D1 and all descendants but keep Q1.')
    assert result['action'] == 'clarify'
    assert engine.latest('U1') is None
    assert engine.inspect_service('U1', 'Q1')['state'] == 'present'


def test_failed_replacement_durably_invalidates_old_preview(engine):
    previous = deterministic_rehearsal(engine, 'U1')['plan']
    from withdrawal.agent import ModelError
    class Unavailable:
        def complete(self, *_args):
            raise ModelError('Provider unavailable')
    with pytest.raises(ModelError):
        review_plan(engine, Unavailable(), 'U1', 'A different request')
    fresh = Engine(engine.directory, require_review=True)
    try:
        assert fresh.get_request(previous['id'], 'U1')['status'] == 'needs_new_plan'
        with pytest.raises(BoundaryError):
            fresh.approve(previous['id'], 'U1')
        assert fresh.inspect_service('U1', 'D1')['state'] == 'present'
    finally:
        fresh.close()


def test_auditor_unresolved_clears_full_completion_flag(engine):
    req = deterministic_rehearsal(engine, 'U1')['plan']
    engine.approve(req['id'], 'U1')
    engine.delete_approved_records(req['id'], 'U1')
    result = audit_outcome(engine, Script([review('clarify')]), 'U1', req['id'])
    assert result['status'] == 'partial'
    assert result['full_withdrawal_complete'] is False


def test_langgraph_stages_and_repair_are_recorded(engine):
    req = review_plan(engine, Script(investigation() + [review(), review('revise')] +
                                    investigation() + [review(), review()]), 'U1', 'Withdraw D1.')['plan']
    assert req['telemetry']['framework'] == 'langgraph'
    nodes = req['telemetry']['graph_nodes']
    assert nodes == ['investigator', 'hard_checks', 'scope_reviewer', 'evaluation_judge',
                     'decision', 'repair', 'investigator', 'hard_checks', 'scope_reviewer',
                     'evaluation_judge', 'decision', 'finish']
    assert req['approval'] is None


def test_outcome_evidence_distinguishes_removed_targets_from_catalog(engine):
    req = deterministic_rehearsal(engine, 'U1')['plan']
    engine.approve(req['id'], 'U1')
    engine.delete_approved_records(req['id'], 'U1')

    class Auditor:
        def complete(self, messages, tools):
            assert 'This is a post-execution audit' in messages[0]['content']
            assert 'This is a pre-approval scope review' not in messages[0]['content']
            payload = json.loads(messages[-1]['content'])
            evidence = payload['evidence']
            assert set(evidence['proposal']['targets']) == {t['id'] for t in req['targets']}
            assert all(record['state'] == 'absent' for record in evidence['states'])
            actions = {r['id']: r['action'] for r in payload['exact_record_actions']}
            assert actions['Q1'] == 'DELETE' and actions['B1'] == 'KEEP'
            return review()

    result = audit_outcome(engine, Auditor(), 'U1', req['id'])
    assert result['outcome_audit']['verdict'] == 'pass'


def test_auditor_cannot_claim_removed_target_is_preserved(engine):
    req = deterministic_rehearsal(engine, 'U1')['plan']
    engine.approve(req['id'], 'U1')
    engine.delete_approved_records(req['id'], 'U1')
    bad = json.loads(review()['content'])
    bad['preserved_ids'] = ['D1', 'B1']
    result = audit_outcome(engine, Script([{'content': json.dumps(bad)}]), 'U1', req['id'])
    assert result['status'] == 'partial'
    assert result['outcome_audit']['verdict'] == 'unresolved'


def test_execution_graph_requires_approval_and_resumes_after_restart(engine):
    from withdrawal.workflow import execute_with_audit
    req = deterministic_rehearsal(engine, 'U1')['plan']
    audits = []

    def audit(request_id):
        audits.append(request_id)
        engine.verify_withdrawal(request_id, 'U1')

    with pytest.raises(BoundaryError):
        execute_with_audit(engine, 'U1', req['id'], audit)
    assert audits == []
    engine.approve(req['id'], 'U1')
    stopped = execute_with_audit(engine, 'U1', req['id'], audit, stop_after=1)
    assert stopped['status'] == 'interrupted' and audits == []
    fresh = Engine(engine.directory, require_review=True)
    try:
        completed = execute_with_audit(fresh, 'U1', req['id'],
                                       lambda rid: fresh.verify_withdrawal(rid, 'U1'))
        assert completed['status'] == 'complete'
        assert fresh.inspect_service('U1', 'B1')['state'] == 'present'
        assert all(t['attempts'] == 1 for t in completed['targets'])
    finally:
        fresh.close()
