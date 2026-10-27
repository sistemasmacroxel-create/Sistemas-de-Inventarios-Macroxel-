from pathlib import Path
import re

def patch():
    target='web'
    ip=Path('docs/index.html')
    jp=Path('docs/sistema-inventario.js')
    html=ip.read_text(encoding='utf-8')
    js=jp.read_text(encoding='utf-8')
    if 'mxInvUbicacionCoincideV277' in js and 'id="invFiltroUbic"' in html:
        print('Filtro por ubicación ya presente, sin cambios')
        return
    def replace_once(original,from_,to_,what):
        n=original.count(from_)
        if n!=1: raise AssertionError(f'{target} {what}: {n} matches')
        return original.replace(from_,to_,1)
    html=replace_once(html,'''grid-template-columns:minmax(300px,1fr) 185px 145px 150px 130px 175px;''', '''grid-template-columns:minmax(220px,1fr) 165px 135px 155px 145px 130px 165px;''', 'desktop grid')
    html=replace_once(html,'''#view-inventario #invFiltroStock{width:145px !important;}''','''#view-inventario #invFiltroStock{width:145px !important;}
#view-inventario #invFiltroUbic{width:155px !important;}''', 'select width')
    html=replace_once(html,'''@media(max-width:1320px){
  #view-inventario .mx-inv-toolbar{
    grid-template-columns:minmax(270px,1fr) 170px 135px 145px 125px 165px;
  }
}''','''@media(max-width:1400px){
  #view-inventario .mx-inv-toolbar{display:flex !important; flex-wrap:wrap !important;}
  #view-inventario #invBusca{flex:1 1 260px !important;}
  #view-inventario #invFiltroSem{flex:1 1 170px !important; width:auto !important;}
  #view-inventario #invFiltroStock{flex:1 1 135px !important; width:auto !important;}
  #view-inventario #invFiltroUbic{flex:1 1 165px !important; width:auto !important;}
  #view-inventario .mx-inv-toolbar > .btn,
  #view-inventario .mx-inv-toolbar > .mx-inv-export-wrap{flex:1 1 140px !important; width:auto !important;}
}''','responsive')
    html=replace_once(html, '''#view-inventario #invFiltroStock{flex:1 1 140px !important;width:auto !important;}''','''#view-inventario #invFiltroStock{flex:1 1 140px !important;width:auto !important;}
  #view-inventario #invFiltroUbic{flex:1 1 165px !important;width:auto !important;}''','mobile style')
    html=replace_once(html,'''<option value="cero">⭕ En ceros</option></select><button class="btn" id="btnInvTransferSel"''','''<option value="cero">⭕ En ceros</option></select><select class="select" id="invFiltroUbic" title="Filtrar inventario por ubicación" aria-label="Filtrar por ubicación"><option value="">📍 Ubicación: Todas</option></select><button class="btn" id="btnInvTransferSel"''','html select')

    # Canonical helper used both on the visible table and on export datasets.
    anchor='''async function drawInventario(opts={}){'''
    util='''// Filtro de ubicación de Inventario (v277). No escribe ni modifica existencias.
const MX_INV_SIN_UBICACION_V277 = '__SIN_UBICACION__';
function mxInvUbicacionTextoV277(r){
  if(!r) return '';
  for(const value of [r.ubicacion,r['ubicación'],r.UBICACION,r['UBICACIÓN']]){
    if(value != null && String(value).trim()) return String(value).trim().replace(/\s+/g,' ');
  }
  return '';
}
function mxInvUbicacionClaveV277(value){
  return String(value ?? '').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').trim().replace(/\\s+/g,' ').toLocaleUpperCase('es-MX');
}
function mxInvUbicacionCoincideV277(r){
  const selected = String(document.getElementById('invFiltroUbic')?.value || '');
  if(!selected) return true;
  const normalized = mxInvUbicacionClaveV277(mxInvUbicacionTextoV277(r));
  return selected === MX_INV_SIN_UBICACION_V277 ? !normalized : normalized === selected;
}
function mxInvUbicacionActualizarOpcionesV277(data){
  const sel=document.getElementById('invFiltroUbic');
  if(!sel) return;
  const prev=sel.value;
  const uniq=new Map();
  let hasEmpty=false;
  for(const row of Array.isArray(data)?data:[]){
    const label=mxInvUbicacionTextoV277(row);
    const key=mxInvUbicacionClaveV277(label);
    if(!key){hasEmpty=true;continue;}
    if(!uniq.has(key))uniq.set(key,label);
  }
  const entries=Array.from(uniq.entries()).sort((a,b)=>a[1].localeCompare(b[1],'es',{sensitivity:'base',numeric:true}));
  // No reconstruir el select en cada pulsación si las ubicaciones no cambiaron.
  const signature=JSON.stringify([hasEmpty,entries]);
  if(sel.dataset.mxUbicSignatureV277!==signature){
    const frag=document.createDocumentFragment();
    const all=document.createElement('option');all.value='';all.textContent='📍 Ubicación: Todas';frag.appendChild(all);
    for(const [key,label] of entries){const opt=document.createElement('option');opt.value=key;opt.textContent=label;frag.appendChild(opt);}
    if(hasEmpty){const empty=document.createElement('option');empty.value=MX_INV_SIN_UBICACION_V277;empty.textContent='Sin ubicación';frag.appendChild(empty);}
    sel.replaceChildren(frag);
    sel.dataset.mxUbicSignatureV277=signature;
  }
  sel.value=prev;
  if(sel.value!==prev)sel.value='';
}
'''
    js=replace_once(js,anchor,util+'\n'+anchor,'helper')
    js=replace_once(js,'''  const q = ($('#invBusca')?.value || '').toLowerCase().trim();
  const sem''','''  mxInvUbicacionActualizarOpcionesV277(data);
  const q = ($('#invBusca')?.value || '').toLowerCase().trim();
  const sem''','update options')
    js=replace_once(js,'''    return matchQ && matchSem && matchStock;''','''    return matchQ && matchSem && matchStock && mxInvUbicacionCoincideV277(x);''','main inventory filter')
    js=replace_once(js,'''const hayFiltro = Boolean(q || sem || stock);''','''const hayFiltro = Boolean(q || sem || stock || document.getElementById('invFiltroUbic')?.value);''','sum total')
    js=replace_once(js,'''<td>${ubic}</td>
      <td class="mx-sema-cell">''','''<td class="mx-inv-ubic">${ubic}</td>
      <td class="mx-sema-cell">''','location td')
    js=replace_once(js,'''  bindResetAndDraw('invFiltroStock', 'change');''','''  bindResetAndDraw('invFiltroStock', 'change');
  bindResetAndDraw('invFiltroUbic', 'change');''','event')
    js=replace_once(js,'''    const stock = (qs('#invFiltroStock')?.value || '').trim().toLowerCase();

    const rows = qsa('#tblInv tbody tr');''','''    const stock = (qs('#invFiltroStock')?.value || '').trim().toLowerCase();

    const rows = qsa('#tblInv tbody tr');''','apply filter region') if False else js
    js=replace_once(js,'''      tr.style.display = (matchQ && matchSem && matchStock) ? '' : 'none';''','''      const chosenUbic=document.getElementById('invFiltroUbic')?.value || '';
      const currentUbic=tr.querySelector('.mx-inv-ubic')?.textContent || tds[tds.length-2]?.textContent || '';
      const matchUbic=!chosenUbic || (chosenUbic===MX_INV_SIN_UBICACION_V277 ? !mxInvUbicacionClaveV277(currentUbic) : mxInvUbicacionClaveV277(currentUbic)===chosenUbic);
      tr.style.display = (matchQ && matchSem && matchStock && matchUbic) ? '' : 'none';''','legacy apply filters')
    js=replace_once(js,'''    if(stock) stock.addEventListener('change', applyInvFilters);
    const search = qs('#invBusca');''','''    if(stock) stock.addEventListener('change', applyInvFilters);
    const location = qs('#invFiltroUbic');
    if(location) location.addEventListener('change', applyInvFilters);
    const search = qs('#invBusca');''','legacy events')
    js=replace_once(js,'''    const fs = _qs('#invFiltroStock');
    if(fs) fs.addEventListener('change', ()=>{ try{ clearSelection(); refreshSelectionVisibility(); }catch(_){} });''','''    const fs = _qs('#invFiltroStock');
    if(fs) fs.addEventListener('change', ()=>{ try{ clearSelection(); refreshSelectionVisibility(); }catch(_){} });
    const fu = _qs('#invFiltroUbic');
    if(fu) fu.addEventListener('change', ()=>{ try{ clearSelection(); refreshSelectionVisibility(); }catch(_){} });''','selection event')
    # Three export code paths respect the location filter. Keep existing export semantics for other filters.
    js=replace_once(js,'''      if(filtroStock === 'cero' && total !== 0) return false;
      return true;''','''      if(filtroStock === 'cero' && total !== 0) return false;
      if(!mxInvUbicacionCoincideV277(r)) return false;
      return true;''','multi sheet Excel')
    js=replace_once(js,'''  inv = Array.isArray(inv) ? inv : [];
  if(inv.length===0){''','''  inv = Array.isArray(inv) ? inv : [];
  try{const overlay=mxApplyUbicMapToInventory(inv);if(overlay?.arr)inv=overlay.arr;}catch(_e){}
  inv=inv.filter(mxInvUbicacionCoincideV277);
  if(inv.length===0){''','pdf filter')
    js=replace_once(js,'''    data = Array.isArray(data) ? data.slice() : [];
    try{
      if(typeof mxSortInventarioInPlace==='function') mxSortInventarioInPlace(data);''','''    data = Array.isArray(data) ? data.slice() : [];
    try{const overlay=mxApplyUbicMapToInventory(data);if(overlay?.arr)data=overlay.arr;}catch(_e){}
    try{
      if(typeof mxSortInventarioInPlace==='function') mxSortInventarioInPlace(data);''','xlsx 1 overlay')
    js=replace_once(js,'''      return okQ && okSem && okStock;''','''      return okQ && okSem && okStock && mxInvUbicacionCoincideV277(r);''','xlsx 1 filter')
    js=replace_once(js,'''        data = Array.isArray(data) ? data.slice() : [];
        try{
          if(typeof mxSortInventarioInPlace==='function') mxSortInventarioInPlace(data);''','''        data = Array.isArray(data) ? data.slice() : [];
        try{const overlay=mxApplyUbicMapToInventory(data);if(overlay?.arr)data=overlay.arr;}catch(_e){}
        try{
          if(typeof mxSortInventarioInPlace==='function') mxSortInventarioInPlace(data);''','xlsx 2 overlay')
    js=replace_once(js,'''          return okQ && okStock;''','''          return okQ && okStock && mxInvUbicacionCoincideV277(r);''','xlsx 2 filter')
    js=replace_once(js,'''      if(q) parts.push('FILTRADO');''','''      const locationFilter=document.getElementById('invFiltroUbic')?.value || '';
      if(locationFilter) parts.push('UBICACION_FILTRADA');
      if(q) parts.push('FILTRADO');''','export naming')
    js=replace_once(js,'''['invBusca','invFiltroSem','invFiltroStock'].forEach(function(id){''','''['invBusca','invFiltroSem','invFiltroStock','invFiltroUbic'].forEach(function(id){''','reviewed bindings')

    html,count=re.subn(r'sistema-inventario\.js\?v=[^"\s<>]+','sistema-inventario.js?v=v279-filtro-ubicacion-web-20261026',html)
    if count != 1: raise AssertionError(f'No se encontró versión de JavaScript (coincidencias: {count})')
    jp.write_text(js,encoding='utf-8');ip.write_text(html,encoding='utf-8')
    print('patched',target,'js',len(js),'html',len(html))

patch()