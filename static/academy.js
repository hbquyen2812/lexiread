'use strict';
/* Learning content and deterministic recommendations. No model or third-party calls. */
(()=>{
  const levels=['A1','A2','B1','B2','C1','C2'];
  const names={plan:'Lộ trình',grammar:'Học ngữ pháp',vocabulary:'Từ vựng theo chủ đề',dictionary:'Từ điển',sources:'Tài liệu tham khảo'};
  let generation=0;
  const e=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const safe=value=>{try{const u=new URL(value);return u.protocol==='https:'&&!u.username&&!u.password?u.href:'';}catch{return '';}};
  const link=(url,title)=>safe(url)?`<a class="link-btn" href="${e(safe(url))}" target="_blank" rel="noopener noreferrer">${e(title)} ↗</a>`:'';
  const tabs=active=>`<nav class="academy-tabs" aria-label="Các mục học tập">${Object.entries(names).map(([key,title])=>`<a href="#learn/${key}" ${key===active?'aria-current="page"':''}>${title}</a>`).join('')}</nav>`;
  const options=value=>`<option value="">Tất cả trình độ</option>${levels.map(l=>`<option value="${l}" ${l===value?'selected':''}>${l}</option>`).join('')}`;
  const shell=active=>tabs(active)+`<section class="academy" data-academy-root><div class="empty-state" role="status">Đang tải bài học…</div></section>`;
  function quizHTML(questions){
    return `<form class="academy-quiz"><div class="section-title"><div><h2>Luyện tập</h2><p>${questions.length} câu · Có lời giải sau khi nộp bài</p></div></div>${questions.map((q,i)=>`<fieldset class="reading-question academy-question"><legend class="sr-only"><span>Câu ${i+1}: </span><span ${q.prompt_lang==='vi'?'':'lang="en" data-no-i18n'}>${e(q.prompt)}</span></legend><div class="academy-question-heading" aria-hidden="true"><span class="chip">Câu ${i+1}</span><p ${q.prompt_lang==='vi'?'':'lang="en" data-no-i18n'}>${e(q.prompt)}</p></div><div class="reading-options">${q.options.map((answer,j)=>`<label class="reading-option"><input type="radio" name="${e(q.id)}" value="${j}" required><span class="choice-letter">${'ABCD'[j]}</span><span data-no-i18n>${e(answer)}</span></label>`).join('')}</div></fieldset>`).join('')}<button type="submit" class="btn primary">Kiểm tra bài làm</button><p class="academy-feedback" role="status"></p></form>`;
  }
  function resultHTML(result){
    return `<section class="academy-result" tabindex="-1"><div class="reading-score"><strong>${result.score}/${result.total}</strong><div>${result.percent>=80?'Bạn đã làm tốt bài này.':'Xem lời giải để hiểu rõ những câu chưa đúng.'}<p>Kết quả đã được lưu để gợi ý bài học tiếp theo.</p></div></div><label class="academy-wrong-toggle"><input type="checkbox" data-wrong-only> Chỉ xem câu chưa đúng</label><div class="academy-answers">${result.results.map((q,i)=>`<article class="academy-answer ${q.correct?'is-correct':'is-wrong'}"><div class="tags"><span class="chip">Câu ${i+1}</span><b>${q.correct?'✓ Đúng':'Cần xem lại'}</b></div><p ${q.prompt_lang==='vi'?'':'lang="en" data-no-i18n'}>${e(q.prompt)}</p><p>Đáp án: <strong data-no-i18n>${e(q.options[q.answer])}</strong>${q.correct?'':`<br>Bạn chọn: <span data-no-i18n>${e(q.options[q.submitted])}</span>`}</p><p>${e(q.explanation_vi)}</p></article>`).join('')}</div><p class="academy-all-correct" hidden>Bạn đã trả lời đúng tất cả các câu.</p><div class="button-row"><button class="btn secondary" data-academy="retry">Làm lại bài</button><a class="btn primary" href="#learn/plan">Về lộ trình học →</a></div></section>`;
  }
  async function page(root,section='plan',epoch){
    const ticket=++generation,active=()=>ticket===generation&&epoch===state.routeEpoch;
    if(!Object.hasOwn(names,section)&&!['verbs','tenses'].includes(section))section='plan';
    root.innerHTML=shell(['verbs','tenses'].includes(section)?'grammar':section); const area=root.querySelector('[data-academy-root]');
    if(window.LEXIREAD_PREVIEW){area.innerHTML='<div class="notice"><h1>Góc học nền tảng</h1><p>Ngữ pháp, bộ từ và lộ trình cá nhân có trên bản web có tài khoản. Bản HTML ngoại tuyến vẫn hỗ trợ thư viện và ôn từ đã lưu.</p><a class="btn primary" href="http://127.0.0.1:8766/#learn/plan">Mở bản web đang chạy →</a></div>';return;}
    if(section==='vocabulary'){await window.LexiTopics.topics(area,active);return;}
    if(section==='grammar'){await window.LexiGrammar.catalogue(area,active);return;}
    if(['verbs','tenses'].includes(section)){await window.LexiGrammarReference.page(area,section,active);return;}
    if(section==='dictionary'){await window.LexiTopics.dictionary(area,active);return;}
    if(section==='plan'){
      let data=await api('/learn/plan/');if(!active())return;
      const render=()=>{
        const p=data.profile,g=data.guidance;
        area.innerHTML=`<header class="academy-heading"><span class="eyebrow">MỖI NGÀY MỘT BƯỚC</span><h1>Hôm nay bạn muốn học gì?</h1><p>Chọn trình độ, mục tiêu và thời gian học. LexiRead sẽ gợi ý bài phù hợp với bạn.</p></header><form class="academy-profile"><label>Trình độ hiện tại<select name="level">${levels.map(l=>`<option ${l===p.level?'selected':''}>${l}</option>`).join('')}</select></label><label>Mục tiêu học<select name="goal">${[['general','Tiếng Anh hằng ngày'],['ielts','IELTS'],['toeic','TOEIC']].map(([v,t])=>`<option value="${v}" ${p.goal===v?'selected':''}>${t}</option>`).join('')}</select></label><label>Thời gian học mỗi ngày<select name="daily_minutes">${[15,30,45,60].map(n=>`<option value="${n}" ${p.daily_minutes===n?'selected':''}>${n} phút</option>`).join('')}</select></label><button class="btn primary">${p.configured?'Cập nhật lộ trình':'Bắt đầu lộ trình'}</button><p class="academy-feedback" role="status"></p></form><div class="section-title"><h2>Bài học hôm nay</h2><span class="chip">${data.planned_minutes} phút</span></div><ol class="path-tasks">${data.tasks.map((t,i)=>`<li><span class="path-number">${i+1}</span><div><span class="eyebrow">${t.minutes} PHÚT</span><h3>${e(t.title)}</h3><p>${e(t.reason)}</p></div><a class="btn secondary" href="${e(t.href)}">Bắt đầu →</a></li>`).join('')}</ol>${data.next_level?`<div class="notice">Bạn đã làm tốt các bài ${e(p.level)}. Nếu muốn thử bài khó hơn, hãy chọn ${e(data.next_level)} ở mục Trình độ hiện tại.</div>`:''}<details class="academy-guide" ${p.configured?'':'open'}><summary>Gợi ý cách học ở trình độ ${p.level}</summary><h2>${e(g.title)}</h2><p>${e(g.intro)}</p><div class="academy-guide-steps">${g.steps.map(([title,copy,href],i)=>`<article><span class="eyebrow">BƯỚC ${i+1}</span><h3>${e(title)}</h3><p>${e(copy)}</p><a class="link-btn" href="${e(href)}">Bắt đầu học →</a></article>`).join('')}</div><p class="notice">${e(g.tip)}</p></details><details class="academy-guide"><summary>Các bài học được chọn như thế nào?</summary><p>${e(data.method)}</p></details>`;
        area.querySelector('form').onsubmit=async ev=>{
          ev.preventDefault();const form=ev.currentTarget,b=form.querySelector('button');b.disabled=true;
          try{const fields=new FormData(form);data=await api('/learn/plan/',{method:'PATCH',data:{level:fields.get('level'),goal:fields.get('goal'),daily_minutes:Number(fields.get('daily_minutes'))}});if(!active())return;render();toast('Đã cập nhật lộ trình.');}catch(err){if(active())form.querySelector('[role="status"]').textContent=err.message;}finally{b.disabled=false;}
        };
      };render();return;
    }
    const data=await api('/learn/sources/');if(!active())return;
    const kinds={grammar:'Ngữ pháp',vocabulary:'Từ vựng',dictionary:'Từ điển',ielts:'IELTS',toeic:'TOEIC'};
    area.innerHTML=`<header class="academy-heading"><span class="eyebrow">HỌC THÊM TỪ NGUỒN TIN CẬY</span><h1>Tài liệu học thêm</h1><p>Tài liệu tham khảo từ các tổ chức giáo dục để đọc thêm sau bài học.</p></header><section class="source-lessons"><div><h2>Học ngữ pháp ngay trên LexiRead</h2><p>Có bài giảng bằng tiếng Việt, ví dụ từng bước và bài tập kèm lời giải.</p></div><a class="btn primary" href="#learn/grammar">Vào bài học ngữ pháp →</a></section><div class="academy-filters"><label>Trình độ<select data-level>${options('')}</select></label><label>Nội dung<select data-kind><option value="">Tất cả nội dung</option>${Object.entries(kinds).map(([v,t])=>`<option value="${v}">${t}</option>`).join('')}</select></label></div><p data-count role="status"></p><div class="academy-grid" data-cards></div>`;
    const draw=()=>{const l=area.querySelector('[data-level]').value,k=area.querySelector('[data-kind]').value,rows=data.items.filter(r=>(!l||r.levels.includes(l))&&(!k||r.kind===k));area.querySelector('[data-count]').textContent=rows.length+' nguồn học';area.querySelector('[data-cards]').innerHTML=rows.length?rows.map(r=>`<article class="academy-card"><span class="eyebrow">${e(r.provider)} · ${e(kinds[r.kind])}</span><h2>${e(r.title)}</h2><p>${e(r.description_vi)}</p><div class="academy-card-bottom"><small>${e(r.levels.join(' · '))}</small>${link(r.url,'Mở tài liệu')}</div></article>`).join(''):'<p class="empty-state">Chưa tìm thấy tài liệu phù hợp. Thử đổi trình độ hoặc loại nội dung.</p>';};
    area.querySelectorAll('select').forEach(x=>x.onchange=draw);draw();
  }
  async function detail(root,kind,id,epoch){
    const ticket=++generation,active=()=>ticket===generation&&epoch===state.routeEpoch;
    root.innerHTML=shell(kind);const area=root.querySelector('[data-academy-root]');
    if(window.LEXIREAD_PREVIEW){area.textContent='Mở bản web có tài khoản để học và lưu tiến độ phần này.';return;}
    const data=await api(`/learn/${kind}/${encodeURIComponent(id)}/`);if(!active())return;
    const back=`<a class="link-btn" href="#learn/${kind}">← ${names[kind]}</a>`;
    const references=`<details class="academy-guide"><summary>Nguồn tham khảo</summary><p>Nội dung và bài tập do LexiRead biên soạn; các tài liệu dưới đây dùng để đối chiếu cách dùng.</p><div class="button-row">${data.source_urls.map((u,i)=>link(u,`Tài liệu ${i+1}`)).join('')}</div></details>`;
    area.innerHTML=`${back}<header class="academy-heading"><span class="level-pill">${data.level}</span><h1>${e(data.title)}</h1><p>${e(data.summary||data.description)}</p></header>`+(kind==='grammar'?window.LexiGrammar.lessonHTML(data,references,quizHTML(data.questions)):`<div class="collection-actions"><p>Chọn từ cần học rồi nhấn Lưu từ đã chọn.</p><button type="button" class="btn primary" data-save-words>Lưu từ đã chọn</button><button type="button" class="btn secondary" data-study-collection ${data.words.some(w=>w.saved)?'':'disabled'}>Ôn bộ từ này →</button><button type="button" class="link-btn" data-collection-practice aria-pressed="false">Luyện ${data.questions.length} câu</button><p role="status" data-save-status></p></div><div class="academy-grid collection-grid">${data.words.map((w,i)=>`<article class="academy-card"><label class="word-select"><input type="checkbox" value="${i}" ${w.saved?'':'checked'}><span lang="en" data-no-i18n>${e(w.word)}</span><small>${w.saved?'Đã có trong kho':e(w.part_of_speech)}</small></label><p><strong>${e(w.meaning_vi)}</strong></p><p lang="en" data-no-i18n>${e(w.example)}</p><p class="muted">${e(w.example_translation)}</p><p class="word-pattern" data-no-i18n>${e(w.usage_pattern)}</p></article>`).join('')}</div>`)+(kind==='grammar'?'':references+`<div data-quiz>${quizHTML(data.questions)}</div>`);
    if(kind==='vocabulary'){
      area.querySelector('[data-quiz]').hidden=true;
      area.querySelector('[data-study-collection]').onclick=()=>{state.study=null;state.studySettings={...state.studySettings,tag:data.title,reading:'',scope:'all'};location.hash='study';};
      area.querySelector('[data-collection-practice]').onclick=ev=>{const show=ev.currentTarget.getAttribute('aria-pressed')!=='true';ev.currentTarget.setAttribute('aria-pressed',String(show));ev.currentTarget.textContent=show?'Xem lại bộ từ':`Luyện ${data.questions.length} câu`;area.querySelector('.collection-grid').hidden=show;area.querySelector('[data-quiz]').hidden=!show;if(show)area.querySelector('[data-quiz]').scrollIntoView({behavior:'smooth',block:'start'});};
    }
    if(kind==='vocabulary')area.querySelector('[data-save-words]').onclick=async ev=>{
      const b=ev.currentTarget,status=area.querySelector('[data-save-status]'),indices=[...area.querySelectorAll('.word-select input:checked')].map(x=>Number(x.value));
      if(!indices.length){status.textContent='Chọn ít nhất một từ để lưu.';return;}b.disabled=true;
      try{const result=await api(`/learn/vocabulary/${encodeURIComponent(id)}/save/`,{method:'POST',data:{indices}});if(!active())return;area.querySelector('[data-study-collection]').disabled=false;status.textContent=`Đã lưu ${result.created} từ mới${result.existing?`; ${result.existing} từ đã có trong kho`:''}.`;area.querySelectorAll('.word-select input:checked').forEach(x=>{x.checked=false;x.closest('label').querySelector('small').textContent='Đã có trong kho';});await refreshBoot();}catch(err){if(active())status.textContent=err.message;}finally{b.disabled=false;}
    };
    if(kind==='vocabulary')window.LexiTopics.attachCards(area,data);
    if(kind==='grammar')window.LexiGrammar.attachLesson(area);
    const quiz=area.querySelector('[data-quiz]');let token=uid();
    const bind=()=>{quiz.querySelector('form').onsubmit=async ev=>{
      ev.preventDefault();const form=ev.currentTarget,b=form.querySelector('button[type="submit"]');b.disabled=true;
      const fields=new FormData(form),answers=Object.fromEntries(data.questions.map(q=>[q.id,Number(fields.get(q.id))]));
      try{const result=await api(`/learn/${kind}/${encodeURIComponent(id)}/submit/`,{method:'POST',data:{answers,token,version:data.version}});if(!active())return;quiz.innerHTML=resultHTML(result);if(kind==='grammar')area.querySelector('.grammar-practice-help').hidden=true;quiz.querySelector('[tabindex]').focus();quiz.querySelector('[data-wrong-only]').onchange=ev=>{quiz.querySelectorAll('.is-correct').forEach(x=>x.hidden=ev.target.checked);quiz.querySelector('.academy-all-correct').hidden=!(ev.target.checked&&result.score===result.total);};quiz.querySelector('[data-academy="retry"]').onclick=()=>{token=uid();quiz.innerHTML=quizHTML(data.questions);if(kind==='grammar')area.querySelector('.grammar-practice-help').hidden=false;bind();quiz.querySelector('input')?.focus();};await refreshBoot();}catch(err){if(active())form.querySelector('[role="status"]').textContent=err.message;}finally{b.disabled=false;}
    };};bind();
  }
  window.LexiAcademy={page,detail,safeURL:safe,quizHTML,resultHTML};
})();
