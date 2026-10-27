from pathlib import Path
import re

p=Path("docs/sistema-inventario.js")
s=p.read_text(encoding="utf-8")
if "mxAbxCapacityHandShakeV285" not in s:
    before="      const sig=signatureOf(items);if(!force&&sig===lastSignature&&Date.now()-lastPublishedAt<8*60*1000)return false;"
    after="""      // mxAbxCapacityHandShakeV285: confirmar la misma revision de Inventario Principal.
      const actualRev=capacityInventoryRevision(),suc=branch();
      let confirmedMeta=null;
      try{if(typeof window.mxGetJson==='function')confirmedMeta=await window.mxGetJson('/inventory_cpm_totals/'+encodeURIComponent(suc)+'/meta')}catch(e){console.warn('[ABX V285] Lectura:',e?.message||e)}
      const same=confirmedMeta?.sourceAuthority==='INVENTARIO_PRINCIPAL'&&NUM(confirmedMeta?.seq)>0&&TXT(confirmedMeta?.revision)===actualRev;
      if(!same){
        console.warn('[ABX V285] Esperando revision de inventario antes de confirmar capacidad.');
        if(Date.now()-lastInventoryRepairAt>240000&&typeof window.mxPublicarInventarioFirebase==='function'){
          lastInventoryRepairAt=Date.now();
          Promise.resolve().then(()=>window.mxPublicarInventarioFirebase(true)).then(()=>schedule(true,3500)).catch(e=>console.warn('[ABX V285]',e?.message||e));
        }
        return false;
      }
      const sig=actualRev+'|'+confirmedMeta.seq+'|'+signatureOf(items);
      if(!force&&sig===lastSignature&&Date.now()-lastPublishedAt<6*60*1000)return false;"""
    assert s.count(before)==1,"Bloque ABX del principal diferente; no sobrescribir."
    s=s.replace(before,after,1)
    key="let busy=null,lastSignature='',lastPublishedAt=0,timer=0,pendingForce=false,lastUserAction=Date.now();"
    assert s.count(key)==1
    s=s.replace(key,"let busy=null,lastSignature='',lastPublishedAt=0,timer=0,pendingForce=false,lastUserAction=Date.now(),lastInventoryRepairAt=0;",1)
    key="inventorySeq=NUM(localStorage.getItem('mx_cpm_inventory_seq_v1010::'+branch()))"
    assert s.count(key)==1
    s=s.replace(key,"inventorySeq=NUM(confirmedMeta.seq)",1)
    key="payload={schemaVersion:278,inventorySeq,inventoryRevision:capacityInventoryRevision()"
    assert s.count(key)==1
    s=s.replace(key,"payload={schemaVersion:285,inventorySeq,inventoryRevision:actualRev",1)
    marker="      const now=new Date(),inventorySeq=NUM(confirmedMeta.seq),"
    assert s.count(marker)==1
    i=s.index(marker)
    head,tail=s[:i],s[i:]
    key="      await window.mxPublishJson("
    assert tail.count(key)>=1
    tail=tail.replace(key,"      const published=await window.mxPublishJson(",1)
    key="payload);await window.mxPublishJson("
    assert tail.count(key)>=1
    tail=tail.replace(key,"payload);if(published!==true)throw new Error('Firebase no confirmo capacidad');await window.mxPublishJson(",1)
    s=head+tail
    p.write_text(s,encoding="utf-8")
p=Path("docs/index.html")
html=p.read_text(encoding="utf-8")
html=re.sub(r'sistema-inventario\.js\?v=[^"\s<>]+',"sistema-inventario.js?v=v285-abx-confirmado",html)
p.write_text(html,encoding="utf-8")
assert "mxAbxCapacityHandShakeV285" in s
