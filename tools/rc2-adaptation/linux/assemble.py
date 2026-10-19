from pathlib import Path
import os,shutil,json,hashlib,subprocess
os.umask(0o077)
root=Path('/opt/dsh-sep-cross-platform/rc2-adaptation-20261018-r1')
old=Path('/opt/dsh-sep-cross-platform/alpha2-portable-finalization-archive-r51/payload')
out=root/'payload-r1';assert not out.exists()
node='/opt/dsh-sep-cross-platform/runtime/bin/node'
check=subprocess.run([node,'--input-type=module','-e',"import{verifyPayload}from'"+(old/'src/linux-install.mjs').as_uri()+"';await verifyPayload('"+str(old)+"','1f087d0680ca3d0c1b13a38983d564b73c2a0e068b6ec1d9eb87fbc55ca5b196');"],capture_output=True,text=True);assert check.returncode==0,check.stderr
shutil.copytree(old,out,symlinks=True,ignore=lambda d,names:{n for n in names if Path(d)==old and n in ['host','src','desktop','BUILD.json','PAYLOAD-MANIFEST.json']})
shutil.copytree(root/'host',out/'host',symlinks=True);shutil.copytree(root/'carrier',out/'src');shutil.copytree(root/'native-desktop',out/'desktop')
origins=[]
def edit(path,from_,to,count=1):
 raw=path.read_bytes();text=raw.decode();assert text.count(from_)==count,(path,from_,text.count(from_));result=text.replace(from_,to).encode();path.write_bytes(result);origins.append({'path':str(path.relative_to(out)),'sourceSha256':hashlib.sha256(raw).hexdigest(),'resultSha256':hashlib.sha256(result).hexdigest(),'transforms':[{'from':from_,'to':to,'count':count}]})
edit(out/'src/linux-launch.mjs',"dshVersion:'0.2.1-alpha.2'","dshVersion:'0.2.1-rc.2'")
oldref="join(program,'host/node_modules/@deepseek-ai/dsh-client-ui-settings-memory/lib/index.js')"
edit(out/'src/linux-standalone-profile.mjs',oldref,"join(program,'host/node_modules/dsh-sep-bundle/bundle/modules/ui-settings-memory/lib/index.js')")
ui=out/'host/node_modules/dsh-sep-bundle/bundle/modules/ui-settings-memory/package.json';before=ui.read_bytes();manifest=json.loads(before);manifest['engines']={**manifest.get('engines',{}),'dsh':'0.2.1-rc.2'}
for key in manifest.get('peerDependencies',{}):
 if key.startswith('@deepseek-ai/dsh-'):manifest['peerDependencies'][key]='0.2.0-rc.2 || 0.2.1-rc.2' if key=='@deepseek-ai/dsh-invariants' else '0.2.1-rc.2'
ui.write_text(json.dumps(manifest,indent=2)+'\n');origins.append({'path':str(ui.relative_to(out)),'sourceSha256':hashlib.sha256(before).hexdigest(),'resultSha256':hashlib.sha256(ui.read_bytes()).hexdigest(),'reason':'exact RC.2 native profile declaration'})
os.symlink('host/node_modules',out/'node_modules');os.symlink('../host/node_modules',out/'desktop/node_modules')
build={'schema':1,'buildId':'rc2-linux-adapter.1','dsh':'0.2.1-rc.2','sepBase':'0.2.1-beta.3-rc2-adapter.1','scope':'Ubuntu24.04 ext4 isolated preview; validation incomplete','officialMainUnmodified':False,'desktopMainOrigin':'desktop/RC2-ORIGIN.json','automaticUpdate':False,'privateDataIncluded':False}
(out/'BUILD.json').write_text(json.dumps(build,indent=2)+'\n');(root/'LINUX-DERIVATION.json').write_text(json.dumps({'schema':1,'basePayloadManifestSha256':'1f087d0680ca3d0c1b13a38983d564b73c2a0e068b6ec1d9eb87fbc55ca5b196','oldProgramChanged':False,'origins':origins,'build':build},indent=2)+'\n')
print(json.dumps({'status':'assembled','output':str(out),'notVerified':['new payload installation','RC.2 desktop','Wayland interaction']}))
