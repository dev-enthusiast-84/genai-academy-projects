"""Optional, fixed-destination status tool. Never accepts model-authored messages."""
import os
from pathlib import Path
from urllib.parse import urlparse

import httpx


def notification_settings(path='.env'):
    values = {}
    if Path(path).exists():
        for line in Path(path).read_text().splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                values[key.strip()] = value.strip().strip('\"\'')
    keys = ['NOTIFICATION_ENABLED', 'NOTIFICATION_PROVIDER', 'NOTIFICATION_WEBHOOK_URL',
            'NOTIFICATION_EVENTS', 'NOTIFICATION_TIMEOUT_SECONDS']
    for key in keys:
        if key in os.environ:
            values[key] = os.environ[key]
    try:
        timeout = min(15, max(1, float(values.get('NOTIFICATION_TIMEOUT_SECONDS', '5'))))
    except ValueError:
        timeout = 5
    return {'enabled': values.get('NOTIFICATION_ENABLED', 'false').lower() == 'true',
            'provider': values.get('NOTIFICATION_PROVIDER', 'slack'),
            'url': values.get('NOTIFICATION_WEBHOOK_URL', ''), 'timeout': timeout,
            'events': {v.strip() for v in values.get('NOTIFICATION_EVENTS', 'awaiting_approval,review_blocked,partial,complete').split(',')}}


def notify_withdrawal_status(engine, user, request_id, config, transport=None):
    req = engine.get_request(request_id, user)
    status = 'review_blocked' if req['status'] == 'blocked' else req['status']
    if not config['enabled'] or status not in config['events']:
        return {'result': 'disabled_or_unnecessary'}
    try:
        parsed = urlparse(config['url'])
        port = parsed.port
    except ValueError:
        return {'result': 'configuration_required'}
    if (config['provider'] != 'slack' or parsed.scheme != 'https' or parsed.hostname != 'hooks.slack.com'
            or not parsed.path.startswith('/services/') or parsed.username or parsed.password
            or parsed.query or parsed.fragment or port not in (None, 443)):
        return {'result': 'configuration_required'}
    # Claim before I/O so refresh/restart cannot silently send duplicate notifications.
    # An ambiguous network response is retained as unknown; it is not automatically retried.
    engine.db.execute('CREATE TABLE IF NOT EXISTS notifications(request_id TEXT, status TEXT, result TEXT, PRIMARY KEY(request_id,status))')
    inserted = engine.db.execute('INSERT OR IGNORE INTO notifications VALUES (?,?,?)', (request_id, status, 'unknown')).rowcount
    engine.db.commit()
    if not inserted:
        return {'result': 'already_attempted'}
    labels = {'awaiting_approval': 'A reviewed withdrawal is ready for your approval.',
              'review_blocked': 'A withdrawal needs clarification before approval.',
              'partial': 'A withdrawal is incomplete and needs attention.',
              'complete': 'Approved withdrawal targets and configured checks are verified.'}
    if status not in labels:
        return {'result': 'unnecessary'}
    result = 'unknown'
    try:
        with httpx.Client(timeout=config['timeout'], follow_redirects=False, trust_env=False, transport=transport) as client:
            response = client.post(config['url'], json={'text': f"Recall · {request_id}\n{labels[status]}"})
            result = 'sent' if response.status_code == 200 and response.text.strip() == 'ok' else 'rejected'
    except httpx.HTTPError:
        pass
    engine.db.execute('UPDATE notifications SET result=? WHERE request_id=? AND status=?', (result, request_id, status))
    engine.db.commit()
    req = engine.get_request(request_id, user)
    engine.event(req, 'notify_withdrawal_status', f'Slack status notification: {result}.')
    engine.save(req)
    return {'result': result}
