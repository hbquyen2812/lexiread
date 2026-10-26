'use strict';
/* Shared presentation, local artwork and a non-sensitive level preference. */
(()=>{
  const levels=[['pre-A1','Mới bắt đầu'],['A1','Khởi đầu'],['A2','Nền tảng'],['B1','Trung cấp'],['B2','Khá'],['C1','Nâng cao'],['C2','Thành thạo']];
  const artwork=Object.fromEntries(['reading','nature','school','work','travel','city','food','technology'].map(key=>[key,'/static/illustrations/'+key+'.svg']));
  const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let topics={};
  try{const parsed=JSON.parse(document.getElementById('topic-labels-data')?.textContent||'{}');if(parsed&&typeof parsed==='object'&&!Array.isArray(parsed))topics=parsed;}catch{}
  const topicLabel=value=>Object.hasOwn(topics,value)?topics[value]:String(value||'Reading').replaceAll('_',' ');
  function savedLevel(track='general'){
    try{const value=localStorage.getItem('lexiread.level.'+track)||'';return levels.some(([code])=>code===value)?value:'';}catch{return '';}
  }
  function saveLevel(value,track='general'){
    const level=levels.some(([code])=>code===value)?value:'';
    try{localStorage.setItem('lexiread.level.'+track,level);}catch{}
    return level;
  }
  function levelPicker(selected='',track='general'){
    return `<section class="level-picker"><div class="level-picker-heading"><div><h2 data-i18n="level.choose">Chọn trình độ đọc</h2><p data-i18n="level.note">Chọn mức bạn thấy vừa sức. Bạn có thể đổi bất cứ lúc nào.</p></div><button type="button" class="level-all" data-action="library-level" data-track="${track}" data-level="" aria-pressed="${selected===''}" data-i18n="level.label.all">Tất cả trình độ</button></div><div class="level-options" role="group" aria-label="Chọn trình độ đọc">${levels.map(([code,label])=>`<button type="button" class="level-option" data-action="library-level" data-track="${track}" data-level="${code}" aria-pressed="${selected===code}"><strong>${code}</strong><span data-i18n="level.label.${code}">${label}</span></button>`).join('')}</div></section>`;
  }
  function cover(row){
    const key=Object.hasOwn(artwork,row.cover_key)?row.cover_key:'reading';
    return `<div class="lesson-cover illustrated"><img src="${artwork[key]}" alt="" width="640" height="360" loading="lazy" decoding="async"><span class="cover-topic" lang="en" data-no-i18n>${escape(row.topic_label||topicLabel(row.topic))}</span></div>`;
  }
  window.LexiLibrary={levels,artwork,savedLevel,saveLevel,levelPicker,cover,topicLabel};
})();
