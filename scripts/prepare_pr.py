#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, load_json, write_json, current_branch, current_head, utc_now

def main():
    repo=repository_root(); features=load_json(repo/'tasks/feature_list.json'); state=load_json(repo/'tasks/run_state.json'); run_id=features['run_id']
    outdir=repo/'docs/pull-requests'; outdir.mkdir(parents=True, exist_ok=True)
    md=outdir/f'{run_id}.md'; meta=outdir/f'{run_id}.json'
    tasks=features.get('tasks',[])
    lines=[f'# Pull Request: {run_id}','',f'Branch: `{current_branch(repo)}`',f'Head: `{current_head(repo)[:12]}`','', '## Summary','', f'Implements approved run `{run_id}`.', '', '## Task Traceability','', '| Task | Status | Commit |','|---|---|---|']
    for t in tasks:
        lines.append(f"| {t['task_id']} | {t.get('status')} | `{str(t.get('implementation',{}).get('commit_sha') or 'pending')[:12]}` |")
    lines += ['', '## Validation', '', f"- Engineering closure: `{state.get('closure',{}).get('engineering',{}).get('verdict','not closed')}`", '- See run and session reports for evidence.', '', '## Rollback', '', '- Revert task commits in reverse order and rerun gates.', '', '## Non-goals', '', '- No merge, deployment, or production operation.']
    md.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    write_json(meta, {'schema_version':'1.0','run_id':run_id,'generated_at':utc_now(),'title':f'Implement {run_id}','body_path':str(md.relative_to(repo)),'head_branch':current_branch(repo),'head_sha':current_head(repo),'draft_default':True})
    print(json.dumps({'verdict':'PASS','body':str(md.relative_to(repo)),'metadata':str(meta.relative_to(repo))}, indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
