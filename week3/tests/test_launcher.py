"""Launcher orchestration without binding fixed demo ports or starting model clients."""
import run_demo


def test_launcher_preserves_state_and_cleans_owned_processes(tmp_path, monkeypatch):
    processes = []
    class Process:
        pid = 123
        def __init__(self, command, **kwargs):
            self.command, self.env = command, kwargs['env']
            self.stopped = False
            processes.append(self)
        def poll(self):
            return 0 if self.stopped else None
        def terminate(self):
            self.stopped = True
        def wait(self, timeout=None):
            return 0
    class Response:
        status_code = 200
        def __init__(self, url):
            self.url = url
        def json(self):
            return {'service': next(name for name, port in run_demo.PORTS.items() if f':{port}' in self.url)}
    class Client:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def get(self, url): return Response(url)
    seeded = []
    class Database:
        def execute(self, query): return self
        def fetchone(self): return None
    class Engine:
        db = Database()
        def __init__(self, *args): pass
        def seed(self, fixture): seeded.append(fixture)
        def close(self): pass
    monkeypatch.setattr(run_demo.subprocess, 'Popen', Process)
    monkeypatch.setattr(run_demo.httpx, 'Client', Client)
    monkeypatch.setattr(run_demo, 'Engine', Engine)
    monkeypatch.setattr(run_demo, 'available', lambda port: None)
    monkeypatch.setattr(run_demo.time, 'sleep', lambda value: (_ for _ in ()).throw(KeyboardInterrupt()))
    monkeypatch.setattr(run_demo.sys, 'argv', ['run_demo.py', '--directory', str(tmp_path)])
    monkeypatch.setenv('RECALL_TOOL_TRANSPORT', 'http')
    assert run_demo.main() == 0
    assert len(processes) == 4
    assert all(process.stopped for process in processes)
    assert seeded[0]['records'][0]['title'] == 'Fitness interests questionnaire'
    assert processes[-1].env['RECALL_DATA_DIR'] == str(tmp_path / 'recall')


def test_launcher_http_process_smoke(tmp_path):
    import os
    import signal
    import subprocess
    import sys
    import time
    import httpx
    import pytest
    for port in [*run_demo.PORTS.values(), 8501]:
        try:
            run_demo.available(port)
        except (OSError, RuntimeError):
            pytest.skip('Demo ports occupied; launcher unit coverage still runs.')
    env = dict(os.environ, RECALL_TOOL_TRANSPORT='http', NOTIFICATION_ENABLED='false')
    process = subprocess.Popen([sys.executable, 'run_demo.py', '--directory', str(tmp_path)],
                               cwd=run_demo.ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True)
    try:
        deadline = time.monotonic() + 20
        with httpx.Client(trust_env=False, timeout=.5) as client:
            while True:
                assert process.poll() is None, process.stdout.read()
                try:
                    response = client.get('http://127.0.0.1:8501/_stcore/health')
                    if response.status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                assert time.monotonic() < deadline, 'Dashboard failed to become ready'
                time.sleep(.1)
            for port in run_demo.PORTS.values():
                assert client.get(f'http://127.0.0.1:{port}/health').status_code == 200
            assert 'Club Portal' in client.get('http://127.0.0.1:8101').text
    finally:
        process.send_signal(signal.SIGINT)
        process.communicate(timeout=15)
    assert process.returncode == 0
