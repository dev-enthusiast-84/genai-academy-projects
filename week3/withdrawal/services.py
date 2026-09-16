"""HTTP adapters for the three independently running local applications."""
import json
import os

import httpx

from .core import BoundaryError

PORTS = {'documents': 8101, 'search': 8102, 'personalization': 8103}


class HttpServices:
    def __init__(self, urls, token):
        if set(urls) != set(PORTS) or not token:
            raise BoundaryError('Configure all three applications and a local service token.')
        self.urls, self.token = urls, token

    def call(self, service, operation, **payload):
        try:
            response = httpx.post(self.urls[service] + '/api/' + operation,
                                  json=payload, headers={'Authorization': 'Bearer ' + self.token},
                                  timeout=3, trust_env=False)
            if response.status_code == 409:
                return {'changed': True}
            if response.status_code >= 500:
                raise ConnectionError('Application unavailable.')
            if response.status_code != 200:
                raise BoundaryError('Application rejected the scoped service request.')
            return response.json()
        except BoundaryError:
            raise
        except (httpx.HTTPError, ValueError) as exc:
            raise ConnectionError('Application unavailable or returned an invalid response.') from exc

    def reset(self, service):
        self.call(service, 'reset')

    def read(self, service, rid, user):
        return self.call(service, 'read', id=rid, user=user)['record']

    def delete(self, service, rid, user, version):
        return not self.call(service, 'delete', id=rid, user=user, version=version).get('changed')

    def block(self, service, user, ids):
        return self.call(service, 'block', user=user, ids=ids)

    def behavior(self, service, user):
        return self.call(service, 'behavior', user=user)

    def replay(self, service, rid, user):
        return self.call(service, 'replay', id=rid, user=user)

    def ingest(self, service, rid, user):
        result = self.call(service, 'share', id=rid, user=user)
        if result['result'] == 'blocked':
            raise BoundaryError('Withdrawn information cannot be shared again.')


def configured_services():
    value = os.environ.get('RECALL_SERVICE_URLS')
    return HttpServices(json.loads(value), os.environ.get('RECALL_SERVICE_TOKEN', '')) if value else None
