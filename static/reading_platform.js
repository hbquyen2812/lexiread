'use strict';
/* Shared UI for the curated library and private reader. Loaded before app.js.
   It never calls a model directly or embeds an API key. All content is escaped. */
const readingKinds={main_idea:'Ý chính',detail:'Chi tiết',tfng:'TRUE / FALSE / NOT GIVEN',ynng:'YES / NO / NOT GIVEN',vocabulary:'Từ trong ngữ cảnh',inference:'Suy luận',matching_heading:'Ghép tiêu đề',matching_information:'Ghép thông tin',gap_fill:'Điền từ',short_answer:'Trả lời ngắn'};
function lessonStatus(r){return r.status==='completed'?'Đã đọc':r.status==='started'?'Đang đọc':'Chưa đọc';}
function lessonCard(r){
  const status=['completed','started'].includes(r.status)?r.status:'new';
  return `<article class="lesson-card" data-level="${esc(r.level)}" data-track="${esc(r.track||'general')}" data-read-status="${status}"><div class="lesson-card-top"><span class="level-pill ${esc(r.level.toLowerCase())}">${esc(r.level)}</span><span class="reading-status ${status}">${status==='completed'?'✓ ':status==='started'?'◐ ':''}${lessonStatus(r)}</span></div>${window.LexiLibrary.cover(r)}<h3 data-no-i18n lang="en">${esc(r.title)}</h3><p class="lesson-summary">${esc(r.summary)}</p><div class="lesson-meta">${esc(r.word_count)} từ <span>·</span> ${esc(r.estimated_minutes||Math.max(5,Math.round(r.word_count/120+r.question_count*.75)))} phút <span>·</span> ${esc(r.question_count)} câu hỏi</div><div class="card-footer"><span class="lesson-score">${r.progress?.quiz_total?`Tốt nhất ${esc(r.progress.quiz_best)}/${esc(r.progress.quiz_total)}`:r.favorite?'★ Yêu thích':''}</span><a class="btn small secondary" href="#lesson/${esc(r.slug)}">${status==='completed'?'Đọc lại':r.reading_id?'Đọc tiếp':'Bắt đầu'} →</a></div></article>`;
}
async function readingHome(epoch){
  const [c,ielts,community]=await Promise.all([api('/catalog/?track=general'),api('/catalog/?track=ielts'),api('/community/').catch(()=>null)]);if(epoch!==state.routeEpoch)return;
  const s=state.boot.stats,featured=['A1','A2','B1'].map(l=>c.items.find(x=>x.level===l)).filter(Boolean);
  $('#main').replaceChildren(window.LexiDOM.fragment(`<section class="hero reading-hero garden-hero"><div><span class="eyebrow" data-i18n="hero.chip">Một thói quen nhỏ. Một thế giới rộng hơn.</span><h1><span data-i18n="hero.title1">Đọc một chút.</span><br><em data-i18n="hero.title2">Tiến xa mỗi ngày.</em></h1><p data-i18n="hero.caption">Luyện đọc với câu hỏi, lời giải và từ vựng theo ngữ cảnh.</p><div class="button-row"><a class="btn primary" href="#catalog" data-i18n="hero.start">Tìm bài đọc của bạn ↗</a><a class="btn secondary import-cta" href="#word-import"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 16V3m-5 5 5-5 5 5M4 14v7h16v-7"/></svg>Nhập bộ từ cá nhân</a></div></div><figure class="garden-welcome"><img src="/static/illustrations/lexi-reading-garden.webp" width="1448" height="1086" alt="Bạn thỏ tai lá đang đọc sách trong khu vườn nhỏ của LexiRead" decoding="async" data-i18n-alt="brand.imageAlt"><figcaption data-i18n="brand.welcome">Góc nhỏ của bạn. Mỗi ngày một điều mới.</figcaption></figure></section>
  <section class="stats">${[[(c.total??c.items.length)+(ielts.total??ielts.items.length),'Bài đọc trong thư viện'],[s.completed_readings||0,'Bài đã đọc'],[s.total,'Thẻ trong kho riêng'],[s.due??s.overdue,'Từ đang chờ ôn']].map(([n,l])=>`<div class="stat"><div class="stat-top">${l}</div><div class="stat-value">${count(n)}</div></div>`).join('')}</section>
  <section class="home-features"><article class="deck-feature"><span class="eyebrow">BỘ TỪ CỦA RIÊNG BẠN</span><h2>Nhập một lần.<br>Ôn cả bộ.</h2><p>Tạo bộ từ theo chủ đề với mẫu gợi ý, nhập file hoặc dán nội dung. Xem trước, đặt tên và lưu để ôn mỗi ngày.</p><div class="button-row"><a class="btn primary" href="#word-import">Nhập bộ từ cá nhân →</a><a class="link-btn" href="#vocabulary">Mở kho từ của tôi</a></div></article><article class="foundation-shortcut"><div><span class="eyebrow">MỘT ĐIỂM BẮT ĐẦU VỪA SỨC</span><h2>Học gì tiếp theo?</h2><p>Ngữ pháp, từ vựng và bài đọc theo trình độ, với lộ trình dành cho bạn.</p></div><a class="btn secondary" href="#learn/plan">Khám phá lộ trình →</a></article></section>${window.LexiMethods.teaser()}${dailyReviewCallout(s)}<div class="section-title"><div><h2>Chọn một điểm bắt đầu</h2><p data-i18n="library.copy">Chọn trình độ và tìm một bài bạn muốn đọc hôm nay.</p></div><a class="link-btn" href="#catalog">Xem thư viện →</a></div>
  ${window.LexiLibrary.levelPicker(window.LexiLibrary.savedLevel('general')).replaceAll('data-action="library-level"','data-action="choose-level"')}<div class="lesson-grid">${featured.map(lessonCard).join('')}</div>
  <section class="public-section"><div class="section-title"><h2 data-i18n="practice.title">Luyện đúng hướng bạn cần.</h2><a class="link-btn" href="#resources" data-i18n="brand.officialLink">Khám phá đề mẫu chính thức ↗</a></div><div class="practice-grid"><article class="practice-path ielts"><span class="chip" data-i18n="ielts.chip">Đọc học thuật · B1–C1</span><h3>IELTS Reading</h3><p data-i18n="ielts.copy"></p><a class="btn primary" href="#ielts" data-i18n="ielts.start">Khám phá IELTS →</a></article><article class="practice-path"><span class="chip" data-i18n="toeic.chip">Tiếng Anh trong công việc</span><h3>TOEIC Reading</h3><p data-i18n="toeic.copy"></p><a class="btn primary" href="#toeic" data-i18n="toeic.start">Luyện TOEIC →</a></article></div></section>${window.LexiMethods.community(community)}`));
}
async function ieltsPage(epoch,kind=''){if(state.ieltsRouteKind!==kind){state.ieltsFilters ||= {};state.ieltsFilters.kind=Object.hasOwn(readingKinds,kind)?kind:'';state.ieltsFilters.page=1;state.ieltsRouteKind=kind;}return catalogPage(epoch,'ielts');}
async function practiceGroupsPage(epoch){
  if(window.LEXIREAD_PREVIEW){$('#main').replaceChildren(window.LexiDOM.fragment(heading('Bộ luyện Reading','Mở bản web có tài khoản để học các bộ luyện v3.')));return;}
  const [catalogue,response]=await Promise.all([api('/practice-groups/'),fetch('/static/practice_resources.json')]);
  if(!response.ok)throw new Error('Chưa tải được danh sách bộ luyện. Bạn thử lại nhé.');
  const resources=await response.json();if(epoch!==state.routeEpoch)return;
  const groups=catalogue.items;
  const root=$('#main');root.replaceChildren(window.LexiDOM.fragment(heading('Bộ luyện Reading','Chọn một bộ và luyện từng phần. Các bài luyện do LexiRead biên soạn.')+`<div class="catalog-filters"><label>Loại nội dung<select data-practice-kind><option value="full_reading">Đề Reading theo từng phần</option><option value="practice_bundle">Bộ luyện ngắn</option><option value="external">Tài liệu đọc thêm</option></select></label><label>Mục tiêu<select data-practice-track><option value="">Tất cả</option><option value="ielts">IELTS</option><option value="toeic">TOEIC</option><option value="general">Tiếng Anh hằng ngày</option></select></label><label>Tìm bộ luyện<input type="search" data-practice-search placeholder="Tìm theo tên…"></label></div><p data-practice-count role="status"></p><div data-practice-rows></div><div class="topic-pagination"><button class="btn secondary" data-practice-prev>← Trang trước</button><span data-practice-page></span><button class="btn secondary" data-practice-next>Trang tiếp →</button></div>`));
  let page=1;
  const draw=()=>{
    const kind=root.querySelector('[data-practice-kind]').value,track=root.querySelector('[data-practice-track]').value,q=root.querySelector('[data-practice-search]').value.trim().toLowerCase();
    const rows=(kind==='external'?resources:groups.filter(r=>r.test_kind===kind)).filter(r=>{
      const t=r.exam_type||r.track||'',category=t.startsWith('ielts')?'ielts':t==='toeic'?'toeic':'general';return (!track||track===category)&&r.title.toLowerCase().includes(q);
    });const pages=Math.max(1,Math.ceil(rows.length/12));page=Math.min(page,pages);
    root.querySelector('[data-practice-count]').textContent=rows.length+' kết quả';
    root.querySelector('[data-practice-rows]').replaceChildren(window.LexiDOM.fragment(rows.slice((page-1)*12,page*12).map(r=>kind==='external'?`<article class="panel practice-group"><h2 lang="en" data-no-i18n>${esc(r.title)}</h2><p>${esc(r.publisher)}${r.cefr_label?' · '+esc(r.cefr_label):''}</p><a class="btn secondary" href="${esc(/^https:\/\//.test(r.url)?r.url:'#')}" target="_blank" rel="noopener noreferrer">Mở tài liệu ↗</a></article>`:`<details class="panel practice-group"><summary>${esc(r.title)}</summary><p>${esc(r.question_count)} câu · ${r.sections.length} phần</p><ol>${r.sections.map(s=>`<li><a class="link-btn" href="${esc(s.href)}"><span lang="en" data-no-i18n>${esc(s.title)}</span> →</a></li>`).join('')}</ol></details>`).join('')||'<div class="empty-state">Chưa có kết quả phù hợp.</div>'));
    root.querySelector('[data-practice-prev]').disabled=page===1;root.querySelector('[data-practice-next]').disabled=page===pages;root.querySelector('[data-practice-page]').textContent=page+' / '+pages;
  };
  root.querySelectorAll('select,input').forEach(el=>el.addEventListener(el.tagName==='SELECT'?'change':'input',()=>{page=1;draw();}));
  root.querySelector('[data-practice-prev]').onclick=()=>{page--;draw();};root.querySelector('[data-practice-next]').onclick=()=>{page++;draw();};draw();
}
async function catalogPage(epoch,track='general'){
  const key=track==='ielts'?'ieltsFilters':'catalogFilters';
  state[key] = {q:'',level:window.LexiLibrary.savedLevel(track),topic:'',status:'',favorite:'all',kind:'',page:1,limit:12,...(state[key]||{})};
  const f=state[key];state.libraryTrack=track;
  const c=await api('/catalog/?'+new URLSearchParams({...f,track}));if(epoch!==state.routeEpoch)return;
  state.catalogItems=c.items;
  const intro=track==='ielts'?'<div class="catalog-note"><b>IELTS Reading · luyện kỹ năng theo trình độ</b><span>Bài luyện do LexiRead biên soạn, giúp bạn tập từng kỹ năng đọc.</span><a class="link-btn" href="#resources/ielts">Khám phá bài mẫu chính thức ↗</a></div>':'';
  $('#main').replaceChildren(window.LexiDOM.fragment(heading(track==='ielts'?'IELTS Reading':'Thư viện luyện đọc','Chọn trình độ và chủ đề bạn muốn đọc.')+
    '<p><a class="btn secondary" href="#practice-tests">Khám phá bộ luyện Reading →</a></p>'+window.LexiLibrary.levelPicker(f.level,track)+intro+(track==='ielts'?'<div class="guide-shortcut"><p><b>Học cách làm từng dạng Reading</b><br>Phân biệt Not Given, tìm ý chính, ghép thông tin và điền từ đúng giới hạn.</p><a class="btn secondary" href="#guides/ielts">Mở cẩm nang →</a></div>':'')+
    `<div class="progress-tabs" role="group" aria-label="Tiến độ đọc">${[['','Tất cả'],['new','Chưa đọc'],['started','Đang đọc'],['completed','Đã đọc']].map(([v,l])=>`<button type="button" data-action="catalog-status" data-status="${v}" aria-pressed="${f.status===v}">${l}</button>`).join('')}</div><div class="catalog-filters">${track==='ielts'?`<select id="catalog-kind" aria-label="Dạng câu hỏi"><option value="">Mọi dạng câu hỏi</option>${Object.entries(readingKinds).map(([v,l])=>`<option value="${v}" ${f.kind===v?'selected':''}>${l}</option>`).join('')}</select>`:''}<input id="catalog-search" type="search" placeholder="Tìm tiêu đề hoặc chủ đề…" aria-label="Tìm bài đọc" value="${esc(f.q)}"><select id="catalog-topic" aria-label="Chủ đề"><option value="">Mọi chủ đề</option>${c.topics.map(t=>`<option lang="en" data-no-i18n value="${esc(t)}" ${f.topic===t?'selected':''}>${esc(window.LexiLibrary.topicLabel(t))}</option>`).join('')}</select><select id="catalog-favorite" aria-label="Bài yêu thích">${[['all','Tất cả bài'],['yes','Chỉ yêu thích'],['no','Chưa yêu thích']].map(([v,l])=>`<option value="${v}" ${f.favorite===v?'selected':''}>${l}</option>`).join('')}</select><button class="btn secondary" data-action="catalog-filter">Lọc</button></div><p class="library-result-count" role="status">${c.total??c.items.length} bài phù hợp${f.level?' · '+esc(f.level):''}</p>`+
    (c.items.length?`<div class="lesson-grid">${c.items.map(lessonCard).join('')}</div>`:empty('Chưa có bài phù hợp','Thử chọn “Tất cả”, một chủ đề hoặc mức độ khác.'))+
    `<div class="button-row">${(c.page||1)>1?'<button class="btn" data-action="catalog-prev">← Trang trước</button>':''}${c.has_more?'<button class="btn" data-action="catalog-next">Trang tiếp →</button>':''}</div>`));
}
async function lessonRoute(slug,epoch){
  const r=await api('/catalog/'+encodeURIComponent(slug)+'/open/',{method:'POST',data:{}});
  if(epoch!==state.routeEpoch)return;state.readingTab='text';location.hash='reading/'+r.id;
}
function ensureReadingState(r){
  if(state.homework?.readingId!==r.id){
    state.readingTab='text';
    state.homework={readingId:r.id,answers:{},token:uid(),result:null};
    state.qaDraft='';state.qaSelected='';state.qaHistory=[];
  }
}
function readingExtraTab(box,r){
  if(state.readingTab==='quiz')renderReadingQuiz(box,r);
  else renderReadingHelp(box,r);
}
function evidenceButton(i,quote){return `<blockquote class="quote">${esc(quote)}</blockquote><button class="link-btn" data-action="jump-paragraph" data-index="${i}">Xem đoạn ${i+1} trong bài →</button>`;}
function renderReadingQuiz(box,r){
  const questions=r.lesson?.questions||[];
  if(!questions.length){box.replaceChildren(window.LexiDOM.fragment(empty('Bài này chưa có câu hỏi cố định','Các bài trong thư viện có sẵn bài tập hiểu bài. Bài tự nhập tập trung vào đọc và hỏi đáp.')));return;}
  const hw=state.homework,res=hw.result;
  box.replaceChildren(window.LexiDOM.fragment(`<div class="section-title"><div><h2>Hiểu bài trước, đối chiếu sau.</h2><p class="fineprint">${questions.length} câu hỏi soạn sẵn. Chấm xong sẽ hiện giải thích và bằng chứng; không quy đổi thành band IELTS.</p></div></div>`+
    (res?`<div class="reading-score" role="status"><strong>${res.score} / ${res.total}</strong><div>Câu trả lời đúng<p>Đối chiếu câu gốc để hiểu cả câu đúng lẫn câu sai.</p></div></div>`:'')+
    questions.map((q,i)=>{
      const result=res?.results.find(x=>x.question_id===q.id),textAnswer=['gap_fill','short_answer'].includes(q.kind);
      const options=textAnswer?`<label>Trả lời tối đa ${q.max_words} từ<input type="text" maxlength="200" data-lesson-text="${esc(q.id)}" value="${esc(hw.answers[q.id]||'')}" ${res?'disabled':''}></label>`:q.options.map((o,j)=>`<label class="reading-option ${result?(j===result.answer?'is-correct':j===result.submitted?'is-wrong':''):''}"><input type="radio" data-lesson-question="${esc(q.id)}" name="lesson-${esc(q.id)}" value="${j}" ${hw.answers[q.id]===j?'checked':''} ${res?'disabled':''}><span class="choice-letter">${'ABCDEFGH'[j]}</span><span lang="en" data-no-i18n>${esc(o)}</span></label>`).join('');
      return `<fieldset class="reading-question"><legend class="question-legend"><span>Câu ${i+1}: </span><span lang="en" data-no-i18n>${esc(q.prompt)}</span></legend><div class="reading-question-heading" aria-hidden="true"><span class="chip">${i+1} · ${readingKinds[q.kind]||'Reading'}</span><p lang="en">${esc(q.prompt)}</p></div><div class="reading-options">${options}</div>${result?`<div class="feedback ${result.correct?'':'wrong'}"><strong><span>${result.correct?'✓ Đúng':'Chưa đúng'}</span> · <span lang="en" data-no-i18n>${esc(textAnswer?result.answer:q.options[result.answer])}</span></strong><p>${esc(result.explanation_vi)}</p>${evidenceButton(result.paragraph_index,result.evidence)}</div>`:''}</fieldset>`;
    }).join('')+
    `<div class="button-row">${res?'<button class="btn secondary" data-action="reset-reading-quiz">Làm lại bộ câu hỏi</button>':'<button class="btn primary" data-action="submit-reading-quiz">Kiểm tra câu trả lời</button>'}<button class="btn" data-action="reader-tab" data-tab="text">Quay lại bài đọc</button></div>`));
}
function qaResultCard(item){
  const a=item.result;
  return `<article class="qa-answer panel"><div class="tags"><span class="chip">${item.origin==='ai'?'AI':'Kết quả nhập'} · chưa xác minh nội dung</span>${a.cannot_answer?'<span class="chip warm">Chưa đủ cơ sở trả lời</span>':''}</div><h3>${esc(item.question)}</h3><p class="qa-response">${esc(a.answer_vi)}</p>${a.language_notes?.map(n=>`<div class="language-note"><b>${esc(n.point)}</b><p>${esc(n.explanation_vi)}</p></div>`).join('')||''}${a.evidence?.map(e=>evidenceButton(e.paragraph_index,e.quote)).join('')||''}${a.limitation_vi?`<div class="notice">${esc(a.limitation_vi)}</div>`:''}</article>`;
}
function renderReadingHelp(box,r){
  const faqs=r.lesson?.faqs||[];
  box.replaceChildren(window.LexiDOM.fragment(`${faqs.length?`<section class="faq-section"><h2>Giải đáp có sẵn</h2><p class="fineprint">Những điểm đáng chú ý trong bài.</p>${faqs.map(f=>`<details class="faq-item"><summary>${esc(f.question)}</summary><div><p>${esc(f.answer_vi)}</p>${evidenceButton(f.paragraph_index,f.evidence)}</div></details>`).join('')}</section>`:''}
  <details class="qa-composer panel" ${state.boot.ai_enabled?'open':''}><summary>Hỏi thêm về bài đọc</summary><h2>Chỗ nào khiến bạn chưa hiểu?</h2><p>Hỏi về nghĩa theo ngữ cảnh, cấu trúc câu, đại từ hoặc cách tác giả lập luận. Câu trả lời cần dựa trên bài đang mở.</p>${state.qaSelected?`<div class="selected-context"><span class="eyebrow">PHẦN BẠN ĐÃ CHỌN</span><blockquote class="quote">${esc(state.qaSelected)}</blockquote><button class="link-btn" data-action="clear-qa-selection">Bỏ phần chọn</button></div>`:''}<label for="reading-question-input">Câu hỏi của bạn</label><textarea id="reading-question-input" rows="3" maxlength="1500" placeholder="Ví dụ: Tại sao tác giả dùng ‘however’ trong câu này?">${esc(state.qaDraft||'')}</textarea><div class="quick-prompts">${['Tóm tắt ý chính của bài bằng tiếng Việt.','Giải thích một cấu trúc khó trong bài.','Chỉ ra một cặp paraphrase hữu ích trong bài.'].map(t=>`<button class="btn small" data-action="qa-preset" data-text="${esc(t)}">${esc(t)}</button>`).join('')}</div><div class="button-row">${state.boot.ai_enabled?'<button class="btn primary" data-action="ask-reading-ai">✦ Hỏi trợ lý</button>':''}<button class="btn secondary" data-action="ask-reading-prompt">Dùng trợ lý bên ngoài</button></div><p class="fineprint">${state.boot.ai_enabled?'Bạn sẽ được hỏi trước khi gửi bài và câu hỏi cho trợ lý.':'Bạn có thể sao chép câu hỏi sang trợ lý khác rồi nhập lời giải vào đây.'}</p></details>
  ${state.qaHistory?.length?'<h2>Các câu bạn đã hỏi</h2>':''}<div id="qa-history">${(state.qaHistory||[]).map(qaResultCard).join('')}</div>`));
}
function getQuestionPayload(){
  const question=$('#reading-question-input')?.value.trim()||state.qaDraft||'';
  if(!question.trim())throw new Error('Hãy nhập câu hỏi hoặc chọn một gợi ý.');
  state.qaDraft=question;
  return {reading_id:state.reading.id,question,selected_text:state.qaSelected||''};
}
function jumpToParagraph(index){
  state.readingTab='text';renderReader();
  const p=$('.parallel-row[data-paragraph="'+index+'"]');
  if(p){p.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'center'});p.classList.add('paragraph-focus');setTimeout(()=>p.classList.remove('paragraph-focus'),2000);}
}
async function platformAct(button){
  const action=button.dataset.action;
  switch(action){
    case 'toggle-navigation':{
      const open=$('.sidebar').classList.toggle('menu-open');button.setAttribute('aria-expanded',String(open));return true;
    }
    case 'catalog-prev':case 'catalog-next':{
      const track=state.libraryTrack||'general',key=track==='ielts'?'ieltsFilters':'catalogFilters';
      state[key].page=Math.max(1,(state[key].page||1)+(action==='catalog-next'?1:-1));await catalogPage(++state.routeEpoch,track);return true;
    }
    case 'choose-level':state.catalogFilters={q:'',level:window.LexiLibrary.saveLevel(button.dataset.level,'general'),topic:'',status:'',favorite:'all',page:1};location.hash='catalog';return true;
    case 'library-level':{
      const track=button.dataset.track||'general',key=track==='ielts'?'ieltsFilters':'catalogFilters';
      state[key]={...state[key],level:window.LexiLibrary.saveLevel(button.dataset.level,track),page:1};
      await catalogPage(++state.routeEpoch,track);$('#main .level-option[aria-pressed=true]')?.focus({preventScroll:true});return true;
    }
    case 'catalog-status':
    case 'catalog-filter':{
      const track=state.libraryTrack||'general',key=track==='ielts'?'ieltsFilters':'catalogFilters';
      state[key]={q:$('#catalog-search').value.trim(),level:window.LexiLibrary.saveLevel(state[key]?.level||'',track),topic:$('#catalog-topic').value,status:button.dataset.action==='catalog-status'?button.dataset.status:state[key]?.status||'',favorite:$('#catalog-favorite').value,kind:$('#catalog-kind')?.value||'',limit:12,page:1};
      await catalogPage(++state.routeEpoch,track);if(button.dataset.action==='catalog-status')$('#main .progress-tabs [aria-pressed=true]')?.focus({preventScroll:true});return true;
    }
    case 'bookmark-paragraph':await busy(button,async()=>{const r=await api('/readings/'+state.reading.id+'/progress/',{method:'POST',data:{paragraph:Number(button.dataset.index)}});state.reading.progress=r.progress;toast('Đã lưu vị trí đọc ở đoạn '+(Number(button.dataset.index)+1)+'.');renderReader();});return true;
    case 'jump-bookmark':jumpToParagraph(state.reading.progress?.paragraph||0);return true;
    case 'jump-paragraph':jumpToParagraph(Number(button.dataset.index));return true;
    case 'complete-reading':await busy(button,async()=>{const r=await api('/readings/'+state.reading.id+'/progress/',{method:'POST',data:{completed:!state.reading.progress?.completed}});state.reading.progress=r.progress;await refreshBoot();renderReader();});return true;
    case 'study-reading':state.study=null;state.readingSources=[...new Map([...(state.readingSources||[]),{id:state.reading.id,title:state.reading.title}].map(r=>[r.id,r])).values()];state.studySettings={...state.studySettings,tag:'',reading:state.reading.id,scope:'all',mode:'flashcard'};location.hash='study';return true;
    case 'ask-paragraph':state.qaSelected=state.reading.paragraphs[Number(button.dataset.index)];state.qaDraft='Giải thích ý nghĩa và cấu trúc đáng chú ý của đoạn đã chọn.';state.readingTab='help';renderReader();return true;
    case 'selected-question':if(state.selection){state.qaSelected=state.selection.word;state.qaDraft='Giải thích ý nghĩa và cấu trúc của phần đã chọn trong ngữ cảnh này.';state.readingTab='help';clearSelection();window.getSelection()?.removeAllRanges();renderReader();}return true;
    case 'clear-qa-selection':state.qaSelected='';renderReader();return true;
    case 'qa-preset':state.qaDraft=button.dataset.text;$('#reading-question-input').value=state.qaDraft;return true;
    case 'ask-reading-prompt':{
      const payload=getQuestionPayload();state.pendingQuestion=payload;
      await busy(button,async()=>{const res=await api('/prompts/',{method:'POST',data:{task:'question',...payload}});showPrompt(res.prompt,'question');});return true;
    }
    case 'ask-reading-ai':{
      const payload=getQuestionPayload();
      if(cloudConsent('Bài “'+state.reading.title+'”, câu hỏi và phần được chọn'))await busy(button,async()=>{
        const answer=await api('/readings/'+payload.reading_id+'/questions/',{method:'POST',data:{...payload,allow_cloud:true}});
        await refreshBoot();if(state.reading?.id===payload.reading_id){state.qaHistory=[answer,...state.qaHistory].slice(0,30);renderReader();toast('Đã lưu lời giải. Đối chiếu trích dẫn trước khi ghi nhớ.');}
      },'Đang giải thích…');return true;
    }
    case 'submit-reading-quiz':{
      const hw=state.homework;await busy(button,async()=>{const res=await api('/readings/'+state.reading.id+'/quiz/',{method:'POST',data:{token:hw.token,answers:hw.answers}});hw.result=res;state.reading.progress=res.progress;await refreshBoot();renderReader();});return true;
    }
    case 'reset-reading-quiz':state.homework={readingId:state.reading.id,answers:{},token:uid(),result:null};renderReader();return true;
  }
  return false;
}
document.addEventListener('change',e=>{
  if(e.target.dataset.lessonQuestion){state.homework.answers[e.target.dataset.lessonQuestion]=Number(e.target.value);}
  if(e.target.id==='reading-font'){state.readerFont=Number(e.target.value);renderReader();}
});
document.addEventListener('input',e=>{if(e.target.id==='reading-question-input')state.qaDraft=e.target.value;if(e.target.dataset.lessonText)state.homework.answers[e.target.dataset.lessonText]=e.target.value;});
document.addEventListener('keydown',e=>{if(e.target.id==='catalog-search'&&e.key==='Enter'){e.preventDefault();platformAct($('[data-action="catalog-filter"]')).catch(err=>toast(err.message,true));}});
