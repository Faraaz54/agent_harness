#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, git, changed_files
PATTERNS={
 'private_key': re.compile(r'-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
 'generic_api_key': re.compile(r'(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{20,}'),
 'azure_conn': re.compile(r'DefaultEndpointsProtocol=.*AccountKey=', re.I),
 'databricks_token': re.compile(r'dapi[a-f0-9]{32}', re.I),
}
SKIP_DIRS={'.git','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache'}

def scan_file(path: Path) -> list[dict]:
    out=[]
    try:
        text=path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return out
    for name,pat in PATTERNS.items():
        for m in pat.finditer(text):
            line=text.count('\n',0,m.start())+1
            out.append({'kind':name,'line':line})
    return out

def all_files(repo: Path) -> list[Path]:
    files=[]
    for p in repo.rglob('*'):
        if any(part in SKIP_DIRS for part in p.parts): continue
        if p.is_file() and p.stat().st_size < 2_000_000: files.append(p)
    return files

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--changed-only', action='store_true'); args=ap.parse_args(); repo=repository_root()
    paths=[repo/p for p in changed_files(repo)] if args.changed_only else all_files(repo)
    findings=[]
    for p in paths:
        if p.exists() and p.is_file():
            for f in scan_file(p): findings.append({'path':str(p.relative_to(repo)),**f})
    verdict='FAIL' if findings else 'PASS'
    print(json.dumps({'verdict':verdict,'findings':findings}, indent=2)); return 1 if findings else 0
if __name__=='__main__': raise SystemExit(main())
