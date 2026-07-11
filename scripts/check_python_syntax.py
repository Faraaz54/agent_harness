#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, sys
from pathlib import Path
sys.dont_write_bytecode = True
EXCLUDE={'.git','__pycache__','.venv','venv','node_modules','.mypy_cache','.pytest_cache'}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('paths', nargs='*', default=['scripts','src','tests','harness_tests'])
    args=ap.parse_args(); errors=[]; checked=0
    for raw in args.paths:
        root=Path(raw)
        if not root.exists(): continue
        candidates=[root] if root.is_file() else root.rglob('*.py')
        for p in candidates:
            if any(part in EXCLUDE for part in p.parts): continue
            try: ast.parse(p.read_text(encoding='utf-8'), filename=str(p)); checked+=1
            except Exception as e: errors.append(f'{p}: {e}')
    if errors:
        print('\n'.join('ERROR '+e for e in errors)); return 1
    print(f'Python syntax validation passed: {checked} file(s).'); return 0
if __name__=='__main__': raise SystemExit(main())
