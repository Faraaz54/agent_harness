#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
sys.dont_write_bytecode=True
from harnesslib import repository_root, load_json, write_json, utc_now, git

def fmap(features): return {t['task_id']:t for t in features.get('tasks',[])}
def save(repo,state,features): state['last_updated_at']=utc_now(); write_json(repo/'tasks/run_state.json',state); write_json(repo/'tasks/feature_list.json',features)
def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd', required=True)
    for c in ['abort','resume','defer','unblock','rollback']:
        sp=sub.add_parser(c); sp.add_argument('--task-id'); sp.add_argument('--reason'); sp.add_argument('--decision')
    args=ap.parse_args(); repo=repository_root(); state=load_json(repo/'tasks/run_state.json'); features=load_json(repo/'tasks/feature_list.json'); fm=fmap(features)
    if args.cmd=='abort':
        state['status']='aborted'; state.setdefault('abortions',[]).append({'reason':args.reason,'at':utc_now()}); out={'verdict':'PASS','status':'aborted'}
    elif args.cmd=='resume':
        state['status']='in_progress'; out={'verdict':'PASS','status':'in_progress','current_task_id':state.get('current_task_id')}
    elif args.cmd=='defer':
        f=fm[args.task_id]; f['status']='deferred'; f.setdefault('deferrals',[]).append({'reason':args.reason,'at':utc_now()}); state['deferred_task_ids']=sorted(set(state.get('deferred_task_ids',[])+[args.task_id])); state['current_task_id']=None; out={'verdict':'PASS','task_id':args.task_id,'status':'deferred'}
    elif args.cmd=='unblock':
        f=fm[args.task_id]; f['status']='pending'; f.setdefault('unblock_decisions',[]).append({'decision':args.decision,'at':utc_now()}); state['blocked_task_ids']=[x for x in state.get('blocked_task_ids',[]) if x!=args.task_id]; out={'verdict':'PASS','task_id':args.task_id,'status':'pending'}
    else:
        if args.task_id and args.task_id in fm:
            fm[args.task_id]['status']='pending'; state['current_task_id']=None
        out={'verdict':'PASS_WITH_WARNINGS','message':'Rollback marked task pending. Revert code manually or use git reset only with explicit authority.','task_id':args.task_id}
    save(repo,state,features); print(json.dumps(out,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
