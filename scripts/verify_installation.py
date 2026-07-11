#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root
REQ=['AGENTS.md','README.md','harness.config.json','.cursor/commands/build-auto.md','scripts/build_orchestrator.py','scripts/validate_harness.py','docs/operator-manual/README.md']
def main():
    repo=repository_root(); missing=[p for p in REQ if not (repo/p).exists()]
    out={'verdict':'FAIL' if missing else 'PASS','missing':missing}
    print(json.dumps(out,indent=2)); return 1 if missing else 0
if __name__=='__main__': raise SystemExit(main())
