#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, tempfile, shutil
from pathlib import Path
sys.dont_write_bytecode=True

def main():
    root=Path.cwd(); fixture=root/'fixtures/tiny-python-pipeline'
    if not fixture.exists():
        print(json.dumps({'verdict':'FAIL','error':'missing tiny fixture'}, indent=2)); return 1
    checks=[
        [sys.executable,'-B','scripts/validate_harness.py','.'],
        [sys.executable,'-B','scripts/model_router.py','validate'],
        [sys.executable,'-B','scripts/test_strategy.py','validate'],
        [sys.executable,'-B','scripts/project_pack.py','validate','--pack','project-packs/invoice-governance'],
    ]
    results=[]; verdict='PASS'
    for cmd in checks:
        p=subprocess.run(cmd,cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        results.append({'command':cmd,'returncode':p.returncode,'stdout':p.stdout[-2000:],'stderr':p.stderr[-2000:]})
        if p.returncode!=0: verdict='FAIL'
    print(json.dumps({'verdict':verdict,'results':results}, indent=2)); return 0 if verdict=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
