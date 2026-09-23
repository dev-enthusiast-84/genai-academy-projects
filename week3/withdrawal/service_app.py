"""Minimal scoped applications. Each process owns one database and HTTP port."""
import argparse
import hmac
import html
import json
import os
import secrets
import sqlite3
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

from ui.identity import app_identity, persona, identity_css
from .services import PORTS, configured_services
from .core import Engine, BoundaryError

ROOT = Path(__file__).resolve().parents[1]
HIDDEN = {'extracted_text', 'derived_preference', 'copied_preference', 'audience_membership'}
APPS = {
    'documents': ('Club Portal', 'Your club. Your choices.', 'Manage your membership and choose how your fitness interests are used.', '#2359d1'),
    'search': ('Class Booking', 'Make time to move.', 'Your booked classes and suggestions based on your interests.', '#087d75'),
    'personalization': ('Member Offers', 'A little extra motivation.', 'Preview the personalized invitations prepared for you.', '#8444a5'),
}


class Store:
    def __init__(self, directory, service):
        Path(directory).mkdir(parents=True, exist_ok=True)
        self.path = Path(directory) / (service + '.sqlite')
        self.service = service
        fixture = json.loads((ROOT / 'data/fitness.json').read_text())
        self.fixture = {r['id']: r for r in fixture['records'] if r['service'] == service}
        with self.connect() as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, payload TEXT);
            CREATE TABLE IF NOT EXISTS blocked(id TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS sharing(id TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS initialized(value INTEGER);''')
            if not db.execute('SELECT 1 FROM initialized').fetchone():
                self.seed(db)

    def connect(self):
        return sqlite3.connect(self.path)

    def seed(self, db):
        db.execute('DELETE FROM records')
        db.execute('DELETE FROM blocked')
        db.execute('DELETE FROM sharing')
        db.executemany('INSERT INTO records VALUES (?,?)', [(r['id'], json.dumps(r)) for r in self.fixture.values()
                                                          if not r.get('consent_root')])
        db.execute('DELETE FROM initialized')
        db.execute('INSERT INTO initialized VALUES (1)')

    def operate(self, operation, data):
        if operation == 'delete_profile':
            if self.service != 'documents' or data.get('user') != 'U1':
                return 403, {'error': 'Record outside authorized scope.'}
            self.delete_visible_profile()
            return 200, {'deleted': 'D1'}
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if operation == 'reset':
                self.seed(db)
                return 200, {'reset': True}
            if operation in ('behavior', 'block'):
                user = data.get('user')
                if user != 'U1':
                    return 403, {'error': 'Record outside authorized scope.'}
                if operation == 'block':
                    ids = data.get('ids')
                    if not isinstance(ids, list) or not all(isinstance(rid, str) and rid in self.fixture
                            and self.fixture[rid]['user_id'] == user and self.fixture[rid].get('consent_root') for rid in ids):
                        return 403, {'error': 'Only consent-linked records may be blocked.'}
                    db.executemany('INSERT OR IGNORE INTO blocked VALUES (?)', [(rid,) for rid in ids])
                records = [json.loads(r[0]) for r in db.execute('SELECT payload FROM records ORDER BY id')]
                records = [r for r in records if r['user_id'] == user]
                blocked = [r[0] for r in db.execute('SELECT id FROM blocked ORDER BY id')
                           if self.fixture[r[0]]['user_id'] == user]
                return 200, {'active_ids': [r['id'] for r in records], 'blocked_ids': blocked,
                             'consent_ids': [r['id'] for r in records if r.get('consent_root')],
                             'visible_ids': [r['id'] for r in records if r['type'] not in HIDDEN]}
            rid, user = data.get('id'), data.get('user')
            original = self.fixture.get(rid)
            if not original or original['user_id'] != user:
                return 403, {'error': 'Record outside authorized scope.'}
            row = db.execute('SELECT payload FROM records WHERE id=?', (rid,)).fetchone()
            record = json.loads(row[0]) if row else None
            if record and record['user_id'] != user:
                return 403, {'error': 'Identity mismatch.'}
            if operation == 'read':
                return 200, {'record': record}
            if operation == 'delete':
                if rid == 'B1':
                    return 403, {'error': 'Paid bookings are protected from consent withdrawal.'}
                if record and record['version'] != data.get('version'):
                    return 409, {'changed': True}
                db.execute('INSERT OR IGNORE INTO blocked VALUES (?)', (rid,))
                db.execute('DELETE FROM records WHERE id=?', (rid,))
                return 200, {'deleted': rid}
            if operation in ('share', 'replay'):
                blocked = db.execute('SELECT 1 FROM blocked WHERE id=?', (rid,)).fetchone()
                permitted = db.execute('SELECT 1 FROM sharing WHERE id=?', (rid,)).fetchone()
                if operation == 'share' and not blocked:
                    db.execute('INSERT OR IGNORE INTO sharing VALUES (?)', (rid,))
                    permitted = True
                if not permitted:
                    blocked = True
                if not blocked:
                    db.execute('INSERT OR REPLACE INTO records VALUES (?,?)', (rid, json.dumps(original)))
                return 200, {'record_id': rid, 'result': 'blocked' if blocked else 'inserted'}
            return 404, {'error': 'Unknown operation.'}

    def delete_visible_profile(self):
        # This customer action removes the source only; no cascade or consent revocation.
        with self.connect() as db:
            db.execute("DELETE FROM records WHERE id='D1'")

    def visible(self, query=''):
        with self.connect() as db:
            records = [json.loads(r[0]) for r in db.execute('SELECT payload FROM records ORDER BY id')]
        return [r for r in records if r['user_id'] == 'U1' and r['type'] not in HIDDEN
                and query.casefold() in (r['title'] + ' ' + r['content']).casefold()]


def page(store, query, csrf='', consent=None, notice=''):
    name, heading, description, accent = APPS[store.service]
    esc = html.escape
    records = store.visible(query)
    # A repeated same-document anchor navigation does not fetch updated records.
    # Give each rendered refresh link a new URL, preserving the search filter.
    refresh_url = '/?' + esc(urlencode({'q': query, 'refresh': '1',
                                      'refresh_id': secrets.token_urlsafe(12)}), quote=True) + '#refresh-status'
    dashboard = html.escape(os.environ.get('RECALL_DASHBOARD_URL', 'http://127.0.0.1:8501'), quote=True)
    app_urls = {key: f'http://127.0.0.1:{port}' for key, port in PORTS.items()}
    app_urls.update(json.loads(os.environ.get('RECALL_SERVICE_URLS', '{}')))
    club_url = esc(app_urls['documents'], quote=True)
    cards = ''.join(f'<article class="{esc(r["type"])}"><small>{esc(r["type"].replace("_", " "))}</small>'
                    f'<h2>{esc(r["title"])}</h2><p>{esc(r["content"])}</p></article>' for r in records)
    form = (f'<form><label for="q">Search your saved copies</label><div class="search">'
            f'<input id="q" name="q" value="{esc(query, quote=True)}" placeholder="Try yoga">'
            '<button>Search</button></div></form>') if store.service == 'search' else ''
    if store.service == 'documents':
        state = (consent or {}).get('state', 'not_granted')
        if state == 'not_granted':
            form = f'''<article class="action-panel"><small>WHAT YOU CAN DO HERE</small><h2>1. Give consent &amp; share interests</h2>
            <p>Your fitness interests: evening yoga, after 6 pm.</p>
            <form method="post" action="/consent"><input type="hidden" name="csrf" value="{csrf}">
            <p><label><input type="checkbox" name="agree" required> I consent to share this profile with Class Booking
            for class recommendations and Member Offers for personalized promotions.</label></p>
            <p><button>Give consent &amp; share interests</button></p></form></article>'''
        elif state == 'active':
            source_present = any(record['id'] == 'D1' for record in store.visible())
            title = 'Sharing consent active' if source_present else 'Questionnaire removed · consent still active'
            form = f'''<article class="action-panel"><small>YOUR QUESTIONNAIRE · THIS APP ONLY</small><h2>{title}</h2><p>You agreed to share your profile with Class Booking and Member Offers.</p>
            {'' if source_present else '<p>Deleting the questionnaire did not withdraw sharing consent. Downstream copies may remain until Recall completes withdrawal.</p>'}
            <form method="post" action="/delete-profile"><input type="hidden" name="csrf" value="{csrf}">
            <p><button {'' if source_present else 'disabled'}>Delete questionnaire only</button></p></form>
            <p>This removes your saved profile here. To withdraw sharing consent and remove linked information across apps,
            open Recall and approve a withdrawal.</p>
            <p><a class="action-button" href="{dashboard}" target="_blank" rel="noopener">Withdraw across all apps in Recall ↗</a></p></article>'''
        else:
            form = '<article><h2>Sharing consent withdrawn</h2><p>Your profile will no longer be shared. Check Recall for the removal and verification status of each connected app.</p></article>'
    if store.service == 'personalization':
        form = '<p class=preview>Message preview · Nothing is sent from this demo.</p>'
    dashboard = html.escape(os.environ.get('RECALL_DASHBOARD_URL', 'http://127.0.0.1:8501'), quote=True)
    if store.service != 'documents':
        purpose = ('Search your saved information and view class suggestions. Your paid booking stays protected.'
                   if store.service == 'search' else 'View your personalized invitation. This is a preview; no message is sent.')
        snapshot = store.operate('behavior', {'user': 'U1'})[1]
        count = len(snapshot['consent_ids'])
        sharing_status = f'{count} shared or derived records remain in this app.' if count else 'No shared personalization records are stored here.'
        form = f'''<article class="action-panel"><small>WHAT YOU CAN DO HERE</small><h2>{'Your classes & suggestions' if store.service == 'search' else 'Your offer preview'}</h2>
        <p>{purpose}</p><p><strong>{sharing_status}</strong></p>
        <p>Deleting the questionnaire in Club Portal does not remove copies here. Use Recall to request removal across all apps.</p>
        <div class="action-links"><a class="action-button" href="{refresh_url}">Refresh this app</a><a class="action-button secondary" href="{dashboard}" target="_blank" rel="noopener">Withdraw via Recall ↗</a></div>
        <p><a href="{club_url}" target="_blank" rel="noopener">Give consent in Club Portal ↗</a></p></article>''' + form
    app_links = '<div class="action-links">' + ''.join(
        f'<a href="{esc(app_urls[key], quote=True)}" target="_blank" rel="noopener">{app_identity(key)} ↗</a>'
        for key in PORTS if key != store.service) + '</div>'
    brand_panel = {
        'documents': '<section class=member-card><small>CLUB MEMBERSHIP / 2026</small><strong>Avery Example</strong><span>Member preferences &amp; privacy</span></section>',
        'search': '<section class=week aria-label="Weekly class calendar"><span>MON<strong>14</strong></span><span>TUE<strong>15</strong></span><span>WED<strong>16</strong></span><span>THU<strong>17</strong></span><span>FRI<strong>18</strong></span><span class=selected>SAT<strong>19</strong></span></section>',
        'personalization': '<section class=offers-banner><small>THE MEMBER COLLECTION</small><strong>Something selected for you.</strong><span>Personal invitations, on your terms.</span></section>',
    }[store.service]
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{name} · Recall demo</title><style>
    {(ROOT / 'ui/customer.css').read_text()}
    {identity_css()}
    </style><body class="{store.service}"><main><nav><strong>{app_identity(store.service)}</strong><a href="{dashboard}" target="_blank" rel="noopener">Open Recall ↗</a></nav>
    {persona()}<header><small>AVERY EXAMPLE · SYNTHETIC DEMO</small><h1>{heading}</h1><p>{description}</p></header>
    {'<p id="refresh-status" role="status">' + esc(notice) + '</p>' if notice else ''}{form}{app_links}{brand_panel}<div class="count">{len(records)} visible items · <a href="{refresh_url}">Refresh</a></div>
    {cards or '<article><h2>Nothing to show yet</h2><p>Save your interests in Club Portal to see personalized suggestions here. After withdrawal, these suggestions disappear.</p></article>'}
    <footer>Local actions affect this app only. Recall investigates, requests your approval, and verifies withdrawal across all three apps.</footer></main></body></html>'''


def make_server(store, token, port):
    csrf = secrets.token_urlsafe(32)

    def workflow():
        return Engine(os.environ.get('RECALL_DATA_DIR', str(ROOT / '.runtime' / 'connected')), configured_services())

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, status, body, content_type='application/json'):
            body = body.encode() if isinstance(body, str) else json.dumps(body).encode()
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'none'; img-src data:; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == '/health':
                return self.respond(200, {'service': store.service})
            if parsed.path != '/':
                return self.respond(404, {'error': 'Not found'})
            params = parse_qs(parsed.query)
            query = params.get('q', [''])[0]
            notice = ('Refreshed at ' + datetime.now().astimezone().strftime('%H:%M:%S %Z')
                      + '. Showing the latest saved information from this app.'
                      if params.get('refresh') == ['1'] else '')
            consent = None
            if store.service == 'documents':
                engine = workflow()
                try:
                    consent = engine.consent_status('U1')
                finally:
                    engine.close()
            self.respond(200, page(store, query, csrf, consent, notice), 'text/html; charset=utf-8')

        def do_POST(self):
            if self.path in ('/consent', '/delete-profile') and store.service == 'documents':
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                    if length < 0 or length > 4096:
                        raise ValueError()
                    form = parse_qs(self.rfile.read(length).decode())
                    if not hmac.compare_digest(form.get('csrf', [''])[0], csrf):
                        return self.respond(403, {'error': 'Reload the page before submitting.'})
                    engine = workflow()
                    try:
                        if self.path == '/consent':
                            if form.get('agree') != ['on']:
                                raise BoundaryError('Consent must be selected before sharing.')
                            engine.grant_fitness_consent('U1')
                            notice = 'Profile saved. Your consented preferences have been shared with Class Booking and Member Offers.'
                        else:
                            store.delete_visible_profile()
                            notice = 'Your profile was deleted from Club Portal. Sharing consent is still active.'
                        self.respond(200, page(store, '', csrf, engine.consent_status('U1'), notice), 'text/html; charset=utf-8')
                    finally:
                        engine.close()
                except (ValueError, ConnectionError) as exc:
                    self.respond(400, {'error': str(exc) or 'Invalid form. If sharing was interrupted, restore the apps and retry.'})
                return
            if not hmac.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + token):
                return self.respond(401, {'error': 'Service authentication required.'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if length < 0 or length > 4096:
                    raise ValueError()
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict) or not self.path.startswith('/api/'):
                    raise ValueError()
                status, result = store.operate(self.path.removeprefix('/api/'), data)
                self.respond(status, result)
            except (ValueError, TypeError):
                self.respond(400, {'error': 'Invalid request.'})
    return ThreadingHTTPServer(('127.0.0.1', port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('service', choices=PORTS)
    parser.add_argument('--directory', default=str(ROOT / '.runtime' / 'applications'))
    args = parser.parse_args()
    token = os.environ.get('RECALL_SERVICE_TOKEN')
    if not token:
        parser.error('RECALL_SERVICE_TOKEN is required.')
    server = make_server(Store(args.directory, args.service), token, PORTS[args.service])
    print(f'{APPS[args.service][0]}: http://127.0.0.1:{PORTS[args.service]} (PID {os.getpid()})', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
