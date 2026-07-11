#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, load_config

def main():
    repo=repository_root(); cfg=load_config(repo); workflows=list((repo/'.github/workflows').glob('*.yml'))+list((repo/'.github/workflows').glob('*.yaml')) if (repo/'.github/workflows').exists() else []
    gate_cmds=[g.get('command') for group in cfg.get('gates',{}).values() for g in group]
    warnings=[]
    if not workflows: warnings.append('no GitHub Actions workflows found; CI parity cannot be fully checked')
    if not gate_cmds: warnings.append('no local harness gates configured')
    out={'verdict':'PASS_WITH_WARNINGS' if warnings else 'PASS','workflow_count':len(workflows),'gate_count':len(gate_cmds),'warnings':warnings}
    print(json.dumps(out,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
