'use strict';
document.addEventListener('DOMContentLoaded',()=>{
  const t=(key,vars)=>window.LexiI18n.t(key,vars),cards=[...document.querySelectorAll('#public-library .lesson-card')],search=document.querySelector('#public-search');
  let level=window.LexiLibrary?.savedLevel('general')||'',track='general',limit=6;
  const normalize=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d').toLocaleLowerCase();
  function filter(){
    if(!search)return;
    const query=normalize(search.value.trim()),matched=cards.filter(c=>(!level||c.dataset.level===level)&&c.dataset.track===track&&normalize(c.dataset.search).includes(query));
    cards.forEach(c=>{c.hidden=!matched.includes(c)||matched.indexOf(c)>=limit;});
    document.querySelectorAll('[data-level-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.levelFilter===level)));
    document.querySelectorAll('[data-track-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.trackFilter===track)));
    document.querySelector('#library-count').textContent=t('library.count',{count:matched.length});
    document.querySelector('#library-empty').hidden=matched.length>0;document.querySelector('#show-more-lessons').hidden=matched.length<=limit;
  }
  document.querySelectorAll('[data-level-filter]').forEach(b=>b.addEventListener('click',()=>{level=window.LexiLibrary.saveLevel(b.dataset.levelFilter,track);limit=6;filter();}));
  document.querySelectorAll('[data-track-filter]').forEach(b=>b.addEventListener('click',()=>{track=b.dataset.trackFilter;level=window.LexiLibrary.savedLevel(track);limit=6;filter();}));
  search?.addEventListener('input',()=>{limit=6;filter();});document.querySelector('#show-more-lessons')?.addEventListener('click',()=>{limit+=6;filter();});
  document.querySelector('[data-show-ielts]')?.addEventListener('click',()=>{track='ielts';level=window.LexiLibrary.saveLevel('',track);search.value='';limit=6;filter();document.querySelector('#lessons').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth'});});
  document.addEventListener('lexiread:language',filter);filter();
  document.querySelector('#demo-word')?.addEventListener('click',e=>{const button=e.currentTarget,saved=button.getAttribute('aria-pressed')!=='true';button.setAttribute('aria-pressed',String(saved));button.dataset.i18n=saved?'demo.saved':'demo.save';document.querySelector('#demo-status').dataset.i18n=saved?'demo.done':'demo.caption';window.LexiI18n.apply();});
  document.querySelector('.password-toggle')?.addEventListener('click',e=>{const input=document.querySelector('#login-password'),button=e.currentTarget,show=input.type==='password';input.type=show?'text':'password';button.setAttribute('aria-pressed',String(show));button.dataset.i18n=show?'auth.hide':'auth.show';window.LexiI18n.apply();});
});
