import json
from pathlib import Path

import httpx
import pytest

from withdrawal.core import Engine
from withdrawal.notifications import notify_withdrawal_status


@pytest.fixture
def notification_case(tmp_path):
    engine = Engine(tmp_path)
    engine.seed(json.loads((Path(__file__).resolve().parents[1] / 'data/fitness.json').read_text()))
    req = engine.create_plan('U1', ['D1'])
    config = {'enabled': True, 'provider': 'slack', 'url': 'https://hooks.slack.com/services/test/secret/key',
              'timeout': 1, 'events': {'awaiting_approval', 'complete', 'review_blocked'}}
    yield engine, req, config
    engine.close()


def test_minimal_notification_deduplicates_across_restart(notification_case):
    engine, req, config = notification_case
    seen = []
    def send(request):
        seen.append(json.loads(request.content))
        return httpx.Response(200, text='ok')
    transport = httpx.MockTransport(send)
    assert notify_withdrawal_status(engine, 'U1', req['id'], config, transport)['result'] == 'sent'
    other = Engine(engine.directory)
    assert notify_withdrawal_status(other, 'U1', req['id'], config, transport)['result'] == 'already_attempted'
    other.close()
    assert len(seen) == 1
    assert 'yoga' not in json.dumps(seen) and 'Avery' not in json.dumps(seen)
    assert req['id'] in seen[0]['text']
    assert 'secret' not in json.dumps(engine.get_request(req['id'], 'U1'))


def test_disabled_and_invalid_destination_never_send(notification_case):
    engine, req, config = notification_case
    def fail(_):
        raise AssertionError('Network must not be called')
    transport = httpx.MockTransport(fail)
    assert notify_withdrawal_status(engine, 'U1', req['id'], {**config, 'enabled': False}, transport)['result'] == 'disabled_or_unnecessary'
    for url in ['http://localhost/private', 'https://hooks.slack.com.evil.example/services/x', 'https://hooks.slack.com:bad/services/x']:
        assert notify_withdrawal_status(engine, 'U1', req['id'], {**config, 'url': url}, transport)['result'] == 'configuration_required'


def test_timeout_is_unknown_and_does_not_change_withdrawal(notification_case):
    engine, req, config = notification_case
    def timeout(_):
        raise httpx.ReadTimeout('contains secret URL')
    transport = httpx.MockTransport(timeout)
    assert notify_withdrawal_status(engine, 'U1', req['id'], config, transport)['result'] == 'unknown'
    current = engine.get_request(req['id'], 'U1')
    assert current['status'] == req['status'] and not current['approval']
    assert 'secret URL' not in json.dumps(current)
    assert notify_withdrawal_status(engine, 'U1', req['id'], config, transport)['result'] == 'already_attempted'
