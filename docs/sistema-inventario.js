

/* ===== MACROXEL V246 · LOGOS PDF QUIROFANO TOMADOS DIRECTAMENTE DE CONFIGURACION ===== */
(function(){
  'use strict';
  if(window.__mxQxPdfConfiguredLogosV246)return;
  window.__mxQxPdfConfiguredLogosV246=true;
  const KEY='mx_collective_pdf_assets_principal_v1';
  const ROOT='/collective_pdf_assets';
  const qtxt=v=>v==null?'':String(v).trim();
  const readLocal=()=>{try{return JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(_e){return{}}};
  const branch=()=>{try{return String(window.mxGetSucursalFromLicense?.()||'HGAM').trim().toUpperCase()||'HGAM'}catch(_e){return'HGAM'}};
  const previewSrc=id=>{try{const el=document.getElementById(id);return qtxt(el?.currentSrc||el?.src||'')}catch(_e){return''}};
  const isUseful=src=>!!src && !/^blob:null/i.test(src);

  async function loadPng(src){
    src=qtxt(src);if(!isUseful(src))return'';
    try{
      if(typeof mxOrderPdfLoadImage==='function'){
        const d=await Promise.race([Promise.resolve(mxOrderPdfLoadImage(src)),new Promise(r=>setTimeout(()=>r(''),2200))]);
        if(d)return d;
      }
    }catch(_e){}
    try{
      const r=await fetch(src,{cache:'no-store'});if(!r.ok)return'';const b=await r.blob();
      const data=await new Promise((resolve,reject)=>{const fr=new FileReader();fr.onload=()=>resolve(String(fr.result||''));fr.onerror=reject;fr.readAsDataURL(b)});
      if(typeof mxOrderPdfLoadImage==='function')return await mxOrderPdfLoadImage(data);
      return data;
    }catch(_e){return''}
  }
  async function firstValid(list){for(const src of list){const d=await loadPng(src);if(d)return d}return''}
  async function remoteAssets(){
    let remote={};
    try{if(typeof window.mxGetJson==='function' && qtxt(window.mxRemoteDbUrl?.()))remote=await window.mxGetJson(`${ROOT}/${encodeURIComponent(branch())}`)||{}}catch(_e){}
    return remote&&typeof remote==='object'?remote:{};
  }
  async function configuredSources(){
    let getter={};try{if(typeof window.mxGetCollectivePdfAssets==='function')getter=await window.mxGetCollectivePdfAssets()||{}}catch(_e){}
    const local=readLocal(),remote=await remoteAssets();
    return {
      left:[remote.left,getter.left,local.left,previewSrc('mxColImgLeftPreview'),remote.collective,getter.collective,local.collective,previewSrc('mxColImgCollectivePreview')],
      right:[remote.right,getter.right,local.right,previewSrc('mxColImgRightPreview'),'./logo_macroxel_hps.png'],
      collective:[remote.collective,getter.collective,local.collective,previewSrc('mxColImgCollectivePreview')],
      footer:[remote.footer,getter.footer,local.footer,previewSrc('mxColImgFooterPreview')]
    };
  }
  async function resolveLogos(){
    const src=await configuredSources();
    let [left,right,collective,footer]=await Promise.all([firstValid(src.left),firstValid(src.right),firstValid(src.collective),firstValid(src.footer)]);
    let split={left:'',right:''};
    try{if(collective&&typeof mxOrderPdfSplitCollectiveHeader==='function')split=await mxOrderPdfSplitCollectiveHeader(collective)||split}catch(_e){}
    if(!left)left=split.left||collective||'';
    if(!right)right=split.right||'';
    const out={left,right,collective,footer,collectiveLeft:split.left||left,collectiveRight:split.right||right};
    window.__mxQxPdfLastLogoStatus={at:new Date().toISOString(),branch:branch(),left:!!out.left,right:!!out.right,footer:!!out.footer,collective:!!out.collective};
    return out;
  }
  window.mxQxPdfConfiguredLogos=resolveLogos;
  try{window.mxOrderPdfLogos=resolveLogos}catch(_e){}
})();
