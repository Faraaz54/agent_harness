#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, git_runtime_dir

def main():
    repo=repository_root(); audit=git_runtime_dir(repo)/'audit'/'hooks.jsonl'
    print(json.dumps({'verdict':'PASS' if audit.exists() else 'WARN','audit_log':str(audit),'message':'Hook health is optional in v0.5.1; deterministic scripts remain authoritative.'}, indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
