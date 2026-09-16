"""Real local stores; simulated services. Model output never authorizes a write."""
from __future__ import annotations
import hashlib
import json
import sqlite3
import time
import uuid
from pathlib import Path


class BoundaryError(ValueError):
    pass


class Engine:
    def __init__(self, directory, services=None, require_review=False):
        self.services = services
        self.require_review = require_review or bool(services)
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.directory / 'workflow.sqlite')
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS catalog(id TEXT PRIMARY KEY, service TEXT, user_id TEXT, version INTEGER, kind TEXT, title TEXT);
        CREATE TABLE IF NOT EXISTS edges(source TEXT, target TEXT, evidence TEXT);
        CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY, user_id TEXT, payload TEXT, created REAL);
        CREATE TABLE IF NOT EXISTS suppression(record_id TEXT PRIMARY KEY, user_id TEXT, request_id TEXT);
        CREATE TABLE IF NOT EXISTS faults(service TEXT PRIMARY KEY, mode TEXT, remaining INTEGER);
        CREATE TABLE IF NOT EXISTS consent(user_id TEXT, root_id TEXT, state TEXT, granted REAL, withdrawn REAL, purpose TEXT, PRIMARY KEY(user_id, root_id));
        CREATE TABLE IF NOT EXISTS notifications(request_id TEXT, status TEXT, result TEXT, PRIMARY KEY(request_id,status));
        ''')
        self.db.commit()

    def close(self):
        self.db.close()

    def _service(self, name):
        if not name.replace('_', '').isalnum():
            raise BoundaryError('Invalid service name.')
        con = sqlite3.connect(self.directory / f'{name}.sqlite')
        con.row_factory = sqlite3.Row
        con.execute('CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, payload TEXT)')
        return con

    def seed(self, fixture):
        """Called only by an explicit fixture initialization/reset action."""
        names = {r['service'] for r in fixture['records']}
        names |= {r[0] for r in self.db.execute('SELECT DISTINCT service FROM catalog')}
        for name in names:
            if self.services:
                self.services.reset(name)
            else:
                with self._service(name) as con:
                    con.execute('DELETE FROM records')
        for table in ['catalog', 'edges', 'requests', 'suppression', 'faults', 'consent', 'notifications']:
            self.db.execute(f'DELETE FROM {table}')
        for r in fixture['records']:
            if self.services and r.get('consent_root'):
                continue
            if not self.services:
                with self._service(r['service']) as con:
                    con.execute('INSERT INTO records VALUES (?,?)', (r['id'], json.dumps(r)))
            self.db.execute('INSERT INTO catalog VALUES (?,?,?,?,?,?)',
                            (r['id'], r['service'], r['user_id'], r['version'], r['type'], r.get('title', r['id'])))
        for e in fixture['lineage']:
            if self.services and any(r.get('consent_root') for r in fixture['records'] if r['id'] == e['target']):
                continue
            self.db.execute('INSERT INTO edges VALUES (?,?,?)', (e['source'], e['target'], e['evidence_id']))
        self.db.commit()

    def consent_status(self, user, root='D1'):
        row = self.db.execute('SELECT * FROM consent WHERE user_id=? AND root_id=?', (user, root)).fetchone()
        return dict(row) if row else {'state': 'not_granted'}

    def grant_fitness_consent(self, user):
        if not self.services or user != 'U1':
            raise BoundaryError('Fitness consent requires the connected demo applications.')
        previous = self.consent_status(user)
        if previous['state'] == 'withdrawn':
            raise BoundaryError('This consent has been withdrawn. Reset the demo to start a new journey.')
        self.db.execute('INSERT OR IGNORE INTO consent VALUES (?,?,?,?,?,?)',
                        (user, 'D1', 'active', time.time(), None,
                         'Share fitness interests with Class Booking for recommendations and Member Offers for personalized promotions.'))
        self.db.commit()
        fixture = json.loads((Path(__file__).resolve().parents[1] / 'data/fitness.json').read_text())
        # Record intended provenance before sending a write: a lost response cannot hide a copy.
        # Presence is subsequently checked against the application's own store.
        for record in fixture['records']:
            if record.get('consent_root') != 'D1':
                continue
            self.db.execute('INSERT OR IGNORE INTO catalog VALUES (?,?,?,?,?,?)',
                            (record['id'], record['service'], user, record['version'], record['type'], record['title']))
            for edge in fixture['lineage']:
                if edge['target'] == record['id'] and not self.db.execute('SELECT 1 FROM edges WHERE source=? AND target=?',
                                                                         (edge['source'], edge['target'])).fetchone():
                    self.db.execute('INSERT INTO edges VALUES (?,?,?)',
                                    (edge['source'], edge['target'], 'SHARE-' + uuid.uuid4().hex[:12]))
            self.db.commit()
            self.services.ingest(record['service'], record['id'], user)
        return self.consent_status(user)

    def meta(self, rid, user):
        row = self.db.execute('SELECT * FROM catalog WHERE id=? AND user_id=?', (rid, user)).fetchone()
        if not row:
            raise BoundaryError('Record is not available within your authorized scope.')
        return dict(row)

    def set_fault(self, service, mode='offline', remaining=-1):
        self.db.execute('INSERT OR REPLACE INTO faults VALUES (?,?,?)', (service, mode, remaining))
        self.db.commit()

    def clear_faults(self):
        self.db.execute('DELETE FROM faults')
        self.db.commit()

    def _fault(self, service, operation):
        row = self.db.execute('SELECT * FROM faults WHERE service=?', (service,)).fetchone()
        if not row or row['remaining'] == 0 or (row['mode'] != 'offline' and operation != 'delete'):
            return None
        if row['remaining'] > 0:
            self.db.execute('UPDATE faults SET remaining=remaining-1 WHERE service=?', (service,))
            self.db.commit()
        return row['mode']

    def discover_records(self, user, query=''):
        rows = [dict(r) for r in self.db.execute('SELECT * FROM catalog WHERE user_id=? ORDER BY id', (user,))]
        return [r for r in rows if not query or query.casefold() in json.dumps(r).casefold()]

    def trace_lineage(self, user, root_id):
        self.meta(root_id, user)
        seen, edges, queue = set(), [], [root_id]
        while queue:
            rid = queue.pop(0)
            if rid in seen:
                continue
            self.meta(rid, user)
            seen.add(rid)
            for e in self.db.execute('SELECT * FROM edges WHERE source=?', (rid,)):
                self.meta(e['target'], user)
                edges.append(dict(e))
                queue.append(e['target'])
        shared = set()
        for rid in seen - {root_id}:
            for e in self.db.execute('SELECT * FROM edges WHERE target=?', (rid,)):
                if e['source'] not in seen:
                    shared.add(rid)
        return {'root': root_id, 'records': [self.meta(r, user) for r in sorted(seen)],
                'edges': edges, 'shared_dependencies': sorted(shared)}

    def inspect_service(self, user, record_id):
        meta = self.meta(record_id, user)
        if self._fault(meta['service'], 'read') == 'offline':
            return {**meta, 'state': 'unknown'}
        try:
            rec = self._read_record(meta['service'], record_id, user)
        except ConnectionError:
            return {**meta, 'state': 'unknown'}
        if rec:
            if rec['user_id'] != user:
                raise BoundaryError('Service identity mismatch.')
            return {**meta, 'version': rec['version'], 'state': 'present'}
        return {**meta, 'state': 'absent'}

    def _read_record(self, service, rid, user):
        if self.services:
            return self.services.read(service, rid, user)
        with self._service(service) as con:
            row = con.execute('SELECT payload FROM records WHERE id=?', (rid,)).fetchone()
        return json.loads(row[0]) if row else None

    def _delete_record(self, target, user):
        if self.services:
            return self.services.delete(target['service'], target['id'], user, target['version'])
        with self._service(target['service']) as con:
            con.execute('BEGIN IMMEDIATE')
            row = con.execute('SELECT payload FROM records WHERE id=?', (target['id'],)).fetchone()
            if row:
                rec = json.loads(row[0])
                if rec['version'] != target['version'] or rec['user_id'] != user:
                    return False
            con.execute('DELETE FROM records WHERE id=?', (target['id'],))
        return True

    def create_plan(self, user, roots, proposed_targets=None, origin='live_agent'):
        if not roots or len(set(roots)) != len(roots):
            raise BoundaryError('Select at least one distinct source.')
        records, edges = {}, []
        for root in roots:
            trail = self.trace_lineage(user, root)
            if trail['shared_dependencies']:
                raise BoundaryError('A derived record has another source. Human review is required; no deletion plan was created.')
            records.update({r['id']: r for r in trail['records']})
            edges.extend(trail['edges'])
        if proposed_targets is not None and set(proposed_targets) != set(records):
            raise BoundaryError('Proposed targets do not match the evidenced dependency scope.')
        targets = []
        for rid, rec in records.items():
            if rec['kind'] in {'paid_booking', 'class_listing'}:
                raise BoundaryError('Paid bookings and public class listings are protected from consent withdrawal.')
            actual = self.inspect_service(user, rid)
            targets.append({**rec, 'version': actual['version'], 'status': 'pending', 'attempts': 0,
                            'verification': 'not_checked', 'newly_deleted': False})
        req = {'id': uuid.uuid4().hex[:12], 'user_id': user, 'roots': sorted(roots),
               'targets': sorted(targets, key=lambda t: t['id']), 'edges': edges,
               'status': 'awaiting_approval', 'origin': origin, 'approval': None,
               'events': [], 'created': time.time(), 'retry_limit': 2,
               'scope': 'Withdraw the recorded consent for the selected sources, delete their explicitly linked descendants, and block their re-ingestion.',
               'review_required': self.require_review,
               'consent_roots': [root for root in roots if self.consent_status(user, root)['state'] != 'not_granted']}
        if self.require_review:
            req['status'] = 'under_review'
        self._order(req)  # Refuse unsupported cyclic graphs before approval.
        self.event(req, 'plan_ready', 'Preview prepared. No deletion has occurred.')
        self.save(req)
        return req

    @staticmethod
    def plan_hash(req):
        fields = {'user': req['user_id'], 'roots': req['roots'], 'scope': req['scope'],
                  'targets': [{k: t[k] for k in ['id', 'service', 'version']} for t in req['targets']],
                  'edges': req['edges'], 'retry_limit': req['retry_limit'], 'consent_roots': req.get('consent_roots', [])}
        return hashlib.sha256(json.dumps(fields, sort_keys=True).encode()).hexdigest()

    def save(self, req):
        self.db.execute('INSERT OR REPLACE INTO requests VALUES (?,?,?,?)',
                        (req['id'], req['user_id'], json.dumps(req), req['created']))
        self.db.commit()

    def get_request(self, request_id, user):
        row = self.db.execute('SELECT payload FROM requests WHERE id=? AND user_id=?', (request_id, user)).fetchone()
        if not row:
            raise BoundaryError('Request is not available.')
        return json.loads(row[0])

    def latest(self, user):
        row = self.db.execute('SELECT payload FROM requests WHERE user_id=? ORDER BY created DESC LIMIT 1', (user,)).fetchone()
        return json.loads(row[0]) if row else None

    def approve(self, request_id, user):
        req = self.get_request(request_id, user)
        if req['status'] != 'awaiting_approval':
            raise BoundaryError('Only a current preview can be approved.')
        if req.get('review_required'):
            gate = req.get('evaluation', {})
            if gate.get('verdict') != 'pass' or gate.get('plan_hash') != self.plan_hash(req):
                raise BoundaryError('The current plan must pass evaluation before approval.')
            from .review import hard_checks
            if hard_checks(self, req):
                raise BoundaryError('The evidence changed. Run the review again before approval.')
        req['approval'] = {'hash': self.plan_hash(req), 'at': time.time(), 'expires': time.time()+86400, 'active': True}
        req['status'] = 'approved'
        self.event(req, 'approved', 'Human approved these targets, withdrawal markers, and bounded retries.')
        self.save(req)
        return req

    def revoke(self, request_id, user):
        req = self.get_request(request_id, user)
        if req['approval']:
            req['approval']['active'] = False
        req['status'] = 'approval_revoked'
        self.event(req, 'revoked', 'Further attempts stopped. Completed deletions cannot be undone.')
        self.save(req)
        return req

    def check_approval(self, req):
        a = req['approval']
        if not a or not a['active'] or a['expires'] < time.time() or a['hash'] != self.plan_hash(req):
            raise BoundaryError('A valid human approval is required.')

    @staticmethod
    def event(req, kind, message, record_id=None):
        req['events'].append({'time': time.time(), 'kind': kind, 'record_id': record_id, 'message': message})

    def _order(self, req):
        remaining = {t['id']: t for t in req['targets']}
        result = []
        while remaining:
            leaves = sorted(r for r in remaining if not any(e['source'] == r and e['target'] in remaining for e in req['edges']))
            if not leaves:
                raise BoundaryError('Cyclic dependencies require human review.')
            for rid in leaves:
                result.append(remaining.pop(rid))
        return result

    def stale(self, req):
        req['approval'] = None
        req['status'] = 'needs_new_plan'
        self.event(req, 'scope_changed', 'Data changed. Investigate again and obtain fresh approval.')
        self.save(req)
        return req

    def delete_approved_records(self, request_id, user, stop_after=None):
        req = self.get_request(request_id, user)
        self.check_approval(req)
        current, edges = set(), []
        for root in req['roots']:
            trail = self.trace_lineage(user, root)
            current.update(r['id'] for r in trail['records'])
            edges.extend(trail['edges'])
            if trail['shared_dependencies']:
                return self.stale(req)
        if current != {t['id'] for t in req['targets']} or sorted(edges, key=str) != sorted(req['edges'], key=str):
            return self.stale(req)
        for target in req['targets']:
            actual = self.inspect_service(user, target['id'])
            if actual['state'] == 'present' and actual['version'] != target['version']:
                return self.stale(req)
        ordered = self._order(req)
        for root in req['roots']:
            self.db.execute("UPDATE consent SET state='withdrawn', withdrawn=? WHERE user_id=? AND root_id=?",
                            (time.time(), user, root))
        for target in req['targets']:
            self.db.execute('INSERT OR IGNORE INTO suppression VALUES (?,?,?)', (target['id'], user, request_id))
        self.db.commit()
        req['status'] = 'executing'
        self.save(req)
        if self.services:
            for service in sorted({t['service'] for t in req['targets']}):
                self.check_approval(self.get_request(request_id, user))
                try:
                    if self._fault(service, 'read') == 'offline':
                        raise ConnectionError()
                    self.services.block(service, user, [t['id'] for t in req['targets'] if t['service'] == service])
                except ConnectionError:
                    self.event(req, 'unavailable', f'{service}: withdrawal blocks could not yet be confirmed.')
            self.save(req)
        completed = 0
        for target in ordered:
            self.check_approval(self.get_request(request_id, user))
            actual = self.inspect_service(user, target['id'])
            if actual['state'] == 'absent':
                target.update(status='verified_absent', verification='absent')
                self.event(req, 'verified', 'Read confirms absence; no new delete needed.', target['id'])
                self.save(req)
                continue
            target['status'] = 'pending'
            while target['attempts'] < 3:
                if actual['state'] == 'unknown':
                    self.event(req, 'unavailable', 'Service unavailable; verification is unknown.', target['id'])
                    break
                self.check_approval(self.get_request(request_id, user))
                target['attempts'] += 1
                self.event(req, 'delete_attempt', 'Execute approved deletion.', target['id'])
                self.save(req)
                fault = self._fault(target['service'], 'delete')
                if fault in ['offline', 'fail_before_commit']:
                    self.event(req, 'retry', 'Attempt failed before commit.', target['id'])
                else:
                    try:
                        if not self._delete_record(target, user):
                            return self.stale(req)
                    except ConnectionError:
                        fault = 'commit_then_timeout'
                    if fault == 'commit_then_timeout':
                        self.event(req, 'uncertain', 'Response lost; inspect before any retry.', target['id'])
                    else:
                        target['newly_deleted'] = True
                actual = self.inspect_service(user, target['id'])
                if actual['state'] == 'absent':
                    target.update(status='verified_absent', verification='absent')
                    self.event(req, 'verified', 'Independent read confirms absence.', target['id'])
                    completed += 1
                    break
            if target['status'] != 'verified_absent':
                target.update(status='unresolved', verification=actual['state'])
            self.save(req)
            if stop_after and completed >= stop_after:
                req['status'] = 'interrupted'
                self.event(req, 'interrupted', 'Worker stopped. Resume from persistent state.')
                self.save(req)
                return req
        return self.verify_withdrawal(request_id, user)

    def verify_withdrawal(self, request_id, user):
        req = self.get_request(request_id, user)
        for t in req['targets']:
            actual = self.inspect_service(user, t['id'])
            t['verification'] = actual['state']
            t['status'] = 'verified_absent' if actual['state'] == 'absent' else 'unresolved'
        if req['approval']:
            req['status'] = 'complete' if all(t['verification'] == 'absent' for t in req['targets']) else 'partial'
            if self.services:
                checks = self.behavior_checks(user, req)
                req['behavior_checks'] = checks
                if any(c['result'] != 'pass' for c in checks):
                    req['status'] = 'partial'
        req['full_withdrawal_complete'] = req['status'] == 'complete'
        self.event(req, 'verification', f"Verification result: {req['status']}.")
        self.save(req)
        return req

    def behavior_checks(self, user, req):
        results = []
        for root in req.get('consent_roots', []):
            results.append({'id': 'consent:' + root, 'result': 'pass' if self.consent_status(user, root)['state'] == 'withdrawn' else 'fail',
                            'detail': 'Recorded sharing consent is withdrawn.'})
        for service in sorted({t['service'] for t in req['targets']}):
            try:
                if self._fault(service, 'read') == 'offline':
                    raise ConnectionError()
                snapshot = self.services.behavior(service, user)
                ids = {t['id'] for t in req['targets'] if t['service'] == service}
                remaining = sorted(ids & set(snapshot['active_ids']))
                unblocked = sorted(ids - set(snapshot['blocked_ids']))
                # Detect downstream records added since approval without authorizing new writes.
                unexpected = sorted(set(snapshot['consent_ids']) - ids) if 'D1' in req.get('consent_roots', []) else []
                results.append({'id': 'surface:' + service, 'result': 'fail' if remaining or unblocked or unexpected else 'pass',
                                'detail': {'remaining': remaining, 'unblocked': unblocked, 'unexpected': unexpected,
                                           'visible_ids': snapshot['visible_ids']}})
                if service == 'search':
                    results.append({'id': 'preserved:B1', 'result': 'pass' if 'B1' in snapshot['active_ids'] else 'fail',
                                    'detail': 'Paid booking remains available.'})
            except ConnectionError:
                results.append({'id': 'surface:' + service, 'result': 'unknown', 'detail': 'Application unavailable.'})
        return results

    def replay_ingestion(self, user, record):
        """Explicit synthetic ingestion probe. The source uses stable record IDs."""
        meta = self.meta(record['id'], user)
        if record['user_id'] != user or meta['service'] != record['service']:
            raise BoundaryError('Identity or service mismatch.')
        blocked = self.db.execute('SELECT 1 FROM suppression WHERE record_id=? AND user_id=?', (record['id'], user)).fetchone()
        if blocked:
            return {'record_id': record['id'], 'result': 'blocked', 'reason': 'Approved withdrawal marker'}
        if self.services:
            return self.services.replay(record['service'], record['id'], user)
        with self._service(record['service']) as con:
            con.execute('INSERT OR REPLACE INTO records VALUES (?,?)', (record['id'], json.dumps(record)))
        return {'record_id': record['id'], 'result': 'inserted'}

    def search(self, user, query):
        """Real lexical retrieval over active synthetic records; no claimed vector search."""
        results = []
        for meta in self.discover_records(user):
            if self.inspect_service(user, meta['id'])['state'] != 'present':
                continue
            try:
                rec = self._read_record(meta['service'], meta['id'], user)
            except ConnectionError:
                continue
            if rec:
                if query.casefold() in rec['content'].casefold():
                    results.append({'id': rec['id'], 'service': rec['service'], 'text': rec['content']})
        return results

    def purge_expired_requests(self):
        self.db.execute('DELETE FROM requests WHERE created < ?', (time.time()-86400,))
        self.db.commit()
