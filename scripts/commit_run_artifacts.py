#!/usr/bin/env python3
from __future__ import annotations
import json, tempfile, sys
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, load_json, git, current_head, git_status

def main():
    repo=repository_root(); features=load_json(repo/'tasks/feature_list.json'); run_id=features['run_id']
    allowed=['tasks/feature_list.json','tasks/run_state.json']
    for base in [repo/'docs/run-reports', repo/'docs/session-reports'/run_id, repo/'docs/pull-requests']:
        if base.exists(): allowed += [str(p.relative_to(repo)) for p in base.rglob('*') if p.is_file()]
    allowed=sorted(set(p for p in allowed if (repo/p).exists()))
    if not allowed: print(json.dumps({'verdict':'FAIL','error':'no governance artifacts to commit'},indent=2)); return 1
    git(repo,'add','--',*allowed)
    msg=f'docs(run): record {run_id} governance evidence\n\nRun-ID: {run_id}\n'
    with tempfile.NamedTemporaryFile('w',delete=False,encoding='utf-8') as tmp: tmp.write(msg); tmp_path=tmp.name
    try: git(repo,'commit','-F',tmp_path)
    finally: Path(tmp_path).unlink(missing_ok=True)
    print(json.dumps({'verdict':'PASS','commit_sha':current_head(repo),'paths':allowed,'remaining_status':git_status(repo)}, indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
