import hashlib,json,os,sys,time,urllib.request,zipfile
from pathlib import Path
request=json.loads(sys.stdin.read())
target=Path(request['target']);assert target.is_absolute() and target.is_relative_to(Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1'))
assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({'http':'http://127.0.0.1:7890','https':'http://127.0.0.1:7890'}))
h=hashlib.sha256();n=0
# Retry only opening a read-only connection, before creating any output file.
# A mid-body failure preserves its partial file and is never overwritten.
for attempt in range(3):
 try:
  response=opener.open(request['url'],timeout=120);break
 except Exception:
  if attempt==2:raise
  time.sleep(attempt+1)
with response,target.open('xb') as dest:
 while True:
  b=response.read(1024*1024)
  if not b:break
  n+=len(b);assert n<=request['bytes'];h.update(b);dest.write(b)
 dest.flush();os.fsync(dest.fileno())
assert n==request['bytes'] and h.hexdigest()==request['sha256']
rows=[]
with zipfile.ZipFile(target) as z:
 for i in z.infolist():
  if i.is_dir():continue
  row={'path':i.filename,'bytes':i.file_size};hash_=hashlib.sha256()
  with z.open(i) as f:
   for b in iter(lambda:f.read(1024*1024),b''):hash_.update(b)
  row['sha256']=hash_.hexdigest();rows.append(row)
  if request.get('extractSmall') and i.file_size<=16777216:
   dest=target.parent/'members'/i.filename.replace('/','--');dest.parent.mkdir(exist_ok=True)
   with z.open(i) as src,dest.open('xb') as out:
    for b in iter(lambda:src.read(1024*1024),b''):out.write(b)
report={'schema':1,'status':'pass','artifactId':request['id'],'path':str(target),'bytes':n,'sha256':h.hexdigest(),'members':rows}
with target.with_suffix('.verified.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({'status':'pass','artifactId':request['id'],'bytes':n,'sha256':h.hexdigest(),'members':len(rows)}))
