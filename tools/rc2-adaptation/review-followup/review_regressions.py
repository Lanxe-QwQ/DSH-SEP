"""Local offline review regression; does not dispatch workflows or install code."""
import ast,hashlib,json,os,re,textwrap,types,unittest
from pathlib import Path

S=Path(os.environ.get('SEP_RC2_REVIEW_STAGE',r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1'))
R=Path(os.environ.get('SEP_RC2_REVIEW_SOURCE',str(S/'source')))
CURRENT='854b8dd3c82c7a2d7b26b6a5a14ba3488b293b39b922cd4f5e35347f0ecf40a5'
OLD='f80533561f1c91beab7656f014fa56e05936489a94224cd1f9913766416c8ca8'
NAME='dsh-sep-bundle-0.2.1-beta.3-rc2-adapter.1.tgz'
REPO='Lanxe-QwQ/DSH-SEP'
WORKFLOWS=['sep-release-relay.yml','sep-beta2-release-relay.yml']
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def workflow(name):return (R/'.github/workflows'/name).read_text(encoding='utf-8')
def inline(text):
 lines=text.splitlines();start=next(i for i,x in enumerate(lines) if "python3 - <<'" in x)
 marker=lines[start].split("<<'",1)[1].split("'",1)[0]
 end=next(i for i in range(start+1,len(lines)) if lines[i].strip()==marker)
 return textwrap.dedent('\n'.join(lines[start+1:end]))
def guard(text,repo,ref):
 expr=re.search(r'^\s+if: (.+)$',text,re.M).group(1).replace('&&',' and ')
 tree=ast.parse(expr,mode='eval')
 allowed=(ast.Expression,ast.BoolOp,ast.And,ast.Compare,ast.Eq,ast.Attribute,ast.Name,ast.Load,ast.Constant)
 assert all(isinstance(n,allowed) for n in ast.walk(tree))
 return eval(compile(tree,'<workflow-guard>','eval'),{'__builtins__':{}},{'github':types.SimpleNamespace(repository=repo,ref=ref)})
def adaptation():
 tree=ast.parse(inline(workflow(WORKFLOWS[1])))
 fn=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='adapt_repository_source'),None)
 if fn is None:return None
 ns={'hashlib':hashlib};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<fixed-relay-adapter>','exec'),ns)
 return ns['adapt_repository_source']
def canonical_source(path):return (R/path).read_bytes().replace(b'\r\n',b'\n')

