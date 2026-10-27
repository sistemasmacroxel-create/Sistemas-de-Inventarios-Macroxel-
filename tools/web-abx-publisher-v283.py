from pathlib import Path
import re
p=Path('docs/sistema-inventario.js')
s=p.read_text(encoding='utf-8')
assert 'catalogAbxKeys' not in s and 'mx-primary-stock-published' not in s, 'El publicador ya cambió'
def once(a,b):
 global s
 n=s.count(a)
 if n!=1:raise AssertionError(f'Referencia incorrecta ({n}): {a[:90]}')
 s=s.replace(a,b,1)
once("lastSignature='',timer=0", "lastSignature='',lastPublishedAt=0,timer=0")
s,n=re.subn(r'(?m)^  const idleYield=\(\)=>.*$', "  const idleYield=()=>new Promise(resolve=>{try{if(typeof requestIdleCallback==='function')requestIdleCallback(()=>resolve(),{timeout:220});else setTimeout(resolve,0)}catch(_e){setTimeout(resolve,0)}});",s)
assert n==1,n
once("const [inventory,abHist]=await Promise.all([loadInventory(!!force),loadAntibioticHistory()]),histKeys=", "const [inventory,abHist,masterCatalog]=await Promise.all([loadInventory(!!force),loadAntibioticHistory(),window.idbAll?.('cpm').catch(()=>[])||Promise.resolve([])]),catalogAbxKeys=new Set((masterCatalog||[]).filter(isAbx).map(claveOf).map(NORM).filter(Boolean)),histKeys=")
once("prev.abx=prev.abx||isAbx(r)||histKeys.has(key);", "prev.abx=prev.abx||isAbx(r)||histKeys.has(key)||catalogAbxKeys.has(key);")
once("if(i%8===0)await new Promise(resolve=>setTimeout(resolve,0));", "if(i%6===0)await idleYield();")
once("sig===lastSignature)return false", "sig===lastSignature&&Date.now()-lastPublishedAt<8*60*1000)return false")
once("lastSignature=sig;return true;", "lastSignature=sig;lastPublishedAt=Date.now();return true;")
once("  window.mxPublishAntibioticCapacityV146=publish;", "  window.mxPublishAntibioticCapacityV146=publish;\n  window.addEventListener('mx-primary-stock-published',ev=>{if(TXT(ev?.detail?.branch).toUpperCase()===branch())schedule(true,1500)});\n  window.addEventListener('online',()=>schedule(true,3500));window.addEventListener('focus',()=>{if(!document.hidden&&Date.now()-lastPublishedAt>3*60*1000)schedule(true,3500)});")
assert s.count('schedule(true,90000)')==2
s=s.replace('schedule(true,90000)','schedule(true,12000)')
once('setInterval(()=>schedule(false,30000),1800000);', "setInterval(()=>{if(!document.hidden)schedule(false,15000);},8*60*1000);")
old='localStorage.setItem(invSeqKey(),String(seq));'
assert s.count(old)==4
s=s.replace(old, old+"try{window.dispatchEvent(new CustomEvent('mx-primary-stock-published',{detail:{branch:suc,seq}}))}catch(_e){}")
p.write_text(s,encoding='utf-8')
q=Path('docs/index.html')
h=q.read_text(encoding='utf-8')
needle='sistema-inventario.js?v=v278-inventario-visores-autoritativo-20261026'
assert h.count(needle)==1
q.write_text(h.replace(needle,'sistema-inventario.js?v=v283-abx-control-central-20261026'),encoding='utf-8')
print('Publicador actualizado, versión web invalidada')
