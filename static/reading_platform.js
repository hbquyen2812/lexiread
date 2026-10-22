'use strict';
/* Shared UI for the curated library and private reader. Loaded before app.js.
   It never calls a model directly or embeds an API key. All content is escaped. */
const readingKinds={main_idea:'Ý chính',detail:'Chi tiết',tfng:'TRUE / FALSE / NOT GIVEN',vocabulary:'Từ trong ngữ cảnh',inference:'Suy luận'};
function lessonStatus(r){return r.status==='completed'?'Đã đọc':r.status==='started'?'Đang đọc':'Chưa đọc';}
function lessonCard(r){
  const symbols={A2:'01',B1:'02',B2:'03'};
  return `<article class="lesson-card" data-level="${esc(r.level)}"><div class="lesson-card-top"><span class="level-pill ${esc(r.level.toLowerCase())}">${esc(r.level)} <small>ước lượng</small></span><span class="muted">${r.favorite?'★ Yêu thích · ':''}${lessonStatus(r)}</span></div><div class="lesson-cover"><span>${symbols[r.level]||'↗'}</span><div>${esc(r.topic)}</div></div><h3>${esc(r.title)}</h3><p class="lesson-summary">${esc(r.summary)}</p><div class="lesson-meta">${r.word_count} từ <span>·</span> ${r.vocabulary_count} mục từ <span>·</span> ${r.question_count} câu hỏi</div><div class="card-footer"><span class="fineprint">${r.progress?.quiz_total?`Điểm tốt nhất ${r.progress.quiz_best}/${r.progress.quiz_total}`:'Bản dịch & giải thích có sẵn'}</span><a class="btn small secondary" href="#lesson/${esc(r.slug)}">${r.reading_id?'Đọc tiếp':'Bắt đầu'} →</a></div></article>`;
}
async function readingHome(epoch){
  const [c,r]=await Promise.all([api('/catalog/'),api('/readings/')]);if(epoch!==state.routeEpoch)return;
  const s=state.boot.stats,featured=['A2','B1','B2'].map(l=>c.items.find(x=>x.level===l)).filter(Boolean);
  $('#main').innerHTML=`<section class="hero reading-hero"><div><span class="eyebrow">YOUR READING & VOCABULARY STUDIO</span><h1>Luyện đọc.<br>Hiểu từng ý.<br><em>Giữ lại vốn từ.</em></h1><p>Bài đọc ngắn, chủ đề mới, một chút mỗi ngày.<br>Chọn bài có sẵn hoặc mang bài của riêng bạn vào.</p><div class="button-row"><a class="btn primary" href="#catalog">Khám phá bài đọc →</a><button class="btn ghost" data-action="new-reading">+ Nhập bài của tôi</button></div></div><div class="hero-card-wrap" aria-hidden="true"><div class="hero-card-back"></div><div class="hero-card"><small>READ → UNDERSTAND → REMEMBER</small><div class="hero-word">A little<br>every day.</div><p>Không chỉ sưu tầm từ.<br>Học từ ngay trong câu chuyện.</p><span class="chip">A2 → B1 → B2</span></div></div></section>
  <section class="stats">${[[c.items.length,'Bài soạn sẵn','12 chủ đề để bắt đầu'],[s.completed_readings||0,'Bài đã đọc','Bạn chủ động đánh dấu hoàn thành'],[s.total,'Thẻ trong kho riêng','Chỉ thêm từ khi bạn chọn lưu'],[s.due??s.overdue,'Từ đang chờ ôn','Ưu tiên những từ đến hạn'],[s.active_days_30||0,'Ngày học / 30 ngày','Duy trì nhịp học đều đặn'],[s.page_views_today||0,'Hoạt động hôm nay','Lượt mở các khu học trong ngày'],[s.toeic_attempts||0,'Lượt TOEIC','Điểm tốt nhất '+(s.toeic_best??'—')+'/12']].map(([n,l,h])=>`<div class="stat"><div class="stat-top">${l}</div><div class="stat-value">${count(n)}</div><div class="stat-note">${h}</div></div>`).join('')}</section>
  ${dailyReviewCallout(s)}
  <div class="section-title"><div><h2>Chọn một điểm bắt đầu</h2><p class="fineprint">Bài luyện do LexiRead biên soạn. Mức độ là ước lượng, không phải đề hay thang điểm IELTS chính thức.</p></div><a class="link-btn" href="#catalog">Xem thư viện →</a></div><div class="lesson-grid">${featured.map(lessonCard).join('')}</div>
  <div class="two-paths"><section class="panel"><span class="eyebrow">BÀI ĐỌC CỦA TÔI</span><h2>Mang bài bạn đang học vào.</h2><p>Dán passage hoặc nhập file. Chọn một từ, hỏi về câu khó, rồi giữ lại những nghĩa cần ôn.</p><div class="button-row"><button class="btn secondary" data-action="new-reading">+ Nhập bài</button><a href="#readings" class="link-btn">${count(r.total??r.items.length)} bài đã nhập →</a></div></section><section class="panel"><span class="eyebrow">KHO TỪ CÁ NHÂN</span><h2>Học một lần, gặp lại đúng lúc.</h2><p>Từ trong thư viện và từ từ bài tự nhập cùng vào một kho. Ôn nghĩa, synonym và paraphrase, không cần chép lại thẻ.</p><a href="#study" class="btn primary">Ôn từ hôm nay ↗</a></section></div>`;
}
async function catalogPage(epoch){
  state.catalogFilters ||= {q:'',level:'',topic:'',status:'',favorite:'all'};const f=state.catalogFilters;
  const c=await api('/catalog/?'+new URLSearchParams(f));if(epoch!==state.routeEpoch)return;
  state.catalogItems=c.items;
  $('#main').innerHTML=heading('Thư viện luyện đọc','Bài soạn sẵn theo chủ đề và mức độ. Mở bài là học được, không cần gọi AI.')+
    `<div class="catalog-note"><b>Đọc để hiểu, không cần dịch từng chữ.</b><span>Thử đọc tiếng Anh trước, làm câu hỏi, rồi mở bản dịch và lưu từ bạn muốn học.</span></div><div class="catalog-filters"><input id="catalog-search" type="search" placeholder="Tìm tiêu đề hoặc chủ đề…" aria-label="Tìm bài đọc" value="${esc(f.q)}"><select id="catalog-level" aria-label="Trình độ"><option value="">Mọi trình độ</option>${['A2','B1','B2'].map(l=>`<option ${l===f.level?'selected':''}>${l}</option>`).join('')}</select><select id="catalog-topic" aria-label="Chủ đề"><option value="">Mọi chủ đề</option>${c.topics.map(t=>`<option ${f.topic===t?'selected':''}>${esc(t)}</option>`).join('')}</select><select id="catalog-status" aria-label="Tiến độ đọc"><option value="">Mọi trạng thái</option>${[['new','Chưa đọc'],['started','Đang đọc'],['completed','Đã đọc']].map(([k,l])=>`<option value="${k}" ${f.status===k?'selected':''}>${l}</option>`).join('')}</select><select id="catalog-favorite" aria-label="Bài yêu thích">${[['all','Tất cả bài'],['yes','Chỉ yêu thích'],['no','Chưa yêu thích']].map(([v,l])=>`<option value="${v}" ${f.favorite===v?'selected':''}>${l}</option>`).join('')}</select><button class="btn secondary" data-action="catalog-filter">Lọc</button></div><div class="section-title"><h2>${c.items.length} bài phù hợp</h2><span class="fineprint">A2–B2: mức độ do người biên soạn ước lượng</span></div>`+
    (c.items.length?`<div class="lesson-grid">${c.items.map(lessonCard).join('')}</div>`:empty('Chưa có bài phù hợp','Thử chủ đề hoặc mức độ khác.'));
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
  if(!questions.length){box.innerHTML=empty('Bài này chưa có câu hỏi cố định','Các bài trong thư viện có sẵn bài tập hiểu bài. Bài tự nhập tập trung vào đọc và hỏi đáp.');return;}
  const hw=state.homework,res=hw.result;
  box.innerHTML=`<div class="section-title"><div><h2>Hiểu bài trước, đối chiếu sau.</h2><p class="fineprint">${questions.length} câu hỏi soạn sẵn. Chấm xong sẽ hiện giải thích và bằng chứng; không quy đổi thành band IELTS.</p></div></div>`+
    (res?`<div class="reading-score" role="status"><strong>${res.score} / ${res.total}</strong><div>Câu trả lời đúng<p>Đối chiếu câu gốc để hiểu cả câu đúng lẫn câu sai.</p></div></div>`:'')+
    questions.map((q,i)=>{const result=res?.results.find(x=>x.question_id===q.id);return `<fieldset class="reading-question"><legend><span class="chip">${i+1} · ${readingKinds[q.kind]||'Reading'}</span><span>${esc(q.prompt)}</span></legend><div class="reading-options">${q.options.map((o,j)=>`<label class="reading-option ${result?(j===result.answer?'is-correct':j===result.submitted?'is-wrong':''):''}"><input type="radio" data-lesson-question="${esc(q.id)}" name="lesson-${esc(q.id)}" value="${j}" ${hw.answers[q.id]===j?'checked':''} ${res?'disabled':''}><span class="choice-letter">${'ABCD'[j]}</span><span>${esc(o)}</span></label>`).join('')}</div>${result?`<div class="feedback ${result.correct?'':'wrong'}"><strong>${result.correct?'✓ Đúng':'Chưa đúng'} · ${esc(q.options[result.answer])}</strong><p>${esc(result.explanation_vi)}</p>${evidenceButton(result.paragraph_index,result.evidence)}</div>`:''}</fieldset>`;}).join('')+
    `<div class="button-row">${res?'<button class="btn secondary" data-action="reset-reading-quiz">Làm lại bộ câu hỏi</button>':'<button class="btn primary" data-action="submit-reading-quiz">Kiểm tra câu trả lời</button>'}<button class="btn" data-action="reader-tab" data-tab="text">Quay lại bài đọc</button></div>`;
}
function qaResultCard(item){
  const a=item.result;
  return `<article class="qa-answer panel"><div class="tags"><span class="chip">${item.origin==='ai'?'AI':'Kết quả nhập'} · chưa xác minh nội dung</span>${a.cannot_answer?'<span class="chip warm">Chưa đủ cơ sở trả lời</span>':''}</div><h3>${esc(item.question)}</h3><p class="qa-response">${esc(a.answer_vi)}</p>${a.language_notes?.map(n=>`<div class="language-note"><b>${esc(n.point)}</b><p>${esc(n.explanation_vi)}</p></div>`).join('')||''}${a.evidence?.map(e=>evidenceButton(e.paragraph_index,e.quote)).join('')||''}${a.limitation_vi?`<div class="notice">${esc(a.limitation_vi)}</div>`:''}</article>`;
}
function renderReadingHelp(box,r){
  const faqs=r.lesson?.faqs||[];
  box.innerHTML=`${faqs.length?`<section class="faq-section"><h2>Giải đáp có sẵn</h2><p class="fineprint">Được biên soạn cùng bài đọc, dùng được không cần API.</p>${faqs.map(f=>`<details class="faq-item"><summary>${esc(f.question)}</summary><div><p>${esc(f.answer_vi)}</p>${evidenceButton(f.paragraph_index,f.evidence)}</div></details>`).join('')}</section>`:''}
  <section class="qa-composer panel"><h2>Chỗ nào khiến bạn chưa hiểu?</h2><p>Hỏi về nghĩa theo ngữ cảnh, cấu trúc câu, đại từ hoặc cách tác giả lập luận. Câu trả lời cần dựa trên bài đang mở.</p>${state.qaSelected?`<div class="selected-context"><span class="eyebrow">PHẦN BẠN ĐÃ CHỌN</span><blockquote class="quote">${esc(state.qaSelected)}</blockquote><button class="link-btn" data-action="clear-qa-selection">Bỏ phần chọn</button></div>`:''}<label for="reading-question-input">Câu hỏi của bạn</label><textarea id="reading-question-input" rows="3" maxlength="1500" placeholder="Ví dụ: Tại sao tác giả dùng ‘however’ trong câu này?">${esc(state.qaDraft||'')}</textarea><div class="quick-prompts">${['Tóm tắt ý chính của bài bằng tiếng Việt.','Giải thích một cấu trúc khó trong bài.','Chỉ ra một cặp paraphrase hữu ích trong bài.'].map(t=>`<button class="btn small" data-action="qa-preset" data-text="${esc(t)}">${esc(t)}</button>`).join('')}</div><div class="button-row"><button class="btn primary" data-action="ask-reading-ai">✦ Hỏi AI</button><button class="btn secondary" data-action="ask-reading-prompt">Copy prompt / Dán JSON</button></div><p class="fineprint">${state.boot.ai_enabled?'API chỉ chạy sau khi bạn đồng ý gửi bài và câu hỏi.':'Chưa bật API: dùng giải đáp có sẵn hoặc copy prompt → hỏi AI bên ngoài → dán JSON vào đây.'} Trích dẫn đúng không tự bảo đảm lời giải đúng.</p></section>
  <div class="section-title"><h2>Các câu đã hỏi trong bài này</h2><span class="fineprint">Hiện tối đa 30 câu gần nhất</span></div><div id="qa-history">${(state.qaHistory||[]).length?state.qaHistory.map(qaResultCard).join(''):empty('Chưa có câu hỏi riêng','Câu trả lời bạn lưu sẽ xuất hiện tại đây, gắn với bài đọc này.')}</div>`;
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
    case 'catalog-filter':state.catalogFilters={q:$('#catalog-search').value.trim(),level:$('#catalog-level').value,topic:$('#catalog-topic').value,status:$('#catalog-status').value,favorite:$('#catalog-favorite').value};await catalogPage(++state.routeEpoch);return true;
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
      const hw=state.homework;await busy(button,async()=>{const res=await api('/readings/'+state.reading.id+'/quiz/',{method:'POST',data:{token:hw.token,answers:hw.answers}});hw.result=res;state.reading.progress=res.progress;renderReader();});return true;
    }
    case 'reset-reading-quiz':state.homework={readingId:state.reading.id,answers:{},token:uid(),result:null};renderReader();return true;
  }
  return false;
}
document.addEventListener('change',e=>{
  if(e.target.dataset.lessonQuestion){state.homework.answers[e.target.dataset.lessonQuestion]=Number(e.target.value);}
  if(e.target.id==='reading-font'){state.readerFont=Number(e.target.value);renderReader();}
});
document.addEventListener('input',e=>{if(e.target.id==='reading-question-input')state.qaDraft=e.target.value;});
document.addEventListener('keydown',e=>{if(e.target.id==='catalog-search'&&e.key==='Enter'){e.preventDefault();platformAct($('[data-action="catalog-filter"]')).catch(err=>toast(err.message,true));}});
