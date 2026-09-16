"""Makefile lifecycle commands scoped to processes started by this project."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / '.runtime' / 'processes'


def identity(pid):
    result = subprocess.run(['ps', '-p', str(pid), '-o', 'lstart=', '-o', 'command='],
                            capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ''


def tracked(path):
    try:
        data = json.loads(path.read_text())
        return data if data['identity'] and identity(data['pid']) == data['identity'] else None
    except (FileNotFoundError, ValueError, KeyError):
        return None


def start(name, reset=False):
    STATE.mkdir(parents=True, exist_ok=True)
    path = STATE / (name + '.json')
    if tracked(path):
        print(f'{name} is already running. Use make logs or make stop.')
        return 0
    command = [sys.executable, str(ROOT / 'run_demo.py')] + (['--reset'] if reset else [])
    child = subprocess.Popen(command, cwd=ROOT, start_new_session=True)
    data = {'pid': child.pid, 'identity': identity(child.pid)}
    path.write_text(json.dumps(data))
    try:
        return child.wait()
    except KeyboardInterrupt:
        if child.poll() is None:
            os.killpg(child.pid, signal.SIGINT)
            try:
                child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
        return 0
    finally:
        if path.exists() and json.loads(path.read_text()).get('pid') == child.pid:
            path.unlink()


def stop():
    for path in sorted(STATE.glob('*.json')):
        data = tracked(path)
        if data:
            try:
                os.killpg(data['pid'], signal.SIGINT)
                deadline = time.monotonic() + 15
                while identity(data['pid']) == data['identity'] and time.monotonic() < deadline:
                    time.sleep(.1)
                if identity(data['pid']) == data['identity']:
                    os.killpg(data['pid'], signal.SIGKILL)
            except ProcessLookupError:
                pass
            print(f'Stopped {path.stem}.')
        path.unlink(missing_ok=True)
    print('Managed processes stopped. Saved demo data is preserved.')


def logs():
    for path in sorted(STATE.glob('*.json')):
        data = tracked(path)
        print(f'{path.stem}: ' + (f"running (PID {data['pid']})" if data else 'stopped'))
    print('Application output appears in the terminal running make demo.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['demo', 'stop', 'logs'])
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()
    if args.command == 'demo':
        return start(args.command, args.reset)
    return stop() if args.command == 'stop' else logs()


if __name__ == '__main__':
    raise SystemExit(main())
