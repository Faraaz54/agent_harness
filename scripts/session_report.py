#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, html, sys
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, load_json, write_json, utc_now, current_branch, current_head

def md(model):
    lines=[f"# Session Report — {model['run_id']}",'',f"- Generated: `{model['generated_at']}`",f"- Branch: `{model['branch']}`",f"- Head: `{model['head'][:12]}`",'', '## Task outcomes','', '| Task | Status | Commit |','|---|---|---|']
    for t in model['tasks']: lines.append(f"| {t['task_id']} | {t['status']} | `{str(t.get('commit_sha') or 'none')[:12]}` |")
    lines += ['', '## Teach-me topics', '', '- Explain the intent and constraints.', '- Explain the task contracts and validation evidence.', '- Explain review findings and repairs.']
    return '\n'.join(lines)+'\n'

def html_doc(model):
    rows=''.join(f"<tr><td>{html.escape(t['task_id'])}</td><td>{html.escape(t['status'])}</td><td><code>{html.escape(str(t.get('commit_sha') or 'none')[:12])}</code></td></tr>" for t in model['tasks'])
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Session {html.escape(model['run_id'])}</title><style>body{{font-family:system-ui;margin:2rem;line-height:1.5}}table{{border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:.5rem}}code{{background:#f2f2f2;padding:.15rem}}</style></head><body><h1>Session Report — {html.escape(model['run_id'])}</h1><p>Generated {html.escape(model['generated_at'])}</p><table><tr><th>Task</th><th>Status</th><th>Commit</th></tr>{rows}</table><h2>Teach me</h2><ul><li>Intent and constraints</li><li>Implementation and validation</li><li>Review and repair history</li></ul></body></html>"

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--coverage', default='run'); args=ap.parse_args(); repo=repository_root(); features=load_json(repo/'tasks/feature_list.json'); run_id=features['run_id']
    tasks=[{'task_id':t['task_id'],'status':t['status'],'commit_sha':t.get('implementation',{}).get('commit_sha')} for t in features.get('tasks',[])]
    model={'schema_version':'1.0','run_id':run_id,'generated_at':utc_now(),'coverage':args.coverage,'branch':current_branch(repo),'head':current_head(repo),'tasks':tasks}
    outdir=repo/'docs/session-reports'/run_id; outdir.mkdir(parents=True,exist_ok=True)
    write_json(outdir/'final.json',model); (outdir/'final.md').write_text(md(model),encoding='utf-8'); (outdir/'final.html').write_text(html_doc(model),encoding='utf-8')
    print(json.dumps({'verdict':'PASS','json':str((outdir/'final.json').relative_to(repo)),'markdown':str((outdir/'final.md').relative_to(repo)),'html':str((outdir/'final.html').relative_to(repo))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
