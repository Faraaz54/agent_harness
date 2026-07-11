#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, platform, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import HarnessError, load_config, repository_root, run_command, utc_now, write_json

def probe(name, cmds, exe=None):
    exe = exe or cmds[0][0]
    found = shutil.which(exe)
    r={"name":name,"available": bool(found),"executable": found,"version": None,"probe_status":"unavailable","probe_command": None}
    if not found: return r
    for cmd in cmds:
        p=run_command(cmd, Path.cwd(), timeout=20, check=False)
        out=(p.stdout or p.stderr or '').strip().splitlines()
        if p.returncode==0 and out:
            r.update({"version": out[0][:300],"probe_status":"passed","probe_command":" ".join(cmd)}); return r
    r["probe_status"]="failed"; return r

def py_mod(mod,name,args):
    p=run_command([sys.executable,'-m',mod,*args], Path.cwd(), timeout=20, check=False)
    out=(p.stdout or p.stderr or '').strip().splitlines()
    return {"name":name,"available":p.returncode==0,"executable":sys.executable,"version":out[0][:300] if out else None,"probe_status":"passed" if p.returncode==0 else "unavailable","probe_command":f"python -m {mod} {' '.join(args)}"}

def make_snapshot(repo: Path):
    cfg=load_config(repo)
    tools=[probe('Make',[['make','--version']]),py_mod('pip','pip',['--version']),py_mod('pytest','pytest',['--version']),py_mod('ruff','Ruff',['--version']),py_mod('mypy','mypy',['--version']),probe('Git',[['git','--version']]),probe('GitHub CLI',[['gh','--version']],'gh'),probe('Azure CLI',[['az','version'],['az','--version']],'az'),probe('Azure Developer CLI',[['azd','version'],['azd','--version']],'azd'),probe('Databricks CLI',[['databricks','version'],['databricks','--version']],'databricks'),probe('Docker',[['docker','--version']],'docker'),probe('Docker Compose',[['docker','compose','version']],'docker'),probe('PostgreSQL client',[['psql','--version']],'psql')]
    project_files=[x for x in ['pyproject.toml','requirements.txt','Makefile','Dockerfile','docker-compose.yml','compose.yml','pytest.ini','mypy.ini','ruff.toml','databricks.yml','azure.yaml'] if (repo/x).exists()]
    return {"schema_version":"1.0","generated_at":utc_now(),"platform":{"system":platform.system(),"release":platform.release(),"machine":platform.machine()},"python":{"version":platform.python_version(),"implementation":platform.python_implementation(),"executable":sys.executable,"virtual_environment":os.environ.get('VIRTUAL_ENV') or os.environ.get('CONDA_PREFIX')},"tools":tools,"project":{"config_files":project_files,"canonical_commands":cfg.get('gates',{})}}

def render_md(s):
    lines=['# Development Environment Bootstrap','',f"- Generated: `{s['generated_at']}`",f"- Python: `{s['python']['version']}` at `{s['python']['executable']}`",'', '| Tool | Available | Version |','|---|---:|---|']
    for t in s['tools']: lines.append(f"| {t['name']} | {'yes' if t['available'] else 'no'} | {t.get('version') or '—'} |")
    lines += ['', '## Project files', '', *([f'- `{x}`' for x in s['project']['config_files']] or ['- None detected']), '', '## Agent guidance', '', '- Prefer commands observed in this snapshot.', '- Treat this as a snapshot, not a guarantee.', '- Do not record secrets or cloud account details here.']
    return '\n'.join(lines)+'\n'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); ap.add_argument('--max-age-hours', type=int); args=ap.parse_args()
    try:
        repo=repository_root(); cfg=load_config(repo); j=repo/cfg.get('bootstrap',{}).get('json_path','docs/bootstrap/environment.json'); m=repo/cfg.get('bootstrap',{}).get('markdown_path','docs/bootstrap/environment.md')
        maxh=args.max_age_hours or int(cfg.get('bootstrap',{}).get('max_age_hours',168))
        if args.check:
            if not j.exists(): print(json.dumps({'verdict':'FAIL','error':'bootstrap missing'},indent=2)); return 1
            gen=datetime.fromisoformat(json.loads(j.read_text())['generated_at'].replace('Z','+00:00'))
            age=(datetime.now(timezone.utc)-gen.astimezone(timezone.utc)).total_seconds()/3600
            ok=age<=maxh; print(json.dumps({'verdict':'PASS' if ok else 'FAIL','age_hours':round(age,2),'max_age_hours':maxh},indent=2)); return 0 if ok else 1
        s=make_snapshot(repo); write_json(j,s); m.parent.mkdir(parents=True,exist_ok=True); m.write_text(render_md(s),encoding='utf-8'); print(json.dumps({'verdict':'PASS','json':str(j.relative_to(repo)),'markdown':str(m.relative_to(repo))},indent=2)); return 0
    except Exception as e:
        print(json.dumps({'verdict':'FAIL','error':str(e)}, indent=2)); return 1
if __name__=='__main__': raise SystemExit(main())
