/* Exact-word IPA from the installed dictionary. One batch per rendered view, no AI/network dictionary. */
(() => {
  'use strict';
  const cache=new Map(),pending=new Set();
  const normalize=value=>String(value).normalize('NFKC').replace(/’/g,"'").replace(/\s+/g,' ').trim().toLowerCase();
  const labels={vi:'Tra phiên âm',en:'Look up IPA',fr:'Consulter l’API',zh:'查看音标'};
  let timer;
  function display(host,word){
    const values=cache.get(word);
    if(!values)return;
    let note=host.querySelector('.word-ipa');
    if(!note){note=document.createElement('span');note.className='word-ipa';note.dataset.noI18n='';host.append(note);}
    if(values.length){
      const text=values.join(' · ');
      if(note.textContent!==text)note.textContent=text;
      note.lang='en';note.title='IPA · Open English WordNet 2025';
    }else if(!note.firstChild){
      const link=document.createElement('button');link.type='button';link.className='ipa-lookup';link.dataset.dictionaryWord=word;
      link.textContent=labels[window.LexiI18n?.language]||labels.vi;note.append(link);
    }
  }
  async function scan(){
    const hosts=[...document.querySelectorAll('[data-pronounce-kind="word"]')]
      .filter(button=>!button.closest('.dictionary-panel'));
    const words=[];
    for(const button of hosts){
      const word=normalize(button.dataset.pronounce);
      if(!word||word.length>160)continue;
      if(cache.has(word))display(button.parentElement,word);
      else if(!pending.has(word)){pending.add(word);words.push(word);}
    }
    for(let offset=0;offset<words.length;offset+=100){
      const batch=words.slice(offset,offset+100);
      try{
        const result=await api('/dictionary/pronunciations/',{method:'POST',data:{words:batch}});
        for(const word of batch){
          const values=Object.hasOwn(result.items||{},word)?result.items[word]:[];
          cache.set(word,Array.isArray(values)?values.filter(v=>typeof v==='string'&&v.length<=160).slice(0,4):[]);
        }
      }catch{
        // Keep a manual lookup when unavailable; don't repeatedly retry on DOM mutations.
        for(const word of batch)cache.set(word,[]);
      }finally{batch.forEach(word=>pending.delete(word));}
    }
    document.querySelectorAll('[data-pronounce-kind="word"]').forEach(button=>{if(!button.closest('.dictionary-panel'))display(button.parentElement,normalize(button.dataset.pronounce));});
    // Bound this page's in-memory cache without persisting a learner's vocabulary.
    if(cache.size>2000){for(const key of [...cache.keys()].slice(0,cache.size-1500))cache.delete(key);}
  }
  const schedule=()=>{clearTimeout(timer);timer=setTimeout(scan,50);};
  new MutationObserver(records=>{
    if(records.some(r=>[...r.addedNodes].some(n=>n.nodeType===1&&!n.closest?.('.word-ipa'))))schedule();
  }).observe(document.body,{childList:true,subtree:true});
  document.addEventListener('lexiread:language',()=>{
    document.querySelectorAll('.ipa-lookup').forEach(n=>{n.textContent=labels[window.LexiI18n?.language]||labels.vi;});
  });
  schedule();
})();
