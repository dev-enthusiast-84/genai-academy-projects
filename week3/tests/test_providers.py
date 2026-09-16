from types import SimpleNamespace
import httpx
import pytest
from withdrawal.agent import ModelClient, ModelError


def test_connection_failure_excludes_secrets():
    def fail(request):raise httpx.ConnectError('secret payload')
    client=ModelClient('https://openrouter.ai/api/v1','secret','','openrouter',httpx.MockTransport(fail))
    with pytest.raises(ModelError) as error:client.models()
    assert 'secret' not in str(error.value)


def test_judge_must_differ_from_generator():
    from withdrawal.agent import validate_role_models
    for left,right in [('gpt-4.1-mini','gpt-4.1-mini'),('GPT-4.1','gpt-4.1')]:
        with pytest.raises(ModelError,match='judge must use a different model'):
            validate_role_models({'investigator':left,'judge':right})
    validate_role_models({'investigator':'gpt-4.1-mini','judge':'gpt-4.1'})


def test_review_blocks_self_judging_before_model_calls():
    from withdrawal.review import review_plan
    client=SimpleNamespace(model='gpt-4.1-mini')
    with pytest.raises(ModelError,match='judge must use a different model'):
        review_plan(None,{'investigator':client,'judge':client},'U1','Withdraw D1')


def test_openai_profile_isolated_from_openrouter_settings(tmp_path, monkeypatch):
    import os
    from withdrawal.agent import settings
    for name in list(os.environ):
        if name.startswith(('LLM_', 'OPENAI_', 'OPENROUTER_')):
            monkeypatch.delenv(name)
    path = tmp_path / '.env'
    path.write_text('LLM_PROVIDER=openrouter\nLLM_BASE_URL=https://openrouter.ai/api/v1\nLLM_INVESTIGATOR_MODEL=gpt-4.1-mini\nLLM_JUDGE_MODEL=gpt-4.1\nLLM_API_KEY=proxy-key\nOPENAI_API_KEY=openai-test-key\n')
    original = path.read_text()
    local = settings(path)
    cloud = settings(path, provider='openai')
    assert cloud['base_url'] == 'https://api.openai.com/v1'
    assert cloud['api_key'] == 'openai-test-key'
    assert cloud['models']['investigator'] == 'gpt-4.1-mini'
    assert cloud['models']['judge'] == 'gpt-4.1'
    assert settings(path) == local
    assert path.read_text() == original
    monkeypatch.setenv('OPENAI_API_KEY', 'environment-test-key')
    assert settings(path, provider='openai')['api_key'] == 'environment-test-key'
    assert settings(path, provider='openrouter')['api_key'] != 'environment-test-key'


def test_openai_tool_calls_and_json_review_use_direct_api():
    import json
    from withdrawal.agent import TOOLS
    calls = []
    def respond(request):
        assert str(request.url) == 'https://api.openai.com/v1/chat/completions'
        assert request.headers['Authorization'] == 'Bearer test-key'
        payload = json.loads(request.content)
        calls.append(payload)
        message = {'role': 'assistant', 'content': '{"status":"pass"}'}
        if 'tools' in payload:
            message = {'role': 'assistant', 'content': None, 'tool_calls': [
                {'id': 'call_1', 'type': 'function', 'function': {'name': 'discover_records', 'arguments': '{"query":""}'}}]}
        return httpx.Response(200, json={'choices': [{'message': message}]})
    client = ModelClient('https://api.openai.com/v1','test-key','gpt-4.1-mini','openai',httpx.MockTransport(respond))
    assert client.complete([{'role':'user','content':'Investigate'}], TOOLS)['tool_calls']
    client.complete([{'role':'user','content':'Return JSON review'}])
    assert calls[0]['tools'] == TOOLS
    assert calls[1]['response_format'] == {'type': 'json_object'}
    assert all('provider' not in call and 'reasoning_effort' not in call for call in calls)


def test_openai_missing_key_does_not_call_network():
    client = ModelClient('https://api.openai.com/v1','','gpt-4.1-mini','openai',
                         httpx.MockTransport(lambda _: pytest.fail('No request without a key')))
    with pytest.raises(ModelError, match='OPENAI_API_KEY'):
        client.complete([{'role':'user','content':'Return JSON'}])


@pytest.mark.parametrize('provider', ['litellm', 'litellm_ollama', 'ollama'])
def test_removed_providers_are_rejected(provider, tmp_path, monkeypatch):
    from withdrawal.agent import settings
    monkeypatch.setenv('LLM_PROVIDER', provider)
    with pytest.raises(ModelError, match='Unsupported model provider'):
        settings(tmp_path / 'missing.env')
    with pytest.raises(ModelError, match='Unsupported model provider'):
        ModelClient('https://example.com/v1', '', '', provider)
