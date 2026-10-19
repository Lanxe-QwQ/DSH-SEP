from pathlib import Path
import hashlib,json,re,zipfile
S=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');E=S/'evidence';scan=json.loads((E/'MAC-PRIVACY-SCAN-r12.json').read_bytes());H=lambda b:hashlib.sha256(b).hexdigest();prefix='DSH SEP Installer.app/Contents/Resources/payload/DSH SEP.app/Contents/Resources/product/payload/host/node_modules/'
assert scan['archiveUnchanged'] and not scan['filenameFindings'];rows=[];contexts={}
with zipfile.ZipFile(scan['archive']) as z:
 for item in sorted(scan['findings'],key=lambda r:(r['entry'],r['offset'])):
  name=item['entry'];offset=item['offset'];start=max(0,offset-128)
  with z.open(name) as f:f.seek(start);context=f.read(8192)
  local=offset-start;pattern=item['pattern'];r={**item,'contextSha256':H(context[:local+256]),'scope':'classification of this exact bounded signature hit only'}
  if pattern=='private-key-header':
   header=b'-----BEGIN PRIVATE KEY-----';assert context[local:local+len(header)]==header;after=context[local+len(header):local+len(header)+4]
   assert after.startswith((b'\x00',b"'",b'"')),(name,after.hex())
   r.update(classification='nonsecret-format-marker',evidence='header is immediately terminated by a string quote or NUL, not followed by a PEM key body',followingBytesHex=after.hex())
  elif pattern=='provider-token-like':
   m=re.match(rb'sk-[A-Za-z0-9_-]{20,}',context[local:]);assert m and H(m[0])==item['matchSha256']
   assert re.fullmatch(rb'sk-(?:[a-z]+-)+[a-z]+',m[0]),'opaque token must not be auto-classified'
   if name.startswith(prefix) and name.endswith('/emacs-lisp.mjs'):
    reference=S/'host-rc2/node_modules/@shikijs/langs/dist/emacs-lisp.mjs';b=z.read(name);assert H(b)==H(reference.read_bytes());r.update(referenceSha256=H(b),reference='same exact public @shikijs/langs emacs-lisp grammar bytes in locked RC.2 official dependencies')
    contexts['grammar']=context[local-64:local+256]
   else:
    assert name.endswith('/app.asar')
    referenceEntry=prefix+'@shikijs/langs/dist/emacs-lisp.mjs';b=z.read(referenceEntry);at=b.index(m[0]);assert b[at-64:at+256]==context[local-64:local+256];r.update(referenceEntry=referenceEntry,referenceSha256=H(b),evidence='same grammar identifier and exact 320-byte context embedded in ASAR')
   r.update(classification='public-grammar-identifier',identifier=m[0].decode('ascii'))
  else:raise AssertionError('unreviewed pattern')
  rows.append(r)
assert len(rows)==6
report=dict(schema=1,status='pass',scope='defined-signature privacy review of this exact RC.2 installer, not comprehensive semantic/binary privacy certification',archiveSha256=scan['sha256'],scanRecordSha256=H((E/'MAC-PRIVACY-SCAN-r12.json').read_bytes()),rawScanStatus=scan['status'],rawSignatureHits=6,reviewedNonsecretHits=6,unresolved=0,filenameFindings=0,knownPersonalPathHits=0,githubTokenHits=0,comprehensivePrivacyAudit=False,rows=rows)
with (E/'MAC-PRIVACY-REVIEW-r12.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({k:report[k] for k in ['status','rawScanStatus','rawSignatureHits','reviewedNonsecretHits','unresolved','filenameFindings']}))
