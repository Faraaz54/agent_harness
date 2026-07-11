#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
sys.dont_write_bytecode=True
from harnesslib import repository_root, load_json, write_json, utc_now

def main():
    repo=repository_root(); features=load_json(repo/'tasks/feature_list.json'); state=load_json(repo/'tasks/run_state.json'); run_id=features['run_id']
    terminal=all(t['status'] in ['passed','blocked','deferred'] for t in features.get('tasks',[]))
    state['status']='local_delivery_complete' if terminal else 'not_closable'; state['current_stage']='local_delivery_complete' if terminal else 'blocked'; state['closure']={'engineering':{'verdict':'CLOSED' if terminal else 'NOT_CLOSABLE','closed_at':utc_now() if terminal else None},'learning':{'status':'LEARNING_PENDING'}}; write_json(repo/'tasks/run_state.json',state)
    (repo/'docs/run-reports').mkdir(parents=True,exist_ok=True); (repo/'docs/run-reports'/f'{run_id}.md').write_text(f"# Run Report: {run_id}\n\nVerdict: {state['closure']['engineering']['verdict']}\n",encoding='utf-8')
    subprocess.run([sys.executable,'-B','scripts/session_report.py','--coverage','run'],cwd=repo,check=False)
    print(json.dumps({'verdict':state['closure']['engineering']['verdict'],'run_id':run_id},indent=2)); return 0 if terminal else 1
if __name__=='__main__': raise SystemExit(main())
