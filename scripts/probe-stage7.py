"""Bounded offline final regression; reuses explicit recovery fixture, no paid calls.
Run with PLAYWRIGHT_MODULE set, using backend/.venv/Scripts/python.exe.
Only the scratch copy gets turbopack.root covering its shared dependency junction.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('recovery_runner', ROOT/'scripts/probe-recovery.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def run():
    if not os.environ.get('PLAYWRIGHT_MODULE'):
        raise RuntimeError('Set PLAYWRIGHT_MODULE to installed playwright/index.mjs')
    scratch_root = Path.home()/'AppData/Local/hermes/cache/scratch' if os.name == 'nt' else Path(os.environ['TMPDIR'])
    scratch_root.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix='factlens-stage7-', dir=scratch_root))
    print(f'Evidence directory: {scratch}', flush=True)
    frontend = scratch/'frontend'
    frontend.mkdir()
    for name in ('app', 'public'):
        shutil.copytree(ROOT/name, frontend/name)
    for name in ('package.json', 'package-lock.json', 'tsconfig.json', 'next-env.d.ts', 'next.config.ts', 'postcss.config.mjs'):
        shutil.copy2(ROOT/name, frontend/name)
    if os.name == 'nt':
        subprocess.run(['cmd', '/c', 'mklink', '/J', str(frontend/'node_modules'), str(ROOT/'node_modules')], check=True, capture_output=True)
    else:
        (frontend/'node_modules').symlink_to(ROOT/'node_modules', target_is_directory=True)
    # Installed Next docs: linked dependencies must be inside turbopack.root.
    common = os.path.commonpath([str(frontend.resolve()), str((ROOT/'node_modules').resolve())])
    config = (frontend/'next.config.ts').read_text(encoding='utf-8')
    config = config.replace('/* config options here */', f'turbopack: {{root: {json.dumps(common)}}},')
    assert 'turbopack:' in config
    (frontend/'next.config.ts').write_text(config, encoding='utf-8')
    backend_port, frontend_port = helper.free_port(), helper.free_port()
    env = {k:v for k,v in os.environ.items() if not any(t in k.upper() for t in ('API_KEY','TOKEN','SECRET'))}
    env.update(PROBE_BACKEND=f'http://127.0.0.1:{backend_port}', PROBE_FRONTEND=f'http://127.0.0.1:{frontend_port}', PROBE_EVIDENCE_DIR=str(scratch))
    env['FACTLENS_BACKEND_URL'] = env['PROBE_BACKEND']
    processes, logs = [], []
    try:
        for name, command, cwd in (
            ('backend', [sys.executable, '-m', 'uvicorn', 'recovery_probe_app:app', '--app-dir', str(ROOT/'backend/tests'), '--host', '127.0.0.1', '--port', str(backend_port)], ROOT/'backend'),
            ('next', ['node', str(ROOT/'node_modules/next/dist/bin/next'), 'dev', '--hostname', '127.0.0.1', '--port', str(frontend_port)], frontend),
        ):
            log = (scratch/f'{name}.log').open('w', encoding='utf-8')
            logs.append(log)
            processes.append(subprocess.Popen(command, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT))
        helper.ready(env['PROBE_BACKEND']+'/__test__/recovery', processes[0])
        helper.ready(env['PROBE_FRONTEND']+'/api/fact-check', processes[1])
        out = (scratch/'browser.stdout').open('w', encoding='utf-8')
        err = (scratch/'browser.stderr').open('w', encoding='utf-8')
        logs.extend([out, err])
        browser = subprocess.Popen(['node', str(ROOT/'scripts/probe-stage7.mjs')], cwd=ROOT, env=env, stdout=out, stderr=err)
        processes.append(browser)
        browser.wait(timeout=300)
        out.close()
        err.close()
        print((scratch/'browser.stdout').read_text(encoding='utf-8'), flush=True)
        print((scratch/'browser.stderr').read_text(encoding='utf-8'), flush=True)
        return browser.returncode
    finally:
        for process in reversed(processes):
            helper.stop_owned(process)
        for log in logs:
            log.close()
        closed = [helper.port_closed(p) for p in (backend_port, frontend_port)]
        cleanup = dict(ownedServersStopped=all(closed), ports=[backend_port, frontend_port], processes=[dict(pid=p.pid,exitCode=p.returncode) for p in processes])
        (scratch/'cleanup.json').write_text(json.dumps(cleanup, indent=2), encoding='utf-8')
        print(json.dumps(cleanup), flush=True)
        assert all(closed), 'Owned port still listening'


if __name__ == '__main__':
    sys.exit(run())
