"""Run from repo: backend/.venv/Scripts/python.exe scripts/probe-recovery.py

Requires node, installed repo node_modules and PLAYWRIGHT_MODULE pointing to an
installed Playwright index.mjs (uses installed Google Chrome, headless). No paid calls, no .env
copying, no production test switches. Uses isolated scratch Next copy + webpack
because Turbopack cannot follow the shared node_modules junction outside its root.
Logs/evidence stay in the printed scratch directory. Stops only owned processes.
Add --network-restart for actual backend termination, offline UI requests, and
same-document retries after restarting the fixture on the same port. Without
this flag the existing adapter-failure/detail-panel scenario is unchanged.
"""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def ready(url, process):
    end = time.monotonic() + 180
    while time.monotonic() < end:
        if process.poll() is not None:
            raise RuntimeError(f'Owned server exited: {process.returncode}')
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return
        except (OSError, TimeoutError):
            pass
        time.sleep(.2)
    raise TimeoutError(f'Readiness deadline: {url}')


def stop_owned(process):
    if process.poll() is None:
        if os.name == 'nt':
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], check=True, capture_output=True)
        else:
            process.terminate()
        process.wait(timeout=15)


def port_closed(port):
    with socket.socket() as sock:
        return sock.connect_ex(('127.0.0.1', port)) != 0


def run():
    network_restart = '--network-restart' in sys.argv
    if not os.environ.get('PLAYWRIGHT_MODULE'):
        raise RuntimeError('Set PLAYWRIGHT_MODULE to installed playwright/index.mjs')
    scratch_root = Path.home()/'AppData/Local/hermes/cache/scratch' if os.name == 'nt' else Path(os.environ['TMPDIR'])
    scratch_root.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix='factlens-recovery-', dir=scratch_root))
    print(f'Evidence directory: {scratch}', flush=True)
    frontend = scratch / 'frontend'
    frontend.mkdir()
    for name in ('app', 'public'):
        shutil.copytree(ROOT/name, frontend/name)
    for name in ('package.json', 'package-lock.json', 'tsconfig.json', 'next-env.d.ts', 'next.config.ts', 'postcss.config.mjs'):
        if (ROOT/name).exists():
            shutil.copy2(ROOT/name, frontend/name)
    if os.name == 'nt':
        subprocess.run(['cmd', '/c', 'mklink', '/J', str(frontend/'node_modules'), str(ROOT/'node_modules')], check=True, capture_output=True)
    else:
        (frontend/'node_modules').symlink_to(ROOT/'node_modules', target_is_directory=True)
    backend_port, frontend_port = free_port(), free_port()
    env = os.environ.copy()
    # Never forward provider credentials into either child process.
    for key in list(env):
        if any(token in key.upper() for token in ('API_KEY','TOKEN','SECRET')):
            del env[key]
    env.update(PROBE_BACKEND=f'http://127.0.0.1:{backend_port}', PROBE_FRONTEND=f'http://127.0.0.1:{frontend_port}')
    env['PROBE_EVIDENCE_DIR'] = str(scratch)
    env['FACTLENS_BACKEND_URL'] = env['PROBE_BACKEND']
    processes = []
    logs = []
    try:
        for name, command, cwd in (
            ('backend', [sys.executable, '-m', 'uvicorn', 'recovery_probe_app:app', '--app-dir', str(ROOT/'backend/tests'), '--host', '127.0.0.1', '--port', str(backend_port)], ROOT/'backend'),
            ('next', ['node', str(ROOT/'node_modules/next/dist/bin/next'), 'dev', '--webpack', '--hostname', '127.0.0.1', '--port', str(frontend_port)], frontend),
        ):
            log = (scratch/f'{name}.log').open('w', encoding='utf-8')
            logs.append(log)
            processes.append(subprocess.Popen(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT))
        ready(env['PROBE_BACKEND']+'/__test__/recovery', processes[0])
        ready(env['PROBE_FRONTEND']+'/api/fact-check', processes[1])
        if network_restart:
            browser_out = (scratch/'browser.stdout').open('w', encoding='utf-8')
            browser_err = (scratch/'browser.stderr').open('w', encoding='utf-8')
            logs.extend([browser_out, browser_err])
            browser_process = subprocess.Popen(['node', str(ROOT/'scripts/probe-network-restart.mjs')], env=env, cwd=ROOT, stdout=browser_out, stderr=browser_err)
            processes.append(browser_process)
            completed = set()
            deadline = time.monotonic() + 240
            while browser_process.poll() is None:
                if time.monotonic() > deadline:
                    raise TimeoutError('Network restart browser deadline')
                for action in ('stop', 'restart'):
                    if action in completed or not (scratch/f'{action}.request').exists():
                        continue
                    if action == 'stop':
                        stop_owned(processes[0])
                        assert port_closed(backend_port), 'Backend port must close before UI request'
                        detail = dict(pid=processes[0].pid, exitCode=processes[0].returncode, port=backend_port, portClosed=True)
                    else:
                        assert 'stop' in completed
                        log = (scratch/'backend-restarted.log').open('w', encoding='utf-8')
                        logs.append(log)
                        restarted = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'recovery_probe_app:app', '--app-dir', str(ROOT/'backend/tests'), '--host', '127.0.0.1', '--port', str(backend_port)], cwd=ROOT/'backend', env=env, stdout=log, stderr=subprocess.STDOUT)
                        processes.append(restarted)
                        ready(env['PROBE_BACKEND']+'/__test__/recovery', restarted)
                        detail = dict(pid=restarted.pid, port=backend_port, ready=True)
                    detail['monotonic'] = time.monotonic()
                    temporary = scratch/f'{action}.tmp'
                    temporary.write_text(json.dumps(detail), encoding='utf-8')
                    temporary.replace(scratch/f'{action}.done')
                    completed.add(action)
                time.sleep(.05)
            browser_out.close()
            browser_err.close()
            result = subprocess.CompletedProcess(browser_process.args, browser_process.returncode, (scratch/'browser.stdout').read_text(encoding='utf-8'), (scratch/'browser.stderr').read_text(encoding='utf-8'))
        else:
            result = subprocess.run(['node', str(ROOT/'scripts/probe-recovery.mjs')],env=env,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=240)
        (scratch/'browser-evidence.json').write_text(result.stdout or result.stderr,encoding='utf-8')
        if result.returncode == 0:
            evidence = json.loads(result.stdout)
            print(json.dumps({'passed': evidence['passed'], 'bundler': evidence['bundler'], 'responses': evidence['responses'], 'checkpoints': [{'case': item['case'], 'details': item} for item in evidence['observations']]}), flush=True)
        else:
            print(result.stdout, flush=True)
            print(result.stderr, flush=True)
        return result.returncode
    finally:
        for process in reversed(processes):
            stop_owned(process)
        for log in logs:
            log.close()
        for port in (backend_port,frontend_port):
            assert port_closed(port), f'Owned port still listening: {port}'
        cleanup = dict(ownedServersStopped=True, ports=[backend_port,frontend_port], processes=[dict(pid=p.pid, exitCode=p.returncode) for p in processes])
        (scratch/'cleanup.json').write_text(json.dumps(cleanup, indent=2), encoding='utf-8')
        print(json.dumps(cleanup),flush=True)


if __name__ == '__main__':
    sys.exit(run())
