#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, load_json

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--intent', required=True); ap.add_argument('--context', required=True); ap.add_argument('--expectations', required=True); ap.add_argument('--tasks', required=True); args=ap.parse_args()
    repo=repository_root(); errors=[]
    intent=(repo/args.intent).read_text(encoding='utf-8') if (repo/args.intent).exists() else ''
    for h in ['## Goal','## Constraints','## Failure Conditions']:
        if h not in intent: errors.append(f'intent missing {h}')
    ctx=load_json(repo/args.context); exp=load_json(repo/args.expectations); tasks=load_json(repo/args.tasks)
    if not ctx.get('intent_id'): errors.append('context missing intent_id')
    if not exp.get('success_scenarios'): errors.append('expectations missing success_scenarios')
    if not exp.get('failure_scenarios'): errors.append('expectations missing failure_scenarios')
    if not tasks.get('tasks'): errors.append('task contracts contain no tasks')
    seen=set()
    for t in tasks.get('tasks',[]):
        for k in ['task_id','objective','behavior','scope','acceptance_criteria','verification','required_reviewers','risk_level']:
            if k not in t: errors.append(f"task {t.get('task_id','?')} missing {k}")
        if t.get('task_id') in seen: errors.append(f"duplicate task_id {t.get('task_id')}")
        seen.add(t.get('task_id'))
        for dep in t.get('dependencies',[]):
            if dep not in seen and dep not in [x.get('task_id') for x in tasks.get('tasks',[])]: errors.append(f"task {t.get('task_id')} unknown dependency {dep}")
    print(json.dumps({'verdict':'PASS' if not errors else 'FAIL','errors':errors},indent=2)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
