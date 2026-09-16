"""Integration checks use real HTTP listeners and independent SQLite application stores."""
import json
import threading
import re
from pathlib import Path

import httpx
import pytest

from withdrawal.core import BoundaryError, Engine
from withdrawal.review import deterministic_rehearsal
from withdrawal.service_app import Store, make_server, page
from withdrawal.services import HttpServices, PORTS


@pytest.fixture
def connected(tmp_path):
    stores = {name: Store(tmp_path / 'apps', name) for name in PORTS}
    servers = {name: make_server(store, 'test-token', 0) for name, store in stores.items()}
    threads = [threading.Thread(target=server.serve_forever, daemon=True) for server in servers.values()]
    for thread in threads:
        thread.start()
    services = HttpServices({name: f'http://127.0.0.1:{server.server_port}' for name, server in servers.items()}, 'test-token')
    engine = Engine(tmp_path / 'recall', services, require_review=False)
    engine.seed(json.loads((Path(__file__).resolve().parents[1] / 'data/fitness.json').read_text()))
    try:
        yield engine, services, stores
    finally:
        engine.close()
        for server in servers.values():
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=2)


def test_consent_source_delete_and_independent_behavior(connected):
    engine, services, stores = connected
    assert engine.consent_status('U1')['state'] == 'not_granted'
    assert all(not services.behavior(name, 'U1')['consent_ids'] for name in PORTS)
    engine.grant_fitness_consent('U1')
    assert services.behavior('personalization', 'U1')['visible_ids'] == ['Q1']
    stores['documents'].delete_visible_profile()
    assert services.read('documents', 'D1', 'U1') is None
    assert 'V2' in services.behavior('search', 'U1')['visible_ids']
    assert 'Q1' in services.behavior('personalization', 'U1')['visible_ids']
    assert engine.consent_status('U1')['state'] == 'active'
    plan = deterministic_rehearsal(engine, 'U1')['plan']
    assert {t['id'] for t in plan['targets']} == {'D1', 'T1', 'V1', 'V2', 'P1', 'C1', 'Q1'}
    engine.approve(plan['id'], 'U1')
    result = engine.delete_approved_records(plan['id'], 'U1')
    assert result['status'] == 'complete'
    assert engine.consent_status('U1')['state'] == 'withdrawn'
    for name, store in stores.items():
        assert not services.behavior(name, 'U1')['consent_ids']
        for rid, record in store.fixture.items():
            if record.get('consent_root'):
                assert services.replay(name, rid, 'U1')['result'] == 'blocked'
    assert services.read('search', 'B1', 'U1') is not None
    assert services.read('documents', 'D3', 'U2') is not None


@pytest.mark.parametrize('service', ['search', 'personalization'])
def test_refresh_reports_latest_saved_state(connected, service):
    engine, services, stores = connected
    engine.grant_fitness_consent('U1')
    with httpx.Client(trust_env=False) as client:
        response = client.get(services.urls[service], params={'refresh': '1', 'q': 'yoga'})
        assert response.status_code == 200
        assert 'id="refresh-status" role="status"' in response.text
        assert 'Refreshed at ' in response.text
        assert 'Showing the latest saved information' in response.text
        assert '/?q=yoga&amp;refresh=1#refresh-status' in response.text
        assert response.headers['Cache-Control'] == 'no-store'
        plan = deterministic_rehearsal(engine, 'U1')['plan']
        engine.approve(plan['id'], 'U1')
        engine.delete_approved_records(plan['id'], 'U1')
        refreshed = client.get(services.urls[service], params={'refresh': '1'})
        assert 'No shared personalization records are stored here.' in refreshed.text
        assert 'Refreshed at ' in refreshed.text


def test_http_boundaries_and_durable_block(connected):
    engine, services, stores = connected
    with httpx.Client(trust_env=False) as client:
        response = client.post(services.urls['documents'] + '/api/read', json={'id': 'D1', 'user': 'U1'})
        assert response.status_code == 401
        response = client.post(services.urls['documents'] + '/consent', data={'agree': 'on', 'csrf': 'wrong'})
        assert response.status_code == 403
    with pytest.raises(BoundaryError):
        services.read('documents', 'D3', 'U1')
    with pytest.raises(BoundaryError):
        services.behavior('documents', 'U2')
    with pytest.raises(BoundaryError):
        services.delete('search', 'B1', 'U1', 1)
    services.block('documents', 'U1', ['D1'])
    reopened = Store(stores['documents'].path.parent, 'documents')
    assert reopened.operate('share', {'id': 'D1', 'user': 'U1'})[1]['result'] == 'blocked'
    with pytest.raises(BoundaryError):
        services.block('search', 'U1', ['B1'])


