#!/usr/bin/env python3
from __future__ import annotations
import json, os, re, sys
from pathlib import Path

BLOCKED = [r"rm\s+-rf\s+/", r"git\s+push\s+--force", r"git\s+reset\s+--hard", r"curl\s+.*\|\s*sh"]

def main() -> int:
    payload = json.loads(sys.stdin.read() or '{}') if not sys.stdin.isatty() else {}
    command = payload.get('command') or ' '.join(sys.argv[1:])
    for pat in BLOCKED:
        if re.search(pat, command):
            print(json.dumps({'verdict':'BLOCK','reason':f'blocked dangerous command pattern: {pat}'}))
            return 1
    print(json.dumps({'verdict':'ALLOW','reason':'no harness hook violation detected'}))
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
