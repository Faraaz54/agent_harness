#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys, tempfile
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, load_json, validate_active_preflight, working_tree_fingerprint, current_head, git, write_json, git_runtime_dir, HarnessError, sha256_text

def feature_map(features): return {t['task_id']:t for t in features.get('tasks',[])}
def run_check(repo: Path, cmd: list[str], name: str):
    p=subprocess.run(cmd,cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode!=0:
        raise HarnessError(f'{name} failed:\n{p.stdout}\n{p.stderr}')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--task-id', required=True); args=ap.parse_args(); repo=repository_root()
    try:
        ok,msg,pf=validate_active_preflight(repo)
        if not ok: raise HarnessError(msg)
        features=load_json(repo/'tasks/feature_list.json'); f=feature_map(features)[args.task_id]
        if f.get('validator',{}).get('status')!='passed': raise HarnessError('validator has not passed')
        last=pf.get('last_postflight',{})
        if last.get('task_id')!=args.task_id or last.get('verdict')!='PASS' or last.get('stale') or last.get('working_tree_fingerprint')!=working_tree_fingerprint(repo): raise HarnessError('fresh matching postflight is required')
        run_check(repo,[sys.executable,'-B','scripts/scope_guard.py','--task-id',args.task_id],'scope_guard')
        run_check(repo,[sys.executable,'-B','scripts/secret_scan.py','--changed-only'],'secret_scan')
        paths=f.get('implementation',{}).get('files_changed',[])+['tasks/feature_list.json','tasks/run_state.json']
        for pattern in [f'docs/implementation-results/{args.task_id}*.json', f'docs/reviews/{args.task_id}/**', f'docs/validation-results/{args.task_id}*.json', f'docs/evidence/{features.get("run_id")}/**']:
            paths.extend(str(p.relative_to(repo)) for p in repo.glob(pattern) if p.is_file())
        paths=[p for p in sorted(set(paths)) if (repo/p).exists()]
        if not paths: raise HarnessError('no paths to commit')
        git(repo,'add','--',*paths)
        subject=f"feat({args.task_id.lower()}): complete approved task"
        body=f"Implements and validates task {args.task_id}.\n\nTask-ID: {args.task_id}\nRun-ID: {features.get('run_id')}\n"
        with tempfile.NamedTemporaryFile('w',delete=False,encoding='utf-8') as tmp: tmp.write(subject+'\n\n'+body); tmp_path=tmp.name
        try: git(repo,'commit','-F',tmp_path)
        finally: Path(tmp_path).unlink(missing_ok=True)
        sha=current_head(repo); out={'verdict':'PASS','task_id':args.task_id,'commit_sha':sha,'paths':paths}
        receipt=git_runtime_dir(repo)/'commits'/f'{args.task_id}.json'; receipt.parent.mkdir(parents=True,exist_ok=True); write_json(receipt,{**out,'message_sha256':sha256_text(subject+body)})
        pf['last_postflight']['stale']=True; pf['last_postflight']['stale_reason']='task commit created'; from harnesslib import save_preflight_state; save_preflight_state(repo,pf)
        (repo/'docs/commit-results').mkdir(parents=True,exist_ok=True); write_json(repo/'docs/commit-results'/f'{args.task_id}.json',out)
        print(json.dumps(out,indent=2)); return 0
    except Exception as e:
        print(json.dumps({'verdict':'FAIL','error':str(e)},indent=2)); return 1
if __name__=='__main__': raise SystemExit(main())
