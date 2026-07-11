#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shutil, sys
from pathlib import Path
sys.dont_write_bytecode=True
EXCLUDE={'.git','__pycache__','.pytest_cache'}
def copytree(src: Path, dst: Path, overwrite: bool):
    for p in src.rglob('*'):
        if any(part in EXCLUDE for part in p.parts): continue
        rel=p.relative_to(src); target=dst/rel
        if p.is_dir(): target.mkdir(parents=True, exist_ok=True); continue
        if target.exists() and not overwrite: continue
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p,target)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--target', required=True); ap.add_argument('--overwrite', action='store_true'); args=ap.parse_args(); src=Path(__file__).resolve().parents[1]; dst=Path(args.target).resolve(); dst.mkdir(parents=True, exist_ok=True); copytree(src,dst,args.overwrite)
    manifest={'schema_version':'1.0','source':str(src),'target':str(dst),'overwrite':args.overwrite}
    (dst/'.harness').mkdir(exist_ok=True); (dst/'.harness/install-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'verdict':'PASS','target':str(dst)},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
