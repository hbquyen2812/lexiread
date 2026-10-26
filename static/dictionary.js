'use strict';
(() => {
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const normalize=value=>String(value||'').replaceAll('’',"'").trim().replace(/^[".,;:!?“”()[\]{}]+|[".,;:!?“”()[\]{}]+$/g,'').trim().replace(/\s+/g,' ').toLowerCase();
  const canLookup=value=>{const word=normalize(value);return word.length<=160&&word.split(' ').length<=12&&/^[\p{L}\p{N}][\p{L}\p{N} '\-().,]*$/u.test(word);};
  function safeURL(value,audio=false){
    if(audio&&/^\/api\/dictionary\/audio\/[a-f0-9]{64}\/$/.test(value))return value;
    try{const u=new URL(value),hosts=audio?['api.dictionaryapi.dev','upload.wikimedia.org']:['dictionary.cambridge.org','www.oxfordlearnersdictionaries.com','en.wiktionary.org','commons.wikimedia.org','creativecommons.org','dictionaryapi.dev','en-word.net'];
      const media=(u.hostname==='api.dictionaryapi.dev'&&u.pathname.startsWith('/media/pronunciations/en/')&&u.pathname.endsWith('.mp3'))||(u.hostname==='upload.wikimedia.org'&&u.pathname.startsWith('/wikipedia/commons/')&&/\.(ogg|mp3|wav)$/i.test(u.pathname));
      return u.protocol==='https:'&&!u.username&&!u.password&&(!u.port||u.port==='443')&&hosts.includes(u.hostname)&&(!audio||(media&&!u.search&&!u.hash))?u.href:'';
    }catch{return '';}
  }
  const link=(url,label)=>safeURL(url)?`<a href="${esc(safeURL(url))}" target="_blank" rel="noopener noreferrer">${esc(label)} ↗</a>`:'';
  const definitions=items=>`<ol class="dictionary-senses" lang="en" data-no-i18n>${items.map(d=>`<li><p>${esc(d.definition)}</p>${d.example?`<blockquote>${esc(d.example)}</blockquote>`:''}</li>`).join('')}</ol>`;
  let run=0,current=null;
  function render(data){
    const remote=data.dictionary||{},entries=remote.entries||[],local=data.local_entries||[];
    const pronunciations=entries.flatMap(e=>e.phonetics||[]).filter((p,i,all)=>all.findIndex(x=>x.ipa===p.ipa&&x.audio===p.audio)===i);
    const sounds=pronunciations.filter(p=>safeURL(p.audio,true)).sort((a,b)=>['UK','US','AU',''].indexOf(a.accent)-['UK','US','AU',''].indexOf(b.accent)).slice(0,2);
    const ipa=[...new Set(pronunciations.map(p=>p.ipa).filter(Boolean))];
    const phonetics=sounds.length?(ipa.length&&!sounds.some(p=>p.ipa)?`<p class="dictionary-ipa" lang="en" data-no-i18n>${ipa.map(esc).join(' · ')}</p>`:'')+sounds.map(p=>`<div class="dictionary-sound"><div><span class="chip">${esc(p.accent||'Audio')}</span> <span class="dictionary-ipa" lang="en" data-no-i18n>${esc(p.ipa)}</span></div><audio controls preload="none" src="${esc(safeURL(p.audio,true))}" aria-label="Nghe phát âm ${esc(p.accent||data.word)}"></audio></div>`).join(''):`${ipa.length?`<p class="dictionary-ipa" lang="en" data-no-i18n>${ipa.map(esc).join(' · ')}</p>`:''}<p class="fineprint">Chưa có bản thu phát âm cho từ này.</p>`;
    const messages={not_ready:'Kho từ điển chưa có dữ liệu. Bạn vẫn có thể tra bằng các liên kết bên dưới.',not_found:'Chưa tìm thấy mục từ phù hợp. Thử dạng nguyên mẫu hoặc mở từ điển bên dưới.',unavailable:'Nguồn từ điển đang không phản hồi. Bạn vẫn có thể xem nghĩa trong kho học hoặc mở nguồn bên dưới.',rate_limited:'Bạn vừa tra nhiều từ liên tiếp. Chờ một phút rồi thử lại nhé.',offline:'Bản HTML chỉ tra các từ đã có trong bài. Mở bản web để tra thêm nghĩa và nghe phát âm.'};
    return `<article class="dictionary-panel" lang="vi" data-no-i18n><header><span class="eyebrow">TRA TỪ NHANH</span><h3 lang="en">${esc(data.word)}</h3>${remote.base_words?.length?`<p class="fineprint">Dạng gốc: ${remote.base_words.map(esc).join(', ')}</p>`:''}${phonetics}</header>${pronunciations.length?'<details class="dictionary-ipa-help"><summary>Đọc phiên âm thế nào?</summary><p>Dấu <b>ˈ</b> đứng trước âm tiết được nhấn chính; <b>ˌ</b> chỉ trọng âm phụ. Nghe bản thu, rồi thử nói lại cả từ.</p>'+link('https://dictionary.cambridge.org/help/phonetics.html','Bảng âm IPA của Cambridge')+'</details>':''}${local.map((w,i)=>`<section class="dictionary-local"><span class="eyebrow">${esc(w.label)}</span><p><span class="chip" lang="en">${esc(w.pos)}</span> <strong>${esc(w.meaning_vi)}</strong></p>${w.example?`<blockquote lang="en">${esc(w.example)}</blockquote>`:''}${w.example_vi?`<p class="fineprint">${esc(w.example_vi)}</p>`:''}${w.usage_pattern?`<p class="word-pattern" lang="en">${esc(w.usage_pattern)}</p>`:''}<button class="link-btn" type="button" data-dictionary-save="${i}">+ Lưu nghĩa này</button></section>`).join('')}${entries.length?'<h4 class="dictionary-section-title">Giải nghĩa Anh–Anh</h4><p class="fineprint">Đối chiếu các nghĩa với câu bạn đang đọc.</p>':`<p class="dictionary-message" role="status">${esc(messages[remote.status]||messages.unavailable)}</p>`}${entries.map(entry=>`<section class="dictionary-entry">${entry.meanings.map(m=>`<div class="dictionary-meaning"><h4 lang="en">${esc(m.pos)}</h4>${definitions(m.definitions.slice(0,3))}${m.definitions.length>3?`<details><summary>Xem ${m.definitions.length-3} nghĩa khác</summary>${definitions(m.definitions.slice(3))}</details>`:''}</div>`).join('')}<p class="dictionary-credit">${entry.sources.map(url=>link(url,entry.source_label||'Wiktionary')).join(' · ')} · ${link(entry.license.url,entry.license.name)}</p></section>`).join('')}<div class="dictionary-links"><span>Đối chiếu thêm</span>${(data.links||[]).map(l=>link(l.url,l.title)).join('')}</div>${entries.length?`<details class="dictionary-attribution"><summary>Nguồn dữ liệu và bản thu</summary><p>${remote.storage==='database'?'Mục từ và bản thu có sẵn trong kho LexiRead. Open English WordNet được phát triển từ Princeton WordNet.':'Mục từ từ Free Dictionary API / Wiktionary.'} Bố cục được rút gọn; liên kết nguồn có mục từ đầy đủ.</p>${sounds.map(p=>`<p>${esc(p.accent||data.word)}: ${link(p.source,'Bản thu gốc')} · ${p.license?link(p.license.url,p.license.name):''}</p>`).join('')}</details>`:''}</article>`;
  }
  function stopAudio(){document.querySelectorAll('#modal audio').forEach(a=>a.pause());}
  async function open(selection){
    const word=normalize(selection.word);if(!canLookup(word)){toast('Chọn một từ hoặc cụm từ tiếng Anh ngắn để tra.',true);return;}
    stopAudio();const id=++run;current={selection:{...selection,word},data:null,pending:true};
    openModal('Nghĩa & phát âm',`<div id="dictionary-result"><p role="status">Đang tra <strong lang="en">${esc(word)}</strong>…</p></div>`, '<button class="btn" data-action="close-modal">Đóng</button><button class="btn secondary" data-dictionary-save="new" disabled>+ Lưu từ</button>');
    const root=document.getElementById('dictionary-result');
    const saveButton=document.querySelector('#modal [data-dictionary-save="new"]');
    try{
      let data;
      if(window.LEXIREAD_PREVIEW){const found=(state.reading?.analysis?.vocabulary||[]).filter(w=>normalize(w.word)===word).map(w=>({...w,label:'Trong bài đang đọc'}));data={word,local_entries:found,dictionary:{status:'offline',entries:[]},links:[{title:'Cambridge Dictionary',url:'https://dictionary.cambridge.org/search/english/direct/?q='+encodeURIComponent(word)}]};}
      else data=await api('/dictionary/?word='+encodeURIComponent(word)+(selection.reading_id?'&reading_id='+encodeURIComponent(selection.reading_id):''));
      if(id!==run||!root.isConnected||!document.getElementById('modal').open)return;
      current.data=data;current.pending=false;root.innerHTML=render(data);saveButton.disabled=false;
      root.querySelectorAll('audio').forEach(a=>{a.addEventListener('play',()=>root.querySelectorAll('audio').forEach(other=>{if(other!==a)other.pause();}));a.addEventListener('error',()=>{const note=document.createElement('p');note.className='fineprint';note.textContent='Chưa phát được bản thu. Bạn có thể mở bản thu gốc trong phần nguồn dữ liệu.';a.replaceWith(note);});});
    }catch(error){if(id===run&&root.isConnected&&document.getElementById('modal').open){root.textContent=error.message;current.pending=false;saveButton.disabled=false;saveButton.textContent='+ Nhập nghĩa thủ công';}}
  }
  document.addEventListener('click',e=>{
    const lookup=e.target.closest('[data-dictionary-word]');if(lookup){open({word:lookup.dataset.dictionaryWord});return;}
    const save=e.target.closest('[data-dictionary-save]');if(!save||!current||current.pending||!document.getElementById('modal').open)return;
    const entry=current.data?.local_entries?.[save.dataset.dictionarySave==='new'?0:Number(save.dataset.dictionarySave)]||{};
    const pronunciation=current.data?.dictionary?.entries?.flatMap(x=>x.phonetics||[]).find(p=>p.ipa);
    const note=[entry.note,pronunciation?'IPA: '+pronunciation.ipa:''].filter(Boolean).join('\n');
    stopAudio();editor({...blankEntry(),...entry,...current.selection,note,verified:false});
  });
  document.addEventListener('close',e=>{if(e.target.id==='modal')stopAudio();},true);
  window.LexiDictionary={open,render,canLookup,safeURL,stopAudio};
})();
