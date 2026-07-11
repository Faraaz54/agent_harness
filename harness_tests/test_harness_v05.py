from __future__ import annotations
import json, subprocess, tempfile, unittest, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TEST_EXPECTATIONS_FIXTURE = '{\n  "highest_required_tier": "integration",\n  "tier_rationale": "The task touches a local verification boundary.",\n  "unit": {"required": true, "what_to_test": ["focused behaviour"], "evidence_required": ["unit test output"]},\n  "integration": {"required": true, "what_to_test": ["local boundary"], "evidence_required": ["integration test output"]},\n  "local_e2e": {"required": false, "what_to_test": [], "evidence_required": [], "not_required_reason": "No multi-stage pipeline flow in this task."},\n  "cloud_e2e": {"required": false, "what_to_test": [], "evidence_required": [], "not_required_reason": "No explicit cloud environment authority."},\n  "coverage_map": [{"criterion": "add works", "tiers": ["unit"]}]\n}'
sys.path.insert(0,str(ROOT/'scripts'))
from harnesslib import working_tree_fingerprint, sha256_file

class HarnessV05Tests(unittest.TestCase):
    def test_required_package_validates(self):
        p=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/validate_harness.py'),str(ROOT)],text=True,capture_output=True)
        self.assertEqual(0,p.returncode,p.stdout+p.stderr)

    def test_tree_fingerprint_staging_invariant(self):
        with tempfile.TemporaryDirectory() as raw:
            repo=Path(raw); subprocess.run(['git','init','-q'],cwd=repo,check=True); subprocess.run(['git','config','user.email','t@example.com'],cwd=repo,check=True); subprocess.run(['git','config','user.name','T'],cwd=repo,check=True)
            (repo/'a.txt').write_text('a\n'); subprocess.run(['git','add','a.txt'],cwd=repo,check=True); subprocess.run(['git','commit','-q','-m','init'],cwd=repo,check=True)
            (repo/'b.txt').write_text('b\n'); before=working_tree_fingerprint(repo); subprocess.run(['git','add','b.txt'],cwd=repo,check=True); after=working_tree_fingerprint(repo)
            self.assertEqual(before,after)
            (repo/'b.txt').write_text('bb\n'); self.assertNotEqual(before,working_tree_fingerprint(repo))

    def test_prepare_run_generates_expected_files(self):
        with tempfile.TemporaryDirectory() as raw:
            repo=Path(raw)
            subprocess.run(['git','init','-q'],cwd=repo,check=True)
            subprocess.run(['git','config','user.email','t@example.com'],cwd=repo,check=True); subprocess.run(['git','config','user.name','T'],cwd=repo,check=True)
            subprocess.run(['cp','-a',str(ROOT)+ '/.', str(repo)],check=True)
            (repo/'docs/intents').mkdir(parents=True,exist_ok=True); (repo/'docs/context').mkdir(parents=True,exist_ok=True); (repo/'docs/expectations').mkdir(parents=True,exist_ok=True); (repo/'docs/task-contracts').mkdir(parents=True,exist_ok=True); (repo/'docs/validation-reports').mkdir(parents=True,exist_ok=True)
            (repo/'docs/intents/x.md').write_text('# Intent: X\n\n## Goal\nG\n\n## Constraints\n- C\n\n## Failure Conditions\n- F\n')
            (repo/'docs/context/x.json').write_text(json.dumps({'intent_id':'x','runtime':{},'repository':{},'project_pack':{}}))
            (repo/'docs/expectations/x.json').write_text(json.dumps({'intent_id':'x','success_scenarios':['s'],'failure_scenarios':['f'],'acceptance_criteria':['a']}))
            (repo/'docs/task-contracts/x.json').write_text(json.dumps({'schema_version':'1.0','intent_id':'x','tasks':[{'task_id':'T-1','objective':'O','behavior':'B','scope':['src/x.py'],'dependencies':[],'acceptance_criteria':['A'],'negative_cases':[],'verification':{'commands':['python -V']},'required_reviewers':['test-agent'],'risk_level':'low','test_expectations': json.loads(TEST_EXPECTATIONS_FIXTURE)}]}))
            (repo/'docs/validation-reports/x-expectations-validation.md').write_text('PASS')
            subprocess.run([sys.executable,'-B','scripts/prepare_run.py','--run-id','r1','--intent','docs/intents/x.md','--context','docs/context/x.json','--expectations','docs/expectations/x.json','--tasks','docs/task-contracts/x.json','--expectation-validation','docs/validation-reports/x-expectations-validation.md','--output','tasks/run_manifest.draft.json','--state-output','tasks/run_state.json','--feature-output','tasks/feature_list.json'],cwd=repo,check=True)
            self.assertTrue((repo/'tasks/run_manifest.draft.json').exists())
            self.assertEqual(load:=json.loads((repo/'tasks/feature_list.json').read_text())['tasks'][0]['status'],'pending')

if __name__=='__main__': unittest.main()

class ModelRoutingTests(unittest.TestCase):
    def test_model_router_validates_config(self):
        p=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/model_router.py'),'validate'],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(0,p.returncode,p.stdout+p.stderr)
        self.assertIn('PASS',p.stdout)

    def test_model_router_returns_validator_alias(self):
        p=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/model_router.py'),'role','--name','validator-agent'],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(0,p.returncode,p.stdout+p.stderr)
        data=json.loads(p.stdout)
        self.assertEqual('validation_reasoning',data['alias'])
