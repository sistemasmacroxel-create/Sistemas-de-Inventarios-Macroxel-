from pathlib import Path
import sys
p=Path('docs/sistema-inventario.js')
s=p.read_text(encoding='utf-8')
tag='mxAbxBackgroundPublisherV284'
if tag in s:
 print('Publicador ya integrado v284')
 sys.exit(0)
mark='/* ===== MACROXEL CANONICAL SOURCE: mx-antibiotic-capacity-publisher-v146 ===== */'
assert s.count(mark)==1
head,tail=s.split(mark,1)
end=tail.find('/* ===== MACROXEL CANONICAL SOURCE:',10)
assert end>0
body,rest=tail[:end],tail[end:]
assert body.count('if(document.hidden)return false;')==1
body=body.replace('if(document.hidden)return false;',"""// mxAbxBackgroundPublisherV284
    if(document.hidden&&!force&&Date.now()-lastPublishedAt<10*60*1000)return false;""",1)
assert body.count('if(!document.hidden)schedule(false,15000);')==1
body=body.replace('if(!document.hidden)schedule(false,15000);','schedule(false,15000);',1)
p.write_text(head+mark+body+rest,encoding='utf-8')
print('Principal ABX v284',p.stat().st_size)