def test_visible_pages_match_customer_scope(connected):
    engine, _, stores = connected
    engine.grant_fitness_consent('U1')
    offers = page(stores['personalization'], '')
    assert 'Your evening yoga invitation' in offers
    assert 'Evening wellness audience' not in offers
    assert 'Nothing is sent' in offers
    club = page(stores['documents'], '', consent=engine.consent_status('U1'))
    assert 'Another member questionnaire' not in club
    assert 'Delete questionnaire only' in club


def test_customer_consent_form_and_visible_delete(connected, monkeypatch):
    engine, services, _ = connected
    monkeypatch.setenv('RECALL_DATA_DIR', str(engine.directory))
    monkeypatch.setenv('RECALL_SERVICE_URLS', json.dumps(services.urls))
    monkeypatch.setenv('RECALL_SERVICE_TOKEN', services.token)
    with httpx.Client(trust_env=False) as client:
        url = services.urls['documents']
        response = client.get(url)
        csrf = re.search(r'name="csrf" value="([^"]+)"', response.text).group(1)
        assert client.post(url + '/consent', data={'csrf': csrf}).status_code == 400
        assert engine.consent_status('U1')['state'] == 'not_granted'
        response = client.post(url + '/consent', data={'csrf': csrf, 'agree': 'on'})
        assert response.status_code == 200
        assert engine.consent_status('U1')['state'] == 'active'
        response = client.post(url + '/delete-profile', data={'csrf': csrf})
        assert response.status_code == 200
        assert 'Questionnaire removed · consent still active' in response.text
        assert engine.consent_status('U1')['state'] == 'active'
        assert services.read('documents', 'D1', 'U1') is None
        assert 'Q1' in services.behavior('personalization', 'U1')['visible_ids']


def test_real_application_outage_resumes(connected):
    engine, services, stores = connected
    engine.grant_fitness_consent('U1')
    plan = deterministic_rehearsal(engine, 'U1')['plan']
    engine.approve(plan['id'], 'U1')
    # Point the adapter at a closed local port: a genuine transport outage, not an engine fault flag.
    import socket
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        unavailable = probe.getsockname()[1]
    original_url = services.urls['personalization']
    services.urls['personalization'] = f'http://127.0.0.1:{unavailable}'
    partial = engine.delete_approved_records(plan['id'], 'U1')
    assert partial['status'] == 'partial'
    assert not partial['full_withdrawal_complete']
    services.urls['personalization'] = original_url
    completed = engine.delete_approved_records(plan['id'], 'U1')
    assert completed['status'] == 'complete'
    assert not services.behavior('personalization', 'U1')['consent_ids']
    assert services.read('search', 'B1', 'U1') is not None


def test_current_dashboard_workflow_remains_functional(connected, monkeypatch):
    from streamlit.testing.v1 import AppTest
    engine, services, _ = connected
    monkeypatch.setenv('RECALL_DATA_DIR', str(engine.directory))
    monkeypatch.setenv('RECALL_SERVICE_URLS', json.dumps(services.urls))
    monkeypatch.setenv('RECALL_SERVICE_TOKEN', services.token)
    monkeypatch.setenv('NOTIFICATION_ENABLED', 'false')
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=20)
    assert not app.exception
    assert any('Your Withdrawal Journey' in item.value for item in app.markdown)
    assert any('Data Flow & Sharing Status' in item.value for item in app.markdown)
    # Consent and source-only deletion belong to Club Portal, not Recall.
    with httpx.Client(trust_env=False) as client:
        club_url = services.urls['documents']
        response = client.get(club_url)
        csrf = re.search(r'name="csrf" value="([^"]+)"', response.text).group(1)
        assert client.post(club_url + '/consent', data={'csrf': csrf, 'agree': 'on'}).status_code == 200
    app.run(timeout=20)
    assert not app.exception
    assert services.read('personalization', 'Q1', 'U1') is not None
    with httpx.Client(trust_env=False) as client:
        assert client.post(club_url + '/delete-profile', data={'csrf': csrf}).status_code == 200
    app.run(timeout=20)
    assert not app.exception
    assert any('Consent still active · questionnaire removed' in item.value for item in app.markdown)
    assert not any('Active Now' in item.value for item in app.markdown)
    assert not any(b.key in {'btn_delete', 'btn_consent'} for b in app.button)
    assert services.read('documents', 'D1', 'U1') is None
    assert services.read('personalization', 'Q1', 'U1') is not None
    next(r for r in app.radio if r.label == 'Investigation mode').set_value('Guided rehearsal').run()
    next(b for b in app.button if b.label == 'Prepare scripted sample plan').click().run(timeout=20)
    assert not app.exception
    assert engine.latest('U1')['status'] == 'awaiting_approval'
    assert services.read('personalization', 'Q1', 'U1') is not None
    next(c for c in app.checkbox if c.label.startswith('I approve these')).check().run()
    next(b for b in app.button if b.label == 'Approve & withdraw').click().run(timeout=20)
    assert not app.exception
    assert engine.latest('U1')['status'] == 'complete'
    assert services.read('personalization', 'Q1', 'U1') is None
    assert services.read('search', 'B1', 'U1') is not None
    # A fresh UI session must recover the completed receipt from durable storage.
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=20)
    assert any('Sharing consent withdrawn' in item.value for item in app.markdown)
    assert not any('Consent still active' in item.value for item in app.markdown)
    next(b for b in app.button if b.label == 'Replay an old search-index job').click().run(timeout=20)
    assert not app.exception
    assert services.read('search', 'V1', 'U1') is None


