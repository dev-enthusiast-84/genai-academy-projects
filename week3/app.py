from __future__ import annotations
import html
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime
import streamlit as st
from withdrawal.core import Engine, BoundaryError
from withdrawal.agent import ModelClient, ModelError, settings, validate_role_models
from withdrawal.services import configured_services
from withdrawal.review import review_plan, deterministic_rehearsal, audit_outcome
from ui.identity import app_identity, persona, identity_css
from withdrawal.workflow import execute_with_audit
from withdrawal.notifications import notification_settings, notify_withdrawal_status

ROOT = Path(__file__).parent
USER = 'U1'
FIXTURE = json.loads((ROOT / 'site/fitness.json').read_text())
st.set_page_config(page_title='Recall — consent has an undo button', page_icon='↩', layout='wide', initial_sidebar_state='collapsed')
st.markdown('<style>' + (ROOT / 'ui/recall.css').read_text() + identity_css() + '</style>', unsafe_allow_html=True)

def esc(value):
    return html.escape(str(value))

services = configured_services()
engine = Engine(os.environ.get('RECALL_DATA_DIR', str(ROOT / '.runtime' / 'fitness-local')), services, require_review=True)
if not engine.db.execute('SELECT 1 FROM catalog LIMIT 1').fetchone():
    engine.seed(FIXTURE)
engine.purge_expired_requests()
config = settings(ROOT / '.env')
notification_config = notification_settings(ROOT / '.env')
config_revision = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
if st.session_state.get('model_config_revision') != config_revision:
    # Apply edited defaults once; manual provider switching still works until
    # the saved configuration changes again. Never put credentials in a key.
    st.session_state['selected_provider'] = config['provider']
    for configured_name in ['openai', 'openrouter']:
        for suffix in ['investigator_model', 'scope_reviewer_model', 'judge_model', 'auditor_model']:
            st.session_state.pop(f'{configured_name}_{suffix}', None)
        st.session_state.pop(f'url_{configured_name}', None)
        st.session_state.pop(f'key_{configured_name}', None)
    st.session_state['model_config_revision'] = config_revision

with st.sidebar:
    st.header('Model connection')
    st.caption('Connect OpenAI or OpenRouter to investigate your withdrawal request.')
    providers = ['openai', 'openrouter']
    provider = st.selectbox('Provider', providers, key='selected_provider',
                           format_func=lambda p: {'openai':'OpenAI · direct API', 'openrouter':'OpenRouter'}[p])
    provider_config = settings(ROOT / '.env', provider=provider)
    base_url = st.text_input('API base URL', value=provider_config['base_url'], key=f'url_{provider}', disabled=provider=='openai')
    api_key = st.text_input('API key', value=provider_config['api_key'], type='password', key=f'key_{provider}')
    if provider == 'openai':
        st.caption('Paid API · sends authorized demo evidence to OpenAI.')
    connection_id = hashlib.sha256(json.dumps([provider, base_url.rstrip('/'), api_key]).encode()).hexdigest()
    catalog_key = f'model_catalog_{connection_id}'
    if st.button('Load available models', width='stretch'):
        try:
            st.session_state[catalog_key] = ModelClient(base_url, api_key, '', provider).models()
        except ModelError as exc:
            st.error(str(exc))
    available = st.session_state.get(catalog_key, [])
    if available:
        st.caption(f'{len(available)} tool-capable models loaded. Select a model for each role below.')
    elif catalog_key in st.session_state:
        st.warning('The provider returned no tool-capable models. Enter a model ID below or check the connection.')
    else:
        st.caption('Load available models to browse the catalog, or type a model ID into any picker below.')
    defaults = provider_config.get('models', {})
    role_models = {}
    for role, label in [('investigator', 'Investigator'), ('scope_reviewer', 'Scope reviewer'), ('judge', 'LLM judge'), ('auditor', 'Outcome auditor')]:
        key = f'{provider}_{role}_model'
        default = defaults.get(role, '')
        current = st.session_state.get(key, default)
        options = list(dict.fromkeys(value for value in [current, default, *available] if value))
        role_models[role] = st.selectbox(
            label + ' model', options, index=options.index(current) if current in options else None,
            key=key, accept_new_options=True, placeholder='Select or enter a model ID',
            help='Choose from the loaded catalog, or type a custom model ID and press Enter.',
        ) or ''
    model = role_models['investigator']
    st.caption('Three agent roles plus a separate judge. At most two repair rounds; each investigation has bounded reads.')
    st.divider()
    st.subheader('Demo controls')
    mode = st.radio('Investigation mode', ['Live agent', 'Guided rehearsal'], help='Rehearsal is a scripted fixture path; it does not call a model.')
    fault = st.selectbox('Execution scenario', ['Healthy services', 'Member Offers offline', 'Search service offline', 'One temporary search failure', 'Lost delete response', 'Worker restart after one deletion'])
    reset_ok = st.checkbox('Reset all local synthetic data and request history')
    if st.button('Reset demo', disabled=not reset_ok, width='stretch'):
        try:
            engine.seed(FIXTURE)
        except ConnectionError:
            st.error('Start all three applications before resetting the connected demo.')
            st.stop()
        for key in ['agent_trace', 'agent_message', 'replay_result', 'needs_clarification']:
            st.session_state.pop(key, None)
        st.session_state['reset_notice'] = True
        st.rerun()
    if st.session_state.pop('reset_notice', False):
        st.success('Demo reset complete. Previous requests, consent choices, and reuse blocks '
                   'were cleared. Starting demo data has been restored.')
        if services:
            st.info('Refresh Club Portal, Class Booking, and Member Offers. '
                    'Give consent in Club Portal to start the demo again. '
                    'The sample paid booking and membership are available.')
    st.caption('Single-user local demo • Avery Example (U1). No production sign-in.')
    st.caption('Status notifications: ' + (notification_config['provider'] + ' enabled' if notification_config['enabled'] else 'disabled; configure in .env'))
    if notification_config['enabled']:
        notification_config = {**notification_config, 'enabled': st.checkbox('Send status notifications to the configured Slack destination', value=False)}

