/* Collocation lessons and direct WordNet relations. No model calls. */
(() => {
  'use strict';
  const e=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const relations={'verb-noun':'Verb + noun','adjective-noun':'Adjective + noun','adverb-adjective':'Adverb + adjective',
    'verb-preposition':'Verb + preposition','adjective-preposition':'Adjective + preposition','noun-preposition':'Noun + preposition','verb-adverb':'Verb + adverb','noun-noun':'Noun + noun'};
  const sourceRelations={...relations,'object_of':'Verb + noun','subject_of':'Noun + verb','modifier':'Modifier + noun',
    'ADV ADJ*':'Adverb + adjective','ADV V*':'Adverb + verb','V* ADV':'Verb + adverb','preposition':'Preposition',
    'verb-adverb':'Verb / adverb','derivation':'Derivation','pertainym':'Related form'};
  const prefs={kind:'collocations',relation:'',level:'',q:'',page:1};
  const html=(target,markup)=>target.replaceChildren(window.LexiDOM.fragment(markup));
  const voice=(text,kind='word')=>window.LexiPronunciation?.button(text,kind)||'';
  const patternArt=key=>window.LexiVisuals?.pattern(key)||'';
  const scene=kind=>window.LexiVisuals?.scene(kind)||'';
  const fold=s=>String(s).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replaceAll('đ','d');
  const combination=r=>r.detail?.pattern||(['object_of','modifier','ADV ADJ*','ADV V*'].includes(r.relation)?r.related+' '+r.headword:r.headword+' '+r.related);

  function filter(items){
    return items.filter(r=>r.kind===prefs.kind&&(!prefs.relation||r.relation===prefs.relation)&&
      (!prefs.level||r.level===prefs.level)&&(!prefs.q||fold(r.title+' '+r.terms).includes(fold(prefs.q))));
  }

  async function page(area,active){
    const data=await api('/lexical/lessons/');if(!active())return;
    html(area,`<header class="academy-heading illustrated-heading pattern-heading">${scene('words')}<span class="eyebrow">WORDS TOGETHER</span><h1>Collocations & Word families</h1><p>Học từ đi cùng nhau. Chọn đúng dạng từ trong câu.</p><div class="pattern-demo" lang="en" data-no-i18n><span>make <b>progress</b></span><span>create <b>→ creative</b></span></div></header>
      <div class="pattern-switch" role="group" aria-label="Kiểu bài học"><button type="button" data-kind="collocations">Collocations</button><button type="button" data-kind="families">Word families</button></div>
      <form class="pattern-filters" role="search"><label><span>Tìm từ hoặc cụm</span><input type="search" data-pattern-query maxlength="80" placeholder="make, decision, creative…"></label><label><span>Trình độ</span><select data-pattern-level><option value="">Tất cả trình độ</option>${['A2','B1','B2'].map(l=>`<option>${l}</option>`).join('')}</select></label><label data-relation-label><span>Cách kết hợp</span><select data-pattern-relation><option value="">Tất cả</option>${Object.entries(relations).map(([k,v])=>`<option value="${k}">${v}</option>`).join('')}</select></label></form>
      <p class="pattern-count" role="status" data-pattern-count></p><div class="pattern-lessons" data-pattern-cards></div>
      <div class="pattern-pagination"><button type="button" class="btn secondary" data-prev>← Trang trước</button><span data-page></span><button type="button" class="btn secondary" data-next>Trang tiếp →</button></div>
      <details class="pattern-reference"><summary>Tra thêm collocations & dạng từ</summary><p>Tra bằng từ gốc, như <span lang="en" data-no-i18n>access, debate, create</span>.</p><form data-reference-form class="pattern-reference-form"><label><span>Từ cần tra</span><input name="q" type="search" minlength="2" maxlength="80" required placeholder="access"></label><label><span>Nội dung</span><select name="kind"><option value="collocation">Collocations</option><option value="family">Word families</option><option value="corpus">Cụm trong câu</option></select></label><button class="btn primary">Tra từ</button></form><div data-reference-results aria-live="polite"></div><details class="pattern-sources"><summary>Nguồn dữ liệu</summary><p>ColloCaid Sample Data · Frankenberg-Garcia, Rees, Lew, Roberts & Butcher. Chỉ gồm phần mẫu được công bố.</p><a href="https://doi.org/10.6084/m9.figshare.13028207.v2" target="_blank" rel="noopener noreferrer">ColloCaid ↗</a><p>Open English WordNet 2025 · Open English WordNet Team, phát triển từ Princeton WordNet. Các dạng từ liên quan được nối theo từng nghĩa, không phải từ đồng nghĩa hay một họ từ đầy đủ.</p><a href="https://en-word.net/" target="_blank" rel="noopener noreferrer">Open English WordNet ↗</a> · <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener noreferrer">CC BY 4.0 ↗</a><p>UD English EWT 2.18 · Natalia Silveira, Sebastian Schuster, Nathan Schneider và các cộng tác viên. Các cặp từ được lọc tự động từ câu có sẵn.</p><a href="https://universaldependencies.org/treebanks/en_ewt/index.html" target="_blank" rel="noopener noreferrer">Nguồn EWT ↗</a> · <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener noreferrer">CC BY-SA 4.0 ↗</a></details></details>`);
    const draw=()=>{
      const rows=filter(data.items),pages=Math.max(1,Math.ceil(rows.length/8));prefs.page=Math.min(prefs.page,pages);
      area.querySelectorAll('[data-kind]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.kind===prefs.kind)));
      area.querySelector('[data-relation-label]').hidden=prefs.kind==='families';
      area.querySelector('[data-pattern-count]').textContent=rows.length+' bài học';
      area.querySelector('[data-page]').textContent=`${prefs.page} / ${pages}`;
      area.querySelector('[data-prev]').disabled=prefs.page===1;area.querySelector('[data-next]').disabled=prefs.page===pages;
      html(area.querySelector('[data-pattern-cards]'),rows.length?rows.slice((prefs.page-1)*8,prefs.page*8).map(r=>`<a class="pattern-lesson" href="#collection/${encodeURIComponent(r.id)}">${patternArt(r.relation)}<div class="pattern-lesson-top"><span class="level-pill">${e(r.level)}</span></div><h2 lang="en" data-no-i18n>${e(r.title)}</h2><p class="pattern-preview" lang="en" data-no-i18n>${r.preview.map(e).join(' · ')}</p><div class="pattern-lesson-bottom"><span>${Number(r.count)} <span>mục</span></span><span>${r.progress?`✓ ${e(r.progress.score)}/${e(r.progress.total)}`:'Bắt đầu →'}</span></div></a>`).join(''):'<div class="empty-state">Chưa tìm thấy bài phù hợp. Thử từ khóa hoặc trình độ khác.</div>');
    };
    area.querySelector('[data-pattern-query]').value=prefs.q;area.querySelector('[data-pattern-level]').value=prefs.level;area.querySelector('[data-pattern-relation]').value=prefs.relation;
    area.querySelector('.pattern-filters').onsubmit=ev=>ev.preventDefault();
    for(const [selector,key,event] of [['[data-pattern-query]','q','input'],['[data-pattern-level]','level','change'],['[data-pattern-relation]','relation','change']])area.querySelector(selector).addEventListener(event,ev=>{prefs[key]=ev.target.value;prefs.page=1;draw();});
    area.querySelectorAll('[data-kind]').forEach(b=>b.onclick=()=>{prefs.kind=b.dataset.kind;prefs.relation='';area.querySelector('[data-pattern-relation]').value='';prefs.page=1;draw();});
    area.querySelector('[data-prev]').onclick=()=>{prefs.page--;draw();};area.querySelector('[data-next]').onclick=()=>{prefs.page++;draw();};draw();
    const form=area.querySelector('[data-reference-form]'),target=area.querySelector('[data-reference-results]');
    let ticket=0;
    const search=async(query,kind,page=1)=>{
      const request=++ticket;target.textContent='Đang tìm từ…';
      try{
        const result=await api('/lexical/reference/?'+new URLSearchParams({q:query,kind,page}));if(!active()||request!==ticket)return;
        html(target,referenceHTML(result,kind)+`<div class="pattern-pagination"><button type="button" class="btn secondary" data-ref-prev ${page===1?'disabled':''}>← Trang trước</button><span>${page}</span><button type="button" class="btn secondary" data-ref-next ${result.has_next?'':'disabled'}>Trang tiếp →</button></div>`);
        target.querySelector('[data-ref-prev]').onclick=()=>search(query,kind,page-1);target.querySelector('[data-ref-next]').onclick=()=>search(query,kind,page+1);
      }catch(error){if(active()&&request===ticket)target.textContent=error.message;}
    };
    form.onsubmit=ev=>{ev.preventDefault();const fields=new FormData(form);search(String(fields.get('q')).trim(),fields.get('kind'));};
  }

  function referenceHTML(result,kind){
    if(!result.items.length)return '<p class="notice">Chưa có kết quả cho từ này trong nguồn đã nhập. Thử từ gốc hoặc mở Từ điển.</p><a class="link-btn" href="#learn/dictionary">Mở từ điển →</a>';
    const note=kind==='family'?'Dạng từ liên quan · Xem nghĩa để chọn cách dùng phù hợp.':kind==='corpus'?'Cụm trong câu · EWT':'Collocations học thuật · ColloCaid';
    return `<p class="pattern-reference-label">${note}</p>${kind==='corpus'?'<p class="pattern-corpus-note">Cặp từ được lọc từ câu thực tế. Xem cả câu để hiểu cách dùng; không phải cụm nào cũng là collocation cố định.</p>':''}<div class="pattern-reference-list">${result.items.map(r=>{
      const d=r.detail||{};
      if(kind==='family'){
        const reverse=r.related===result.query,word=reverse?r.headword:r.related,pos=reverse?d.head_pos:d.related_pos;
        const meanings=(d.senses||[]).map(s=>reverse?s.head_gloss:s.related_gloss);
        return `<article class="pattern-reference-item"><div class="pattern-form-heading"><strong lang="en" data-no-i18n>${e(word)}</strong><span class="chip" lang="en" data-no-i18n>${e(pos)}</span>${voice(word)}</div><p lang="en" data-no-i18n>${e([...new Set(meanings)].join('; '))}</p><button class="link-btn" type="button" data-dictionary-word="${e(word)}">Tra nghĩa & phát âm →</button></article>`;
      }
      const phrase=combination(r);
      return `<article class="pattern-reference-item"><span class="chip" lang="en" data-no-i18n>${e(sourceRelations[r.relation]||r.relation)}</span>${kind==='corpus'?'<span class="pattern-source-tag">EWT · CC BY-SA 4.0</span>':''}<h3 lang="en" data-no-i18n>${e(phrase)}</h3>${voice(phrase,'sentence')}${d.sense?`<p lang="en" data-no-i18n>${e(d.sense)}</p>`:''}${d.following?`<p lang="en" data-no-i18n>${e(d.following)}</p>`:''}${d.examples?.length?`<details><summary>Ví dụ</summary>${d.examples.map(s=>`<p lang="en" data-no-i18n>${e(s)}</p>`).join('')}</details>`:''}</article>`;
    }).join('')}</div>`;
  }

  const wordObject=text=>[
    ['coffee',/coffee|tea|drink/],['calendar',/schedule|appointment|plan|deadline/],['clock',/time|wait|prompt/],
    ['book',/book|read|learn|language|educat/],['travel',/travel|bus|train|trip|station/],
    ['plant',/climate|environment|resource|energy|growth/],['people',/team|friend|respect|people|customer/],
    ['laptop',/data|technology|information|research/],['house',/home|house/],['letter',/communicat|explain|reply|respond/],
    ['apple',/diet|food|healthy/],['receipt',/credit|pay|cost|market|econom/]
  ].find(([,test])=>test.test(String(text).toLowerCase()))?.[0];
  function wordArt(w){
    const key=wordObject(w.word);
    if(key)return window.LexiVisuals?.object(key,'small')||'';
    // Abstract forms use a word-part diagram; do not invent a literal illustration.
    return `<span class="pattern-word-mark" lang="en" data-no-i18n aria-hidden="true">${e(w.family?w.part_of_speech:String(w.word).split(' ')[0])}<span>${w.family?'↗':'＋'}</span></span>`;
  }
  function wordsHTML(data){
    const groups=new Map();data.words.forEach(w=>{const key=w.family||'';if(!groups.has(key))groups.set(key,[]);groups.get(key).push(w);});
    return [...groups].map(([family,words])=>`<section class="pattern-word-group">${family?`<h2 class="pattern-family-title" lang="en" data-no-i18n>${e(family)}</h2><div class="pattern-family-map" lang="en" data-no-i18n>${words.map(w=>`<div><span>${e(w.part_of_speech)}</span><strong>${e(w.word)}</strong></div>`).join('')}</div>`:''}<div class="pattern-word-grid ${family?'is-family':''}">${words.map(w=>`<article class="pattern-word"><div class="pattern-word-visual">${wordArt(w)}</div><div class="pattern-form-heading"><h3 lang="en" data-no-i18n>${e(w.word)}</h3>${voice(w.word)}</div>${family?`<span class="chip" lang="en" data-no-i18n>${e(w.part_of_speech)}</span>`:''}<p class="pattern-meaning">${e(w.meaning_vi)}</p><p class="pattern-example" lang="en" data-no-i18n>${e(w.example)}</p><details><summary>Nghĩa câu & cách dùng</summary><p>${e(w.example_translation)}</p><p ${family?'':'lang="en" data-no-i18n'}>${e(w.usage_pattern)}</p></details></article>`).join('')}</div></section>`).join('');
  }

  function lesson(area,data,active){
    const breadcrumb=document.getElementById('page-label');if(breadcrumb)breadcrumb.textContent='Collocations & Word families';
    html(area,`<a class="link-btn" href="#learn/patterns">← Collocations & Word families</a><header class="academy-heading illustrated-heading pattern-detail-heading"><div class="learning-scene">${patternArt(data.relation)}</div><span class="level-pill">${e(data.level)}</span><h1 lang="en" data-no-i18n>${e(data.title)}</h1><p>${e(data.tip)}</p></header><div class="pattern-study-actions"><div class="pattern-switch" role="group" aria-label="Chế độ học"><button type="button" data-view="learn" aria-pressed="true">Học qua ví dụ</button><button type="button" data-view="quiz" aria-pressed="false">Bài tập</button></div><button type="button" class="btn primary" data-save-pattern>Lưu bộ & ôn thẻ →</button></div><p role="status" data-pattern-status></p><div data-learning>${wordsHTML(data)}</div><section data-pattern-quiz hidden></section><details class="pattern-sources"><summary>Nguồn bài học</summary><p>Ví dụ, bản dịch và bài tập do Lexivela biên soạn.</p><a href="https://dictionary.cambridge.org/grammar/british-grammar/collocation" target="_blank" rel="noopener noreferrer">Cambridge · Collocation ↗</a> · <a href="https://dictionary.cambridge.org/grammar/british-grammar/word-formation" target="_blank" rel="noopener noreferrer">Word formation ↗</a></details>`);
    const quiz=area.querySelector('[data-pattern-quiz]');let token=uid();
    const bind=()=>{
      html(quiz,window.LexiAcademy.quizHTML(data.questions));
      quiz.querySelectorAll('.academy-question-heading').forEach((host,i)=>{if(data.questions[i].hint_vi){const hint=document.createElement('small');hint.className='pattern-hint';hint.textContent=data.questions[i].hint_vi;host.append(hint);const accessible=document.createElement('span');accessible.textContent=' ('+data.questions[i].hint_vi+')';host.closest('fieldset').querySelector('legend').append(accessible);}});
      quiz.querySelector('form').onsubmit=async ev=>{
        ev.preventDefault();const form=ev.currentTarget,b=form.querySelector('button[type="submit"]');if(!form.reportValidity())return;b.disabled=true;
        const fields=new FormData(form),answers=Object.fromEntries(data.questions.map(q=>[q.id,Number(fields.get(q.id))]));
        try{
          const result=await api(`/learn/vocabulary/${encodeURIComponent(data.id)}/submit/`,{method:'POST',data:{answers,token,version:data.version}});if(!active())return;
          html(quiz,window.LexiAcademy.resultHTML(result));quiz.querySelector('[tabindex]').focus();
          quiz.querySelector('[data-wrong-only]').onchange=ev=>{quiz.querySelectorAll('.is-correct').forEach(x=>x.hidden=ev.target.checked);quiz.querySelector('.academy-all-correct').hidden=!(ev.target.checked&&result.score===result.total);};
          quiz.querySelector('[data-academy="retry"]').onclick=()=>{token=uid();bind();quiz.querySelector('input')?.focus();};await refreshBoot();
        }catch(error){if(active())form.querySelector('[role="status"]').textContent=error.message;}finally{b.disabled=false;}
      };
    };bind();
    area.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{const practice=b.dataset.view==='quiz';area.querySelector('[data-learning]').hidden=practice;quiz.hidden=!practice;area.querySelectorAll('[data-view]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));});
    area.querySelector('[data-save-pattern]').onclick=async ev=>{
      const button=ev.currentTarget,status=area.querySelector('[data-pattern-status]');button.disabled=true;status.textContent='Đang lưu bộ từ…';
      try{
        await api(`/learn/vocabulary/${encodeURIComponent(data.id)}/save/`,{method:'POST',data:{indices:data.words.map((_,i)=>i)}});
        if(!active())return;await refreshBoot();if(!active())return;
        state.study=null;location.hash='pattern-cards/'+data.id;
      }catch(error){if(active())status.textContent=error.message;}finally{button.disabled=false;}
    };
  }
  const activeCards=()=>location.hash.startsWith('#pattern-cards/')&&!!state.study?.patternId;
  async function cards(area,id,epoch,restart=false){
    const data=await api('/lexical/lessons/'+encodeURIComponent(id)+'/cards/');if(epoch!==state.routeEpoch)return;
    if(data.items.length&&(restart||state.study?.patternId!==id)){
      state.studySettings={mode:'flashcard',tag:data.title,reading:'',scope:'all',limit:data.items.length};
      state.study={mode:'flashcard',cards:data.items,idx:0,done:0,correct:0,flipped:false,seen:[],finished:false,busy:false,
        token:uid(),question:null,result:null,initialCount:data.items.length,retryCount:0,retried:new Set(),lastReview:null,patternId:id};
    }else if(!data.items.length)state.study=null;
    html(area,`<a class="link-btn" href="#collection/${encodeURIComponent(id)}">← Về bài học</a><header class="academy-heading illustrated-heading">${scene('recall')}<span class="eyebrow">Flashcard</span><h1 lang="en" data-no-i18n>${e(data.title)}</h1></header>${data.items.length?'<div class="study-stage" id="study-stage"></div>':'<p class="notice">Mở bài học rồi chọn “Lưu bộ & ôn thẻ” để bắt đầu.</p>'}`);
    if(data.items.length)renderStage();
  }
  async function restart(button){
    const id=state.study?.patternId,epoch=state.routeEpoch;if(!id)return;
    await busy(button,()=>cards(document.querySelector('#main'),id,epoch,true));
  }
  window.LexiPatterns={page,lesson,cards,restart,activeCards,referenceHTML,wordsHTML};
})();
