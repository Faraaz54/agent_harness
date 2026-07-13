#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, validate_json_schema, HarnessError

SCHEMA_BY_KIND={
 'implementation-result':'schemas/implementation-result.schema.json',
 'review-result':'schemas/review-result.schema.json',
 'task-validation':'schemas/task-validation.schema.json',
 'domain-review-result':'schemas/domain-review-result.schema.json',
 'orchestrator-action':'schemas/orchestrator-action.schema.json',
 'expectations':'schemas/expectations.schema.json',
 'expectation-derivation-result':'schemas/expectation-derivation-result.schema.json',
 'expectation-validation-result':'schemas/expectation-validation-result.schema.json',
 'task-decomposition-result':'schemas/task-decomposition-result.schema.json',
 'task-contract-validation-result':'schemas/task-contract-validation-result.schema.json',
 'task-contracts':'schemas/task-contracts.schema.json',
 'teach-me-report':'schemas/teach-me-report.schema.json',
 'model-routing':'schemas/model-routing.schema.json',
 'run-manifest':'schemas/run-manifest.schema.json',
 'context-pack':'schemas/context-pack.schema.json',
 'project-context-index':'schemas/project-context-index.schema.json',
 'technical-spec':'schemas/technical-spec.schema.json',
 'technical-spec-derivation-result':'schemas/technical-spec-derivation-result.schema.json',
 'technical-spec-validation-result':'schemas/technical-spec-validation-result.schema.json',
}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--kind', required=True, choices=sorted(SCHEMA_BY_KIND))
    ap.add_argument('--path', required=True)
    args=ap.parse_args(); repo=repository_root()
    try:
        validate_json_schema(repo/args.path, repo/SCHEMA_BY_KIND[args.kind])
        print(json.dumps({'verdict':'PASS','kind':args.kind,'path':args.path}, indent=2)); return 0
    except Exception as e:
        print(json.dumps({'verdict':'FAIL','error':str(e)}, indent=2)); return 1
if __name__=='__main__': raise SystemExit(main())