st.markdown('<div class="brand"><span class="brand-symbol">↩</span> Recall <span class="brand-note">Consent has an undo button · working demo</span></div>', unsafe_allow_html=True)
st.markdown('<div class="kicker">Your information. Your decision.</div>', unsafe_allow_html=True)
st.title('You deleted the form.\nWho still remembers?')
st.markdown('<p class="lede">Your club questionnaire can live on as class preferences, an audience label, and a queued offer. Follow the evidence and take back your consent.</p>', unsafe_allow_html=True)

st.markdown(persona(), unsafe_allow_html=True)

st.markdown('<a href="#withdrawal-controls">Manage consent withdrawal ↓</a>', unsafe_allow_html=True)

# Workflow guide with actions
st.markdown('### 🧭 Your Withdrawal Journey')

# Get current consent state early
consent_state = engine.consent_status(USER)["state"]
try:
    source_state = engine.inspect_service(USER, 'D1')['state']
except BoundaryError:
    source_state = 'not_shared'
consent_label = {'not_granted': 'Consent not given', 'active': 'Sharing consent active', 'withdrawn': 'Sharing consent withdrawn'}[consent_state]
source_label = {'present': 'Questionnaire stored in Club Portal', 'absent': 'Questionnaire removed from Club Portal',
                'unknown': 'Questionnaire status unavailable', 'not_shared': 'Questionnaire not shared yet'}[source_state]
if consent_state == 'active' and source_state == 'absent':
    consent_label = 'Consent still active · questionnaire removed'
current_request = engine.latest(USER)
withdrawal_complete = bool(current_request and current_request['status'] == 'complete')

journey_cols = st.columns(3)
with journey_cols[0]:
    step_bg = '#f2e8dd' if consent_state != "active" else '#c8e6c9'
    step_border = '#984b32' if consent_state != "active" else '#2e7d32'
    step_marker = '→' if consent_state == "active" else '1️⃣'
    st.markdown(f'''
    <div style="background:{step_bg}; padding:14px; border-left:4px solid {step_border}; border-radius:6px;">
        <strong style="color:#333;">{step_marker} Sharing consent</strong><br>
        <small style="color:#666;">{esc(source_label)}</small>
        <div style="margin-top:8px; color:#62564b; font-size:11px;"><strong>{esc(consent_label)}</strong></div>
    </div>
    ''', unsafe_allow_html=True)