def test_customer_actions_visible_in_browser(connected, monkeypatch):
    browser_api = pytest.importorskip('playwright.sync_api')
    engine, services, _ = connected
    monkeypatch.setenv('RECALL_DATA_DIR', str(engine.directory))
    monkeypatch.setenv('RECALL_SERVICE_URLS', json.dumps(services.urls))
    monkeypatch.setenv('RECALL_SERVICE_TOKEN', services.token)
    with browser_api.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            club = browser.new_page(viewport={'width': 1280, 'height': 900})
            club.goto(services.urls['documents'])
            browser_api.expect(club.get_by_role('button', name='Give consent & share interests')).to_be_visible()
            club.locator('input[name=agree]').check()
            club.get_by_role('button', name='Give consent & share interests').click()
            browser_api.expect(club.get_by_role('button', name='Delete questionnaire only')).to_be_enabled()
            club.get_by_role('button', name='Delete questionnaire only').click()
            browser_api.expect(club.get_by_role('heading', name='Questionnaire removed · consent still active')).to_be_visible()
            browser_api.expect(club.get_by_role('button', name='Delete questionnaire only')).to_be_disabled()
            assert services.read('personalization', 'Q1', 'U1') is not None
            for service in ['search', 'personalization']:
                page = browser.new_page(viewport={'width': 390, 'height': 844})
                page.goto(services.urls[service])
                browser_api.expect(page.get_by_role('link', name='Refresh this app')).to_be_visible()
                browser_api.expect(page.get_by_role('link', name='Withdraw via Recall ↗')).to_be_visible()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        finally:
            browser.close()


def test_provider_switch_keeps_openrouter_configuration(connected, monkeypatch):
    from streamlit.testing.v1 import AppTest
    engine, services, _ = connected
    monkeypatch.setenv('RECALL_DATA_DIR', str(engine.directory))
    monkeypatch.setenv('RECALL_SERVICE_URLS', json.dumps(services.urls))
    monkeypatch.setenv('RECALL_SERVICE_TOKEN', services.token)
    monkeypatch.setenv('LLM_PROVIDER', 'openrouter')
    monkeypatch.setenv('NOTIFICATION_ENABLED', 'false')
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=20)
    before = next(s.value for s in app.selectbox if s.label == 'Investigator model')
    next(s for s in app.selectbox if s.label == 'Provider').set_value('openai').run(timeout=20)
    assert not app.exception
    assert next(s.value for s in app.selectbox if s.label == 'Investigator model') == 'gpt-4.1-mini'
    assert next(s.value for s in app.selectbox if s.label == 'LLM judge model') == 'gpt-4.1'
    assert next(t.value for t in app.text_input if t.label == 'API base URL') == 'https://api.openai.com/v1'
    next(s for s in app.selectbox if s.label == 'Provider').set_value('openrouter').run(timeout=20)
    assert not app.exception
    assert next(s.value for s in app.selectbox if s.label == 'Investigator model') == before
    assert engine.latest('U1') is None
