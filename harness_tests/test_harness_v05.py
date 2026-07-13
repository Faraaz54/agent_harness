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
            for d in ['docs/intents','docs/context','docs/expectations','docs/task-contracts','docs/validation-reports','tasks']:
                (repo/d).mkdir(parents=True,exist_ok=True)
            (repo/'docs/intents/x.md').write_text('# Intent: X\n\n## Goal\nBuild a tiny local pipeline.\n\n## Constraints\n- Preserve context.\n\n## Failure Conditions\n- Tests fail.\n')
            subprocess.run([sys.executable,'-B','scripts/assemble_context.py','--intent','docs/intents/x.md','--output-json','docs/context/x.json','--output-md','docs/context/x.md'],cwd=repo,check=True)
            ctx=json.loads((repo/'docs/context/x.json').read_text())
            ctx_files=[{'context_id':f['context_id'],'path':f['path'],'used_for':['expectation_derivation','task_decomposition']} for f in ctx['project_context']['included_files']]
            (repo/'docs/expectations/x.json').write_text(json.dumps({
                'schema_version':'1.0','intent_id':'x','source_context_id':'x',
                'source_context':{'context_pack_path':'docs/context/x.json','context_pack_id':'x','project_context_files':ctx_files,'omitted_project_context_files':[]},
                'success_scenarios':['s'],'failure_scenarios':['f'],'acceptance_criteria':['add works'],
                'validation_strategy':['unit test'],
                'testing_expectations_matrix':[{'behavior_or_risk':'add works','unit':'Required','integration':'Not required: no boundary','local_e2e':'Not required: no pipeline','cloud_e2e':'Not required: no authority'}],
                'required_testing_tiers':{'unit':{'required':True,'reason':'logic'},'integration':{'required':False,'reason':'no boundary'},'local_e2e':{'required':False,'reason':'no pipeline'},'cloud_e2e':{'required':False,'reason':'no authority'}}
            }))
            subprocess.run([sys.executable,'-B','scripts/validate_expectations.py','--expectations','docs/expectations/x.json','--output','docs/validation-reports/x-expectations-validation.json'],cwd=repo,check=True)
            task_context_files=[{'context_id':f['context_id'],'path':f['path'],'used_for':['implementation','review','validation']} for f in ctx['project_context']['included_files']]
            (repo/'docs/task-contracts/x.json').write_text(json.dumps({'schema_version':'1.0','intent_id':'x','epics':[{'epic_id':'E-1','name':'Foundation','goal':'Build first slice','sequencing_rationale':'Smallest safe slice','risk_level':'low'}],'tasks':[{'task_id':'T-1','epic_id':'E-1','objective':'O','behavior':'B','scope':['src/x.py'],'allowed_paths':['src/**','tests/**'],'forbidden_paths':['docs/intents/**'], 'non_goals':[], 'dependencies':[],'acceptance_criteria':['add works'],'negative_cases':[],'verification':{'commands':['python -V']},'required_reviewers':['test-agent'],'risk_level':'low','required_context':[f['context_id'] for f in ctx['project_context']['included_files']],'context_files':task_context_files,'test_expectations': json.loads(TEST_EXPECTATIONS_FIXTURE)}]}))
            subprocess.run([sys.executable,'-B','scripts/validate_tasks.py','--tasks','docs/task-contracts/x.json','--output','docs/validation-reports/x-task-contract-validation.json'],cwd=repo,check=True)
            subprocess.run([sys.executable,'-B','scripts/prepare_run.py','--run-id','r1','--intent','docs/intents/x.md','--context','docs/context/x.json','--expectations','docs/expectations/x.json','--tasks','docs/task-contracts/x.json','--expectation-validation','docs/validation-reports/x-expectations-validation.json','--task-validation','docs/validation-reports/x-task-contract-validation.json','--output','tasks/run_manifest.draft.json','--state-output','tasks/run_state.json','--feature-output','tasks/feature_list.json'],cwd=repo,check=True)
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
