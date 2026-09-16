"""Launch Recall and three local fitness applications: python run_demo.py."""
import argparse
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time

import httpx

from withdrawal.core import Engine
from withdrawal.services import HttpServices, PORTS

ROOT = Path(__file__).resolve().parent


def available(port):
    """Check if port is available, retry a few times."""
    for attempt in range(5):
        try:
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', port))
            return
        except OSError:
            if attempt < 4:
                time.sleep(0.2)
            else:
                raise RuntimeError(f'Port {port} is still in use after retries')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=ROOT / '.runtime' / 'fitness')
    parser.add_argument('--reset', action='store_true', help='Explicitly reset all synthetic demo data.')
    parser.add_argument('--mcp', action='store_true', help='Start the optional MCP read-tool server.')
    parser.add_argument('--dashboard-port', type=int, default=8501, help='Recall port; use 8502 to coexist with an existing Streamlit app.')
    args = parser.parse_args()
    args.directory = args.directory.resolve()
    args.directory.mkdir(parents=True, exist_ok=True)
    token = secrets.token_urlsafe(32)
    file_env = {}
    dotenv = ROOT / '.env'
    if dotenv.exists():
        for line in dotenv.read_text().splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                file_env[key.strip()] = value.strip().strip('"').strip("'")
    env = dict(file_env, **os.environ)
    urls = {name: f'http://127.0.0.1:{port}' for name, port in PORTS.items()}
    env.update(RECALL_SERVICE_URLS=json.dumps(urls), RECALL_SERVICE_TOKEN=token,
               RECALL_DASHBOARD_URL=f'http://127.0.0.1:{args.dashboard_port}',
               RECALL_DATA_DIR=str(args.directory / 'recall'))
    use_mcp = args.mcp or env.get('RECALL_TOOL_TRANSPORT') == 'mcp'
    mcp_port = int(env.get('RECALL_MCP_PORT', '8104'))
    if use_mcp:
        env.update(RECALL_TOOL_TRANSPORT='mcp', RECALL_MCP_PORT=str(mcp_port),
                   RECALL_MCP_URL=env.get('RECALL_MCP_URL', f'http://127.0.0.1:{mcp_port}/mcp'))
    children = []
    try:
        for port in [*PORTS.values(), args.dashboard_port, *([mcp_port] if use_mcp else [])]:
            available(port)
        for service in PORTS:
            children.append(subprocess.Popen([sys.executable, '-m', 'withdrawal.service_app', service, '--directory', str(args.directory / 'applications')], cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        deadline = time.monotonic() + 20
        pending = set(PORTS)
        with httpx.Client(trust_env=False, timeout=.5) as client:
            while pending:
                if any(child.poll() is not None for child in children):
                    raise RuntimeError('A customer application exited during startup.')
                for service in list(pending):
                    try:
                        response = client.get(urls[service] + '/health')
                        if response.status_code == 200 and response.json().get('service') == service:
                            pending.remove(service)
                    except (httpx.HTTPError, ValueError):
                        pass
                if time.monotonic() > deadline:
                    raise RuntimeError('Applications did not become ready: ' + ', '.join(sorted(pending)))
                if pending:
                    time.sleep(.1)
        engine = Engine(args.directory / 'recall', HttpServices(urls, token))
        try:
            if args.reset or not engine.db.execute('SELECT 1 FROM catalog').fetchone():
                engine.seed(json.loads((ROOT / 'site/fitness.json').read_text()))
        finally:
            engine.close()
        if use_mcp:
            mcp_process = subprocess.Popen([sys.executable, '-m', 'withdrawal.mcp_server'], cwd=ROOT, env=env)
            children.append(mcp_process)
            deadline = time.monotonic() + 20
            while True:
                if mcp_process.poll() is not None:
                    raise RuntimeError('MCP server failed to start. Install requirements-mcp.txt or select HTTP transport.')
                try:
                    with socket.create_connection(('127.0.0.1', mcp_port), timeout=.2):
                        break
                except OSError:
                    if time.monotonic() > deadline:
                        raise RuntimeError('MCP server did not become ready.')
                    time.sleep(.1)
        children.append(subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'app.py',
                        '--server.address', '127.0.0.1', '--server.port', str(args.dashboard_port),
                        '--server.headless', 'true'], cwd=ROOT, env=env))
        print(f'\n=== Services Available ===\n'
              f'🎯 Recall Dashboard: http://127.0.0.1:{args.dashboard_port}\n'
              f'👥 Start Your Journey: http://127.0.0.1:8101\n'
              f'📚 Class Booking: http://127.0.0.1:8102\n'
              f'🎁 Member Offers: http://127.0.0.1:8103\n\n'
              f'Ctrl+C stops processes; saved state is preserved. Use --reset for a fresh journey.', flush=True)
        reported = set()
        while children[-1].poll() is None:
            for index, child in enumerate(children[:-1]):
                if child.poll() is not None and index not in reported:
                    reported.add(index)
                    print(f'Application process {child.pid} stopped; Recall remains available to show partial completion. '
                          'Restart the launcher to resume all saved application state.', flush=True)
            time.sleep(.5)
        raise RuntimeError('Recall exited. Restart the launcher to resume saved state.')
    except KeyboardInterrupt:
        return 0
    except (OSError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        for child in reversed(children):
            if child.poll() is None:
                child.terminate()
        for child in reversed(children):
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


if __name__ == '__main__':
    raise SystemExit(main())