with journey_cols[1]:
    step_enabled = consent_state == "active"
    step_bg = '#fff3e0' if not step_enabled else '#fff9e6'
    step_border = '#999' if not step_enabled else '#85651f'
    step_marker = '2️⃣' if not step_enabled else '→'
    st.markdown(f'''
    <div style="background:{step_bg}; padding:14px; border-left:4px solid {step_border}; border-radius:6px; opacity:{'0.6' if not step_enabled else '1'};">
        <strong style="color:#333;">{step_marker} See Personalization</strong><br>
        <small style="color:#666;">Apps use your data to personalize</small>
        <div style="margin-top:8px; color:#62564b; font-size:11px;">{'Consent permits personalization' if step_enabled else 'Consent withdrawn · check removal receipt below' if consent_state == 'withdrawn' else 'Give consent first'}</div>
    </div>
    ''', unsafe_allow_html=True)

with journey_cols[2]:
    step_enabled = consent_state == "active"
    step_bg = '#f3e5f5' if not step_enabled else '#fce4ec'
    step_border = '#999' if not step_enabled else '#69445e'
    step_marker = '3️⃣' if not step_enabled else '→'
    st.markdown(f'''
    <div style="background:{step_bg}; padding:14px; border-left:4px solid {step_border}; border-radius:6px; opacity:{'0.6' if not step_enabled else '1'};">
        <strong style="color:#333;">{step_marker} Withdraw & Delete</strong><br>
        <small style="color:#666;">Take back control, delete everywhere</small>
        <div style="margin-top:8px; color:#69445e; font-size:11px;"><strong>{'Withdrawal verified' if withdrawal_complete else 'Withdrawal unfinished · check receipt' if consent_state == 'withdrawn' else 'Ready to request withdrawal' if step_enabled else 'After giving consent'}</strong></div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('---')

# Customer actions belong in their own applications; keep the workflow overview here.
st.markdown('### Customer apps · manage and inspect your information')
app_urls = services.urls if services else {'documents': 'http://127.0.0.1:8101', 'search': 'http://127.0.0.1:8102', 'personalization': 'http://127.0.0.1:8103'}
for column, (service, label, actions) in zip(st.columns(3), [
    ('documents', 'Open Club Portal ↗', 'Give sharing consent or delete only the original questionnaire.'),
    ('search', 'Open Class Booking ↗', 'Search saved information, inspect recommendations and your paid booking.'),
    ('personalization', 'Open Member Offers ↗', 'Inspect the personalized invitation retained by this app.')]):
    with column.container(key=f'app-{service}'):
        st.markdown(app_identity(service), unsafe_allow_html=True)
        st.link_button(label, app_urls[service], width='stretch')
        st.caption(actions)
st.caption('In Recall: investigate linked copies → review the plan → approve withdrawal → verify each app. Deleting the questionnaire alone does not do this.')
st.divider()

# Data flow visualization
if st.session_state.get('withdrawal_requested'):
    st.info('Continue below: investigate the data trail, review the exact records, then approve withdrawal.')
st.markdown('### ⇄ Data Flow & Sharing Status')
if consent_state == 'active' and source_state == 'absent':
    st.warning('The questionnaire is gone from Club Portal, but sharing consent is still active. Downstream copies may remain. Investigate and approve withdrawal below to remove linked copies.')

if consent_state == "active":
    active_records = []
    for meta in engine.discover_records(USER):
        if engine.inspect_service(USER, meta["id"])["state"] == "present":
            record = engine._read_record(meta["service"], meta["id"], USER)
            if record:
                active_records.append(record)
    # Get derived records to show data flow
    source_records = [r for r in active_records if r.get('user_id') == USER and r.get('consent_root') == 'D1' and r.get('type') == 'source_document']
    derived_class = [r for r in active_records if r.get('user_id') == USER and r.get('service') == 'search' and r.get('consent_root') == 'D1']
    derived_offers = [r for r in active_records if r.get('user_id') == USER and r.get('service') == 'personalization' and r.get('consent_root') == 'D1']

    st.markdown('''
    <div style="background: linear-gradient(135deg, #e8f5e9 0%, #fff3e0 100%); padding: 16px; border-radius: 8px; border-left: 5px solid #4caf50; margin: 12px 0;">
        <strong style="color:#2e7d32; font-size: 14px;">Sharing consent active</strong><br>
        <small style="color:#555;">Current records found in the connected apps are shown below. Consent status is separate from record presence.</small>
    </div>
    ''', unsafe_allow_html=True)

    flow_col1, flow_col2, flow_col3, flow_col4 = st.columns([2, 1, 1.5, 1.5])

    with flow_col1:
        st.markdown('**Source** (You shared this)')
        if source_records:
            for rec in source_records:
                st.markdown(f'''
                <div style="background:#e8f5e9; padding:10px; border-left:3px solid #2e7d32; margin:8px 0; border-radius:4px; font-size:11px;">
                    <strong style="color:#1b5e20;">{rec.get("title", "")}</strong><br>
                    <small style="color:#558b2f;">{rec.get("content", "")[:50]}...</small>
                </div>
                ''', unsafe_allow_html=True)

    if not source_records:
        with flow_col1:
            st.caption(source_label)

    with flow_col2:
        st.markdown('')
        st.markdown('<div style="text-align:center; color:#4caf50; font-size:20px; margin-top:20px;">→</div>', unsafe_allow_html=True)

    with flow_col3:
        st.markdown('**Class Booking** (Using your preferences)')
        if derived_class:
            count = len([r for r in derived_class if r.get('consent_root') == 'D1'])
            st.markdown(f'<div style="background:#fff3e0; padding:10px; border-left:3px solid #f57f17; border-radius:4px; font-size:11px; color:#e65100;"><strong>📥 {count} derived record(s)</strong><br>Recommendations based on your interests</div>', unsafe_allow_html=True)

    with flow_col4:
        st.markdown('**Member Offers** (Personalized for you)')
        if derived_offers:
            count = len([r for r in derived_offers if r.get('consent_root') == 'D1'])
            st.markdown(f'<div style="background:#f3e5f5; padding:10px; border-left:3px solid #69445e; border-radius:4px; font-size:11px; color:#4a148c;"><strong>📥 {count} derived record(s)</strong><br>Targeted offers & audience</div>', unsafe_allow_html=True)

elif consent_state == 'withdrawn':
    st.info('Sharing consent withdrawn. ' + ('All approved copies are verified absent.' if withdrawal_complete else 'Removal is not yet complete; check the receipt below.'))
else:
    st.info('Sharing consent not given. Start in Club Portal: give consent, see the other apps personalize, then delete your questionnaire. Return here to investigate what remains.')

if mode=='Guided rehearsal':
    st.warning('Guided rehearsal — the investigation is scripted. Deletions, recovery, verification, and replay protection use the real local stores.')
else:
    st.caption(f"Live agent team · {role_models.get('investigator') or 'select a model in the sidebar'} · {provider}")

if not services:
    st.info('Local rehearsal stores. For three independent customer apps and consent-first onboarding, start with: python3 run_demo.py')

clients = {role: ModelClient(base_url, api_key, selected, provider) for role, selected in role_models.items()}
ready = bool(all(role_models.values()) and api_key)
try:
    validate_role_models(role_models)
except ModelError as exc:
    st.warning(str(exc))
    ready = False
root_exists = bool(engine.db.execute("SELECT 1 FROM catalog WHERE id='D1' AND user_id=?", (USER,)).fetchone())

def run_audit(request_id):
    if mode == 'Live agent' and ready:
        with st.spinner('Outcome auditor is checking the customer experience…'):
            try:
                audit_outcome(engine, clients, USER, request_id)
                current = engine.get_request(request_id, USER)
                current.pop('audit_error', None)
                engine.save(current)
            except (ModelError, BoundaryError) as exc:
                current = engine.get_request(request_id, USER)
                current['audit_error'] = str(exc)
                engine.save(current)
    else:
        engine.verify_withdrawal(request_id, USER)

st.markdown('<div id="withdrawal-controls"></div>', unsafe_allow_html=True)
with st.container(key='withdrawal-request'):
    st.markdown('<div class="case-label">CASE SUBJECT / AVERY EXAMPLE · SYNTHETIC DATA</div>', unsafe_allow_html=True)
    st.subheader('Withdraw consent across all apps')
    st.caption('1. Prepare a plan → 2. Review and approve → 3. Verify removal. Preparing a plan does not withdraw consent or delete data.')
    with st.form('request_form'):
        request_text = st.text_area('What would you like withdrawn?', value='Withdraw my fitness-personalization consent for my fitness interests questionnaire. Remove its shared interests, recommendations and queued offers. Keep my paid class booking.', height=90)
        submit = st.form_submit_button('Prepare withdrawal plan' if mode=='Live agent' else 'Prepare scripted sample plan', type='primary', disabled=not root_exists or (mode=='Live agent' and not ready), width='stretch')
    if submit:
        # An earlier preview cannot be approved while a replacement is prepared.
        st.session_state['needs_clarification'] = True
    if not root_exists:
        st.info('To enable plan preparation, give consent in Club Portal, then reload Recall. '
                'You can delete the questionnaire in Club Portal before returning to investigate its copies.')
    if mode=='Live agent' and not ready:
        st.info('Open the sidebar to configure your selected provider and models. For OpenAI, add OPENAI_API_KEY to .env or enter it there.')
    investigation_progress = st.container()
    if st.session_state.get('agent_message') and not submit:
        if st.session_state.get('needs_clarification'):
            st.warning(st.session_state['agent_message'])
        else:
            st.success('Plan preparation complete · ready for your approval. ' + st.session_state['agent_message'])

# Keep the receipt and approval directly below the request at full width.
# Reserve its position before rendering the supporting evidence trail.
withdrawal_review = st.container(key='withdrawal-review')

with st.container():
    req = engine.latest(USER)
    st.subheader('The evidence trail')
    trail = engine.trace_lineage(USER, 'D1') if root_exists else {'records': [], 'edges': []}
    displayed = req['targets'] if req else trail['records']
    parts = []
    labels = {'documents':'Club Portal', 'search':'Class Booking', 'personalization':'Member Offers'}
    for service in ['documents','search','personalization']:
        cards = []
        for rec in displayed:
            if rec['service'] != service:
                continue
            state = engine.inspect_service(USER, rec['id'])['state']
            label = {'present':'Present', 'absent':'Verified absent', 'unknown':'Unable to verify'}[state]
            cards.append(f'<div class="record"><div class="record-title">{esc(rec["title"])}</div><span class="badge {state}">{label}</span></div>')
        parts.append(f'<div class="lane"><div class="lane-title">{app_identity(service)}</div>{"".join(cards)}</div>')
    st.markdown('<div class="trail">'+''.join(parts)+'</div>', unsafe_allow_html=True)
    edges = req['edges'] if req else trail['edges']
    linked_records = {record['id']: record for record in trail['records']}
    linked_records.update({record['id']: record for record in displayed})

    def describe_record(record_id):
        record = linked_records.get(record_id)
        if not record:
            return 'Record details unavailable'
        return f"{record['title']} ({labels.get(record['service'], record['service'])})"

    with st.expander('How your information was shared'):
        st.caption('Each row shows how one saved item was used to create another. These are recorded relationships; they do not mean the items still exist after withdrawal.')
        readable_links = []
        for edge in edges:
            source = linked_records.get(edge['source'], {})
            target = linked_records.get(edge['target'], {})
            relationship = ('Used to create another item in the same app'
                            if source.get('service') and source.get('service') == target.get('service')
                            else 'Shared with another app' if source and target
                            else 'Recorded link; app details unavailable')
            relationship = {
                'extracted_text': 'Fitness interests were extracted from your questionnaire.',
                'copied_preference': 'Your fitness interests were copied to this app for personalization.',
                'recommendation_cache': 'Your interests were used to create a class recommendation.',
                'audience_membership': 'Your interests were used to add you to an offers audience.',
                'queued_message': 'An invitation was prepared for this audience; it was not sent.',
            }.get(target.get('kind'), relationship)
            readable_links.append({'From': describe_record(edge['source']),
                                   'To': describe_record(edge['target']),
                                   'What happened': relationship})
        if readable_links:
            st.table(readable_links)
        else:
            st.caption('No sharing relationships were found.')
    with st.expander('Technical sharing references'):
        st.caption('D1, T1 and similar codes identify records. SHARE-… identifies a sharing event logged by this demo; it is a reference number, not an explanation or an external document.')
        st.table([{'Reference': edge.get('evidence', 'Not recorded'),
                   'From': f"{edge['source']} · {describe_record(edge['source'])}",
                   'To': f"{edge['target']} · {describe_record(edge['target'])}"}
                  for edge in edges])
    with st.expander('Test what the application can still retrieve', expanded=True):
        query = st.text_input('Search synthetic information', value='evening yoga')
        hits = engine.search(USER, query) if query.strip() else []
        st.caption(f'{len(hits)} accessible matching records · lexical search over active stores')
        for hit in hits:
            st.write(f"**{describe_record(hit['id'])}** — {hit['text']}")
        if not hits:
            st.write('No accessible matches. An offline service is excluded; the receipt remains the source of verification status.')
    if req:
        with st.expander('Agent read-tool evidence'):
            trace = req.get('investigation', st.session_state.get('agent_trace', []))
            if trace:
                st.json(trace)
            else:
                st.caption('No live model trace exists for this scripted rehearsal.')

with withdrawal_review:
    req = engine.latest(USER)
    if req:
        notification = notify_withdrawal_status(engine, USER, req['id'], notification_config)
        if notification['result'] == 'configuration_required':
            st.warning('Notifications need valid provider settings in .env.')
        req = engine.get_request(req['id'], USER)
        verified = sum(t['verification']=='absent' for t in req['targets'])
        total = len(req['targets'])
        complete = req['status']=='complete'
        label = {'awaiting_approval':'Awaiting your approval','approved':'Approved','executing':'In progress','partial':'Partial withdrawal','complete':'Withdrawal verified','interrupted':'Ready to resume','needs_new_plan':'New approval needed','approval_revoked':'Approval revoked'}.get(req['status'],req['status'])
        st.markdown(f'<div class="receipt"><div class="receipt-title">Withdrawal receipt / {esc(req["id"])}</div><div class="stamp {"" if complete else "pending"}">{esc(label.upper())}</div><div class="receipt-number">{verified} / {total}</div><p class="receipt-copy">records independently verified absent</p><p class="receipt-copy">{esc(req["scope"])}</p></div>', unsafe_allow_html=True)
        st.caption('Live model investigation' if req['origin']=='live_agent' else 'Scripted rehearsal · no model investigation')
        gate = req.get('evaluation', {})
        if gate:
            st.write('**Before your approval**')
            st.caption(f"Evaluation: {gate.get('verdict', 'pending')} · {gate.get('mode', 'live')} · {gate.get('rounds', 0)} review rounds")
            with st.expander('Review findings and corrections', expanded=gate.get('verdict') != 'pass'):
                for review in req.get('reviews', []):
                    st.write(f"**{review['role'].replace('_', ' ').title()} · {review['status']}**")
                    st.write(review['explanation'])
                    for finding in review['findings']:
                        st.caption(finding['explanation'] + ' · Evidence: ' + ', '.join(finding['references']))
                if not req.get('reviews'):
                    st.write('Scripted checks only; no model review.' if gate.get('mode') == 'deterministic_rehearsal_no_llm' else 'Model review has not completed.')
                if gate.get('verdict') != 'pass':
                    for finding in gate.get('findings', []):
                        st.write(finding.get('explanation', str(finding)) if isinstance(finding, dict) else finding)
        if req['status'] in ['under_review', 'review_blocked', 'blocked']:
            st.warning('This proposal has not passed review. Resolve the findings and investigate again; approval is unavailable.')
        if req['status']=='awaiting_approval':
            st.write('**Review the exact change**')
            if st.session_state.get('needs_clarification'):
                st.warning('This is an earlier preview. Resolve your latest clarification before approving a new plan.')
            scope_rows = []
            for target in req['targets']:
                state = engine.inspect_service(USER, target['id'])['state']
                scope_rows.append({
                    'Information in scope': target['title'],
                    'App': labels.get(target['service'], target['service']),
                    'Current state': {'present': 'Still stored', 'absent': 'Already absent',
                                      'unknown': 'Unable to verify'}[state],
                    'Action after approval': {
                        'present': 'Delete, verify absence, and block re-import',
                        'absent': 'Recheck absence and block re-import',
                        'unknown': 'Check service, remove if present, and block re-import',
                    }[state],
                })
            st.table(scope_rows)
            st.caption('Already-absent records remain in scope to verify they stay absent and prevent re-import. They are not counted as newly deleted records.')
            st.caption('Your paid class booking, membership contact card, and public class listings will be kept.')
            with st.expander('Technical record references'):
                st.table([{'Information': t['title'], 'Record ID': t['id'],
                           'Service': t['service'], 'Version': t['version']} for t in req['targets']])
            st.caption('Approval withdraws the selected sharing consent, removes any remaining information in scope, verifies absence, and blocks these records from being imported again. Up to two retries per record; approval expires after 24 hours. Deletion cannot be undone.')
            consent = st.checkbox('I approve these deletions and re-ingestion blocks', key=f'approve_{req["id"]}')
            if st.button('Approve & withdraw', type='primary', disabled=not consent or st.session_state.get('needs_clarification',False), width='stretch'):
                try:
                    engine.approve(req['id'], USER)
                    engine.clear_faults()
                    if fault=='Member Offers offline':
                        engine.set_fault('personalization')
                    elif fault=='Search service offline':
                        engine.set_fault('search')
                    elif fault=='One temporary search failure':
                        engine.set_fault('search','fail_before_commit',1)
                    elif fault=='Lost delete response':
                        engine.set_fault('search','commit_then_timeout',1)
                    execute_with_audit(engine, USER, req['id'], run_audit,
                                       stop_after=1 if fault=='Worker restart after one deletion' else None)
                    st.rerun()
                except BoundaryError as exc:
                    st.error(str(exc))
        elif req['status'] in ['partial','interrupted','approved','executing']:
            st.warning('Some work is unfinished. Completed records and approval are saved; refresh or restart will preserve them.')
            exhausted = any(t['attempts']>=3 and t['verification']!='absent' for t in req['targets'])
            if exhausted:
                st.info('The approved retry allowance is exhausted. Start a fresh investigation and approve a new plan to authorize more attempts.')
            if st.button('Restore demo services & resume',type='primary',disabled=exhausted,width='stretch'):
                try:
                    engine.clear_faults()
                    execute_with_audit(engine, USER, req['id'], run_audit)
                    st.rerun()
                except BoundaryError as exc:
                    st.error(str(exc))
            if st.button('Revoke further attempts',width='stretch'):
                engine.revoke(req['id'],USER)
                st.rerun()
        elif req['status'] in ['needs_new_plan','approval_revoked']:
            st.info('Start a fresh investigation and review a new plan before further changes.')
        elif complete:
            st.success('Every approved target is verified absent from the connected local stores.')
            if st.button('Replay an old search-index job',width='stretch'):
                rec = next(r for r in FIXTURE['records'] if r['id']=='V1')
                st.session_state['replay_result'] = engine.replay_ingestion(USER,rec)
            if st.session_state.get('replay_result'):
                replay = st.session_state['replay_result']
                if replay['result']=='blocked':
                    st.success('Re-ingestion blocked. V1 stays absent.')
                else:
                    st.info('V1 was outside this withdrawal scope and was inserted.')
            if st.button('Verify again',width='stretch'):
                run_audit(req['id'])
                st.rerun()
        if req.get('behavior_checks'):
            st.write('**Customer experience checks**')
            check_labels = {'consent:D1': 'Personalization consent withdrawn', 'surface:documents': 'Club Portal copies removed and reuse blocked',
                            'surface:search': 'Class personalization removed and reuse blocked',
                            'surface:personalization': 'Personalized offers removed and reuse blocked', 'preserved:B1': 'Paid class booking preserved'}
            for check in req['behavior_checks']:
                st.write(f"{'✓' if check['result']=='pass' else '…'} {check_labels.get(check['id'], check['id'])} — {check['result']}")
        if req.get('outcome_audit'):
            with st.expander('Outcome auditor findings', expanded=True):
                audit = req['outcome_audit']
                st.write(f"**{audit['verdict'].title()}** · {audit['explanation']}")
                for finding in audit.get('findings', []):
                    st.write(finding['explanation'])
        if req.get('audit_error'):
            st.warning('Model auditor unavailable. Deterministic verification is shown; the model audit remains unfinished.')
        st.download_button('Download verification receipt',json.dumps(req,indent=2),file_name=f'recall-{req["id"]}.json',mime='application/json',width='stretch')
        with st.expander('Execution timeline',expanded=req['status'] in ['partial','complete','interrupted']):
            events = ''.join(f'<div class="event"><small>{datetime.fromtimestamp(e["time"]).strftime("%H:%M:%S")} · {esc(e.get("record_id") or "request")}</small>{esc(e["message"])}</div>' for e in req['events'])
            st.markdown('<div class="timeline">'+events+'</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="receipt"><div class="receipt-title">Your control point</div><h3>Nothing leaves without your approval.</h3><p class="receipt-copy">The agent will inspect the trail and prepare an exact change for you to review. Reads happen autonomously; deletion waits here.</p><hr><p class="receipt-copy">Questionnaire → class preferences → queued offer<br>One request. A verifiable outcome.</p></div>',unsafe_allow_html=True)
    with st.expander('What stays untouched?'):
        for rid in ['B1','D2','V3']:
            item=engine.inspect_service(USER,rid)
            state_label = {'present': 'Still saved', 'absent': 'Not stored', 'unknown': 'Unable to verify'}[item['state']]
            st.write(f"**{item['title']}** · {labels.get(item['service'], item['service'])} · {state_label}")
        st.caption('Another synthetic user has matching text. User-scoped tools do not expose their records; automated tests verify they remain untouched.')

with st.expander('Agent goal and framework'):
    st.markdown((ROOT/'docs/FRAMEWORK.md').read_text())
st.markdown('<div class="footnote">Synthetic data · three local service stores · real local deletion and verification · no external deletion or model unlearning. Workflow metadata expires after 24 hours; lineage and withdrawal markers remain until explicit demo reset. A live investigation sends authorized metadata and your request to your selected model provider.</div>',unsafe_allow_html=True)
# Run the investigation only after the overview and evidence have rendered.
if submit:
    try:
        if mode=='Guided rehearsal':
            result = deterministic_rehearsal(engine, USER)
            st.session_state['needs_clarification'] = result['action'] != 'propose'
            st.session_state['agent_message'] = result['message']
        else:
            with investigation_progress, st.spinner('Still working · preparing your plan. No data is being deleted.', show_time=True), st.status('Investigating shared data…', expanded=True) as status:
                def progress(entry):
                    if 'role' in entry:
                        next_stage = {
                            'investigator': 'Checking scope and ownership…',
                            'hard_checks': 'Reviewing the proposed scope…',
                            'scope_reviewer': 'Waiting for the independent judge…',
                            'repair': 'Revising the plan after review…',
                            'evaluation_judge': 'Checking the review result…',
                        }.get(entry['role'])
                        if next_stage:
                            status.update(label=next_stage)
                        st.write(f"**{entry['role'].replace('_', ' ').title()}** · {entry.get('message', entry.get('result', ''))}")
                        return
                    label = {'discover_records':'Discovering records', 'trace_lineage':'Tracing dependencies', 'inspect_service':'Inspecting service state'}.get(entry['tool'], entry['tool'])
                    st.write(f"{label} · {', '.join(str(v) for v in entry['arguments'].values())}")
                result = review_plan(engine, clients, USER, request_text, on_event=progress)
                st.session_state['needs_clarification'] = result['action'] != 'propose'
                st.session_state['agent_message'] = result['message']
                st.session_state['agent_trace'] = result['trace']
                status.update(label='Plan ready for approval' if result['action']=='propose' else 'Preparation stopped · review the findings', state='complete' if result['action']=='propose' else 'error', expanded=result['action']!='propose')
    except (BoundaryError, ModelError) as exc:
        st.session_state['needs_clarification'] = True
        investigation_progress.error(str(exc))
    else:
        engine.close()
        st.rerun()

engine.close()
