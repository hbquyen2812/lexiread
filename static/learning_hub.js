'use strict';
/* Local learning preferences and guide examples. Never a predicted test score. */
(() => {
  const esc = value => String(value ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const norm = s => String(s ?? '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d').trim();
  const read = (key,fallback) => {try{return JSON.parse(localStorage.getItem(key)) ?? fallback;}catch{return fallback;}};
  const write = (key,value) => {try{localStorage.setItem(key,JSON.stringify(value));return true;}catch{return false;}};
  const json = id => {try{const x=JSON.parse(document.getElementById(id)?.textContent || '[]');return Array.isArray(x)?x:[];}catch{return [];}};
  const guideItems = () => json('strategy-guides-data');
  const publicPage = () => !!document.querySelector('[data-guide-public]');
  const practiceHref = guide => {
    const track=guide.practice_query?.track==='toeic'?'toeic':'ielts';
    const kind=guide.practice_query?.kind || '';
    const readingKinds=['main_idea','detail','tfng','ynng','vocabulary','inference','matching_heading','matching_information','gap_fill','short_answer'];
    const route=track==='toeic' ? (kind.includes('5')?'toeic/5':kind.includes('6')?'toeic/6':kind.includes('7')?'toeic/7':'toeic') : 'ielts'+(readingKinds.includes(kind)?'/'+kind:'');
    return publicPage()?'/login/?next='+encodeURIComponent('/#'+route):'#'+route;
  };
  function guideCard(g) {
    const done=read('lexiread.guides.read',[]);return `<article class="guide-card">${window.LexiVisuals?.guide(g.id)||''}<div class="guide-card-meta"><span class="chip">${g.exam.toUpperCase()}</span><span>${g.duration_minutes} phút đọc</span></div><h3>${esc(g.title)}</h3><p>${esc(g.summary_vi)}</p><a class="btn small secondary" href="#guides/${esc(g.id)}">${Array.isArray(done)&&done.includes(g.id)?'Đọc lại hướng dẫn':'Xem cách làm'} →</a></article>`;
  }
  let guideFilter={exam:'',q:''};
  function guideList(root) {
    const items=guideItems();
    root.replaceChildren(window.LexiDOM.fragment(`${window.LexiChannels?.tabs("guides")||""}<section class="hub-heading"><span class="eyebrow">HIỂU CÁCH LÀM, RỒI LUYỆN TẬP</span><h1>Học cách làm từng dạng bài.</h1><p>Cách làm từng bước, có ví dụ để thử ngay.</p><div class="hub-controls"><div class="filter-chips" role="group" aria-label="Chọn kỳ thi">${[['','Tất cả'],['ielts','IELTS'],['toeic','TOEIC']].map(([v,l])=>`<button type="button" class="filter-chip" data-guide-exam="${v}" aria-pressed="${v===guideFilter.exam}">${l}</button>`).join('')}</div><input type="search" data-guide-search aria-label="Tìm hướng dẫn" placeholder="Tìm dạng bài, ví dụ: Not Given, Part 7…" value="${esc(guideFilter.q)}"></div><p class="hub-result-count" data-guide-count role="status"></p></section><div class="guide-grid" data-guide-results></div>`));
    updateGuides(root,items);
  }
  function updateGuides(root,items=guideItems()) {
    const filtered=items.filter(g=>(!guideFilter.exam||g.exam===guideFilter.exam)&&norm([g.title,g.summary_vi,...g.question_types].join(' ')).includes(norm(guideFilter.q)));
    root.querySelector('[data-guide-results]').replaceChildren(window.LexiDOM.fragment(filtered.length?filtered.map(guideCard).join(''):'<p class="empty-state">Chưa có hướng dẫn phù hợp. Thử từ khóa khác hoặc chọn Tất cả.</p>'));
    root.querySelector('[data-guide-count]').textContent=filtered.length+' hướng dẫn';
    root.querySelectorAll('[data-guide-exam]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.guideExam===guideFilter.exam)));
  }
  function guidePage(root,id='') {
    if(id==='youtube'){window.LexiChannels.page(root);return;}
    if(id==='methods'){window.LexiMethods.page(root);return;}
    root.classList.add('learning-hub');root.dataset.guideRoot='';
    const guide=guideItems().find(g=>g.id===id);
    if(!id || ['ielts','toeic'].includes(id)){if(id)guideFilter.exam=id;guideList(root);return;}
    if(!guide){root.innerHTML='<h1>Chưa tìm thấy hướng dẫn</h1><a class="btn" href="#guides">Về cẩm nang</a>';return;}
    const ex=guide.worked_example,done=read('lexiread.guides.read',[]);
    root.replaceChildren(window.LexiDOM.fragment(`<article class="guide-detail" data-guide-id="${esc(guide.id)}"><a class="link-btn" href="#guides/${guide.exam}">← Cẩm nang ${guide.exam.toUpperCase()}</a><header class="hub-heading guide-illustrated-heading">${window.LexiVisuals?.guide(guide.id)||''}<span class="eyebrow">${guide.exam.toUpperCase()} · ${guide.duration_minutes} PHÚT ĐỌC</span><h1>${esc(guide.title)}</h1><p>${esc(guide.summary_vi)}</p></header><div class="guide-layout"><div><section aria-label="Cách làm"><h2>Làm theo từng bước</h2><ol class="guide-steps">${guide.steps.map(s=>`<li><h3>${esc(s.title)}</h3><p>${esc(s.body)}</p></li>`).join('')}</ol></section><section class="guide-example"><span class="eyebrow">VÍ DỤ NGẮN</span><h2>Thử làm trước khi xem đáp án.</h2><blockquote lang="en">${esc(ex.passage)}</blockquote><p lang="en"><strong>${esc(ex.question)}</strong></p><form data-guide-example><fieldset><legend class="sr-only">Câu trả lời của bạn</legend>${ex.options?.length?ex.options.map((o,i)=>`<label class="reading-option"><input type="radio" name="example" value="${i}"><span lang="en">${esc(o)}</span></label>`).join(''):'<label>Câu trả lời<input name="example" type="text" maxlength="150" autocomplete="off" lang="en"></label>'}</fieldset><button class="btn primary" type="submit">Kiểm tra câu trả lời</button><p data-guide-feedback role="status"></p></form><details class="guide-answer"><summary>Xem đáp án và cách suy luận</summary><p lang="en"><strong>${esc(ex.answer)}</strong></p><p>${esc(ex.explanation_vi)}</p></details></section></div><aside><section class="guide-traps">${window.LexiVisuals?.object('pencil','small')||''}<h2>Chỗ dễ nhầm</h2><ul>${guide.traps.map(t=>`<li>${esc(t)}</li>`).join('')}</ul></section><section class="guide-next"><h2>Thử trên một bài đọc</h2><a class="btn primary" href="${practiceHref(guide)}">Luyện ${guide.exam.toUpperCase()} →</a><button class="btn" type="button" data-guide-done aria-pressed="${Array.isArray(done)&&done.includes(id)}">${Array.isArray(done)&&done.includes(id)?'✓ Đã đọc hướng dẫn':'Đánh dấu đã đọc'}</button><small data-guide-save-note></small></section></aside></div><footer class="guide-sources"><details><summary>Nguồn tham khảo và thông tin bài</summary><ul>${guide.sources.map(s=>`<li><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)} ↗</a></li>`).join('')}</ul><p>Nguồn được kiểm tra ngày ${esc(guide.checked_at)}. Ví dụ do Lexivela biên soạn. Dấu đã đọc chỉ lưu trên thiết bị này.</p></details></footer></article>`));
  }
  const plans=new WeakMap();
  function plan(root,data,selection=null) {
    data=data&&typeof data==='object'?data:{};plans.set(root,data);
    const raw=selection??read('lexiread.plan.v1',{}),saved=raw&&typeof raw==='object'&&!Array.isArray(raw)?raw:{},goal=['general','ielts','toeic'].includes(saved.goal)?saved.goal:'general',minutes=[15,30,45].includes(saved.minutes)?saved.minutes:15;
    const available=Array.isArray(data[goal])?data[goal]:[],pool=available.filter(x=>goal==='toeic'?!x.attempt_count:x.status!=='completed');
    const choices=pool.length?pool:available,day=Math.floor((Date.now()+7*60*60*1000)/86400000),item=choices.length?choices[day%choices.length]:null;
    const due=Number.isInteger(data.due)&&data.due>0?data.due:0;
    const guide=guideItems().find(g=>g.exam===goal),budgets=minutes===15?[3,10,2]:minutes===30?[5,20,5]:[5,30,10];
    root.replaceChildren(window.LexiDOM.fragment(`<section class="daily-plan"><div class="section-title"><div><span class="eyebrow">GỢI Ý CHO HÔM NAY</span><h2>Lên kế hoạch cho buổi học</h2><p>Chọn mục tiêu và thời gian bạn có thể dành cho buổi học.</p></div></div><div class="plan-controls"><label>Mục tiêu<select data-plan-goal aria-label="Mục tiêu"><option value="general" ${goal==='general'?'selected':''}>Đọc tiếng Anh mỗi ngày</option><option value="ielts" ${goal==='ielts'?'selected':''}>IELTS Reading</option><option value="toeic" ${goal==='toeic'?'selected':''}>TOEIC Reading</option></select></label><label>Thời gian hôm nay<select data-plan-time aria-label="Thời gian hôm nay">${[15,30,45].map(m=>`<option value="${m}" ${minutes===m?'selected':''}>${m} phút</option>`).join('')}</select></label></div><ol class="plan-steps"><li><span>01 · ${budgets[0]} PHÚT</span><h3>${guide?'Xem cách làm bài':'Chọn bài đọc phù hợp'}</h3><p>${guide?esc(guide.title):'Đọc tiêu đề, xem các đề mục và đoán nội dung chính.'}</p><a href="${guide?'#guides/'+guide.id:'#catalog'}">${guide?'Mở hướng dẫn':'Khám phá thư viện'} →</a></li><li><span>02 · ${budgets[1]} PHÚT</span><h3>Đọc và tự kiểm tra</h3><p lang="en">${item?esc(item.title):'Chọn bài đọc theo chủ đề bạn thích.'}</p><a href="${item?'#'+(goal==='toeic'?'toeic-set/':'lesson/')+esc(item.slug):'#'+(goal==='general'?'catalog':goal)}">Bắt đầu bài luyện →</a></li><li><span>03 · ${budgets[2]} PHÚT</span><h3>Ôn lại sau khi đọc</h3><p>${due?due+' từ cần ôn hôm nay.':'Lưu vài từ hữu ích từ bài vừa đọc.'} Xem lời giải ở những câu chưa đúng trước khi học bài tiếp theo.</p><a href="#${due?'study':'vocabulary'}">${due?'Ôn từ đến hạn':'Mở kho từ'} →</a></li></ol><p class="fineprint">Bạn có thể đổi bài hoặc thời gian bất cứ lúc nào. <span data-plan-save-note></span></p></section>`));
  }
  const catalogs=new WeakMap();
  function toeicCatalog(root,items,part='') {
    const s={items,part:['5','6','7'].includes(part)?part:'',q:'',status:'',duration:'',limit:9};catalogs.set(root,s);
    root.replaceChildren(window.LexiDOM.fragment(`<section class="practice-library"><div class="progress-tabs" role="group" aria-label="Tiến độ TOEIC">${[['','Tất cả'],['new','Chưa làm'],['done','Đã làm']].map(([v,l])=>`<button type="button" data-toeic-progress="${v}" aria-pressed="${s.status===v}">${l}</button>`).join('')}</div><div class="hub-controls"><input data-toeic-search type="search" aria-label="Tìm bộ TOEIC" placeholder="Tìm đề theo tên…"><select data-toeic-part aria-label="Lọc theo Part"><option value="">Tất cả Part</option>${[5,6,7].map(p=>`<option value="${p}" ${s.part===String(p)?'selected':''}>Part ${p}</option>`).join('')}</select><select data-toeic-duration aria-label="Thời gian luyện"><option value="">Mọi thời lượng</option><option value="15">Tối đa 15 phút</option><option value="25">Tối đa 25 phút</option></select></div><p data-toeic-count class="hub-result-count" role="status"></p><div class="practice-card-grid" data-toeic-results></div><div class="show-more-row"><button type="button" class="btn" data-toeic-more>Xem thêm bộ luyện ↓</button></div></section>`));
    updateToeic(root);
  }
  function toeicArtwork(item){
    const text=norm(item.title+' '+item.description);
    const themes=[['travel',/travel|transport|flight|airport|hotel|accommodation/],['food',/catering|restaurant|food|cafe/],['city',/building|spaces|community/],['nature',/volunteer|environment/],['technology',/technology|repairs|equipment/],['school',/recruitment|training|word forms|workshop|job application/]];
    return themes.find(([,pattern])=>pattern.test(text))?.[0]||(item.parts.includes(5)?'school':item.parts.includes(6)?'work':'reading');
  }
  function updateToeic(root) {
    const s=catalogs.get(root),items=s.items.filter(x=>(!s.part||x.parts.includes(Number(s.part)))&&norm(x.title+' '+x.description+' '+x.mode_label).includes(norm(s.q))&&(!s.status||(s.status==='new'?!x.attempt_count:!!x.attempt_count))&&(!s.duration||x.duration_minutes<=Number(s.duration)));
    root.querySelector('[data-toeic-count]').textContent=items.length+' bộ luyện · '+items.reduce((sum,x)=>sum+x.question_count,0)+' câu hỏi';
    document.querySelectorAll('.toeic-parts a').forEach(link=>{if(link.getAttribute('href')==='#toeic/'+s.part)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');});
    root.querySelectorAll('[data-toeic-progress]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.toeicProgress===s.status)));
    root.querySelector('[data-toeic-results]').replaceChildren(window.LexiDOM.fragment(items.length?items.slice(0,s.limit).map(x=>`<article class="practice-card" data-practice-status="${x.attempt_count?'done':'new'}"><div class="practice-art"><img src="${window.LexiLibrary.artwork[toeicArtwork(x)]}" width="640" height="360" alt="" loading="lazy" decoding="async"><span class="reading-status ${x.attempt_count?'completed':'new'}">${x.attempt_count?'✓ Đã làm':'Chưa làm'}</span></div><div class="practice-card-body"><div class="practice-card-meta"><span>${x.parts.map(p=>'Part '+p).join(' · ')}</span><span>${esc(String(x.level||'').split('·')[0].trim())}</span></div><h3 lang="en" data-no-i18n>${esc(x.title)}</h3><p>${esc(x.description)}</p><div class="practice-card-info">${x.question_count} câu hỏi <span>·</span> ${x.duration_minutes} phút</div><div class="card-footer"><span class="lesson-score">${x.attempt_count?'Tốt nhất '+x.best_score+'/'+x.question_count:''}</span><a class="btn small secondary" href="#toeic-set/${esc(x.slug)}">${x.attempt_count?'Luyện lại':'Bắt đầu'} →</a></div></div></article>`).join(''):'<p class="empty-state">Chưa có bộ luyện phù hợp. Thử đổi Part, thời gian hoặc từ khóa.</p>'));
    root.querySelector('[data-toeic-more]').hidden=items.length<=s.limit;
  }
  document.addEventListener('click',e=>{
    if(publicPage()&&e.target.closest('.skip-link')){e.preventDefault();document.querySelector('[data-guide-public]').focus();return;}
    const exam=e.target.closest('[data-guide-exam]');if(exam){guideFilter.exam=exam.dataset.guideExam;updateGuides(exam.closest('[data-guide-root]'));}
    const done=e.target.closest('[data-guide-done]');if(done){const id=done.closest('[data-guide-id]').dataset.guideId,raw=read('lexiread.guides.read',[]),seen=new Set(Array.isArray(raw)?raw:[]);seen.has(id)?seen.delete(id):seen.add(id);if(write('lexiread.guides.read',[...seen])){done.setAttribute('aria-pressed',String(seen.has(id)));done.textContent=seen.has(id)?'✓ Đã đọc hướng dẫn':'Đánh dấu đã đọc';}else done.parentElement.querySelector('[data-guide-save-note]').textContent='Trình duyệt không cho lưu. Bạn vẫn có thể đọc và luyện tập.';}
    const progress=e.target.closest('[data-toeic-progress]');if(progress){const root=progress.closest('[data-toeic-library]');catalogs.get(root).status=progress.dataset.toeicProgress;catalogs.get(root).limit=9;updateToeic(root);}
    const more=e.target.closest('[data-toeic-more]');if(more){const root=more.closest('[data-toeic-library]');catalogs.get(root).limit+=9;updateToeic(root);}
  });
  document.addEventListener('input',e=>{if(e.target.matches('[data-guide-search]')){guideFilter.q=e.target.value;updateGuides(e.target.closest('[data-guide-root]'));}if(e.target.matches('[data-toeic-search]')){const root=e.target.closest('[data-toeic-library]');catalogs.get(root).q=e.target.value;catalogs.get(root).limit=9;updateToeic(root);}});
  document.addEventListener('change',e=>{
    if(e.target.matches('[data-plan-goal],[data-plan-time]')){const root=e.target.closest('[data-daily-plan]'),selection={goal:root.querySelector('[data-plan-goal]').value,minutes:Number(root.querySelector('[data-plan-time]').value)},saved=write('lexiread.plan.v1',selection);plan(root,plans.get(root),selection);if(!saved)root.querySelector('[data-plan-save-note]').textContent='Trình duyệt không cho lưu. Lựa chọn này vẫn áp dụng trong màn hình hiện tại.';}
    for(const name of ['part','status','duration'])if(e.target.hasAttribute('data-toeic-'+name)){const root=e.target.closest('[data-toeic-library]');catalogs.get(root)[name]=e.target.value;catalogs.get(root).limit=9;updateToeic(root);}
  });
  document.addEventListener('submit',e=>{
    if(!e.target.matches('[data-guide-example]'))return;e.preventDefault();const form=e.target,g=guideItems().find(x=>x.id===form.closest('[data-guide-id]').dataset.guideId),ex=g.worked_example,choice=new FormData(form).get('example'),feedback=form.querySelector('[data-guide-feedback]');
    if(choice===null||String(choice).trim()===''){feedback.textContent='Hãy thử một câu trả lời trước nhé.';return;}
    const answer=ex.options?.length?ex.options[Number(choice)]:String(choice),accepted=ex.accepted_answers?.length?ex.accepted_answers:[ex.answer],correct=accepted.some(expected=>norm(answer)===norm(expected));feedback.className='feedback'+(correct?'':' wrong');feedback.textContent=(correct?'✓ Đúng. ':'Chưa đúng. ')+ex.explanation_vi;form.parentElement.querySelector('details').open=true;
  });
  function publicRoute(){const root=document.querySelector('[data-guide-public]');if(!root)return;guidePage(root,(location.hash||'').replace(/^#guides\/?/,''));window.scrollTo({top:0,behavior:'instant'});root.focus({preventScroll:true});}
  document.addEventListener('DOMContentLoaded',publicRoute);window.addEventListener('hashchange',publicRoute);
  window.LexiHub={guidePage,plan,toeicCatalog,toeicArtwork};
})();