class ReviewRegressions(unittest.TestCase):
 def test_current_candidate_pointer_is_exact(self):
  p=S/'artifacts/CURRENT-CANDIDATE.json';self.assertTrue(p.is_file(),'CURRENT_CANDIDATE_INDEX_MISSING')
  x=json.loads(p.read_bytes());self.assertEqual(x['status'],'ready');self.assertEqual(x['path'],'r4/'+NAME)
  self.assertEqual(x['sha256'],CURRENT);self.assertEqual(sha(S/'artifacts'/x['path']),CURRENT)
 def test_unreviewed_top_level_package_is_quarantined(self):
  self.assertFalse((S/'artifacts'/NAME).exists(),'STALE_INSTALLABLE_NAME_AT_TOP_LEVEL')
  p=S/'artifacts/history/pre-r4'/NAME;self.assertTrue(p.is_file(),'OLD_BYTES_NOT_PRESERVED')
  self.assertEqual(sha(p),OLD)
 def test_quarantine_preserves_provenance(self):
  p=S/'artifacts/history/pre-r4/SUPERSEDED.json';self.assertTrue(p.is_file(),'HISTORY_LABEL_MISSING')
  x=json.loads(p.read_bytes());self.assertEqual(x['status'],'superseded');self.assertFalse(x['installAllowed'])
  self.assertEqual(x['sha256'],OLD);self.assertEqual(x['currentSha256'],CURRENT)
  self.assertEqual(len(x['differentBodyMembers']),4)
 def test_current_owner_on_main_is_admitted(self):
  for name in WORKFLOWS:
   with self.subTest(name=name):self.assertTrue(guard(workflow(name),REPO,'refs/heads/main'))
 def test_old_owner_forks_and_other_refs_remain_denied(self):
  for name in WORKFLOWS:
   for repo,ref in [('Lance-QwQ/DSH-SEP','refs/heads/main'),('fork/DSH-SEP','refs/heads/main'),(REPO,'refs/heads/test'),(REPO,'refs/tags/v1')]:
    with self.subTest(name=name,repo=repo,ref=ref):self.assertFalse(guard(workflow(name),repo,ref))
 def test_live_workflow_endpoints_and_release_guards(self):
  for name in WORKFLOWS:
   text=workflow(name);ast.parse(inline(text));self.assertIn('workflow_dispatch:',text)
   self.assertNotRegex(text,r'^\s{2}(push|pull_request):')
   self.assertIn('github.ref == \'refs/heads/main\'',text)
   self.assertIn('Lanxe-QwQ/DSH-SEP',inline(text))
  text=workflow(WORKFLOWS[0]);self.assertIn("repo='Lanxe-QwQ/DSH-SEP'",text)
  self.assertIn("row['draft'] is True",text);self.assertIn('27cc3bba0a935fc7adbb9a23b30fbb200066fa2d32646774ba7248ae9f3481e1',text)
 def test_beta2_uses_explicit_hash_bound_single_transform(self):
  fn=adaptation();self.assertIsNotNone(fn,'FROZEN_RELAY_OWNER_ADAPTER_MISSING')
  raw=canonical_source('release/v0.2.1-beta.2/relay.py')
  self.assertEqual(hashlib.sha256(raw).hexdigest(),'66440f56b84d4cc7d8388601721b64412845989f5e6c56aa81da8482a6350829')
  out=fn('relay.py',raw);self.assertEqual(hashlib.sha256(out).hexdigest(),'d5f7715f57a640b1f66912f67b6f3f075d073db055ef3617e09fced529fa68b9')
  self.assertIn(b"REPO='Lanxe-QwQ/DSH-SEP';API=",out);compile(out,'<derived-relay>','exec')
  self.assertEqual(fn('RELAY-PLAN.json',b'fixed-input'),b'fixed-input')
 def test_beta2_rejects_tampering_and_reapplication(self):
  fn=adaptation();self.assertIsNotNone(fn,'FROZEN_RELAY_OWNER_ADAPTER_MISSING')
  raw=canonical_source('release/v0.2.1-beta.2/relay.py')
  for bad in [raw+b'\n',raw.replace(b'REPO=',b'OTHER='),fn('relay.py',raw)]:
   with self.subTest(bytes=len(bad)),self.assertRaises(AssertionError):fn('relay.py',bad)
 def test_historical_release_inputs_remain_exact(self):
  for name,pin in [('relay.py','66440f56b84d4cc7d8388601721b64412845989f5e6c56aa81da8482a6350829'),('RELAY-PLAN.json','75dd5684d9844290dfcaaa68db5a7327d6ea8c66486456504a1274eb788509a8'),('zip_rewrite.py','f7cd1ad840b58119ded24e87f50862f50e05b06e2322ae0a82fc2e9d8eef2261')]:
   self.assertEqual(hashlib.sha256(canonical_source('release/v0.2.1-beta.2/'+name)).hexdigest(),pin)
 def test_root_repository_metadata_and_download_links(self):
  x=json.loads((R/'package.json').read_bytes());self.assertEqual(x['repository']['url'],'git+https://github.com/'+REPO+'.git')
  text=(R/'README.md').read_text(encoding='utf-8');self.assertNotIn('github.com/Lance-QwQ/DSH-SEP',text)
  self.assertIn('github.com/'+REPO+'/releases/tag/v0.2.1-beta.3',text)
 def test_frozen_helper_and_explicit_hygiene_disposition(self):
  self.assertEqual(sha(R/'tools/rc2-adaptation/macos/runtime-helper.mjs'),'261a337751be3e2f0f706b267cbb7bde5509a68c436b6f202ca39b2146ace4c2')
  p=R/'tools/rc2-adaptation/review-followup/GENERATED-PATHS.json';self.assertTrue(p.is_file(),'FIXED_HELPER_DISPOSITION_MISSING')
  x=json.loads(p.read_bytes());self.assertEqual(x['disposition'],'retained-frozen-generated-input');self.assertTrue(x['moduleIdsAlsoContainPaths']);self.assertFalse(x['rebuilt'])
 def test_tested_runtime_and_four_delivery_archives_are_unchanged(self):
  p=R/'tools/rc2-adaptation/CANDIDATE-SOURCE.json';x=json.loads(p.read_bytes());self.assertEqual(len(x['files']),445)
  for row in x['files']:
   p=R/'tools/rc2-adaptation/candidate'/row['path'];self.assertEqual(p.stat().st_size,row['bytes']);self.assertEqual(sha(p),row['sha256'])
  x=json.loads((R/'tools/rc2-adaptation/FINAL-VERIFICATION.json').read_bytes());self.assertEqual(len(x['assets']),4)
  for row in x['assets']:
   p=S/row['path'];self.assertEqual(p.stat().st_size,row['bytes']);self.assertEqual(sha(p),row['sha256'])

if __name__=='__main__':unittest.main(verbosity=2)
