from pathlib import Path
import base64, gzip, re

JS=Path("docs/sistema-inventario.js")
INDEX=Path("docs/index.html")
START='/* ===== MACROXEL V151: KITS QUIRURGICOS + HISTORIAL EDITABLE + PDF MANUAL ===== */'
END='/* ===== MACROXEL FINANCIERO OPCIONAL v153 ===== */'

payload=''.join(
    Path(f"tools/v241_payload_{i:02d}.txt").read_text(encoding="utf-8").strip()
    for i in range(5)
)
new_block=gzip.decompress(base64.b64decode(payload)).decode("utf-8")
if not new_block.startswith(START):
    raise SystemExit("Payload v241 inválido")

s=JS.read_text(encoding="utf-8")
a=s.find(START)
b=s.find(END,a)
if a < 0 or b < 0:
    raise SystemExit("No se encontró el bloque de servicio quirúrgico")
s=s[:a]+new_block+s[b:]
marker="/* ===== MACROXEL V241 WEB SINCRONIZADO · SERVICIO + OJO + KITS SIN BLOQUEO ===== */"
if marker not in s:
    s += "\n"+marker+"\n"
for required in ['id="mxQxSrvEye"','ojo_operacion:paciente.ojo','function qLoanLabelHtml(group)','serviceShortageTotal(shortages=[])']:
    if required not in s:
        raise SystemExit("Validación v241 falló: "+required)
JS.write_text(s,encoding="utf-8")

h=INDEX.read_text(encoding="utf-8")
pat=r'sistema-inventario\.js\?v=[^"\']+'
if re.search(pat,h):
    h=re.sub(pat,'sistema-inventario.js?v=v241-web-sync',h,count=1)
elif 'src="sistema-inventario.js"' in h:
    h=h.replace('src="sistema-inventario.js"','src="sistema-inventario.js?v=v241-web-sync"',1)
else:
    raise SystemExit("No se encontró la referencia JS en index.html")
INDEX.write_text(h,encoding="utf-8")
print("WEB v241 sincronizado")
