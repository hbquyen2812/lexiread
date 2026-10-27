'use strict';
/* Study aids for original TOEIC practice; the server remains the scoring authority. */
let practiceClockInterval=null;
function practiceClockRunning(session){return Number.isFinite(session?.clockStartedAt)&&session.clockStartedAt>=0;}
function practiceElapsed(session){const elapsed=Number.isFinite(session?.elapsedMs)&&session.elapsedMs>=0?session.elapsedMs:0;return elapsed+(practiceClockRunning(session)?Math.max(0,Date.now()-session.clockStartedAt):0);}
function hasPracticeAnswer(session,question){const answer=session?.answers?.[question.id];return Number.isInteger(answer)&&answer>=0&&answer<question.options.length;}
function normalizePracticeFlags(session){if(!Array.isArray(session.flags))session.flags=[];else session.flags=[...new Set(session.flags.filter(id=>typeof id==='string'))];}
function pausePracticeClock(){
  clearInterval(practiceClockInterval);practiceClockInterval=null;
  const session=state.toeicSession;
  if(practiceClockRunning(session)){session.elapsedMs=practiceElapsed(session);session.clockStartedAt=null;}
}
function updatePracticeProgress(){
  const session=state.toeicSession,practice=state.toeicSet;
  if(!session||!practice||!document.querySelector('[data-practice-progress]'))return;
  normalizePracticeFlags(session);
  const answered=practice.questions.filter(q=>hasPracticeAnswer(session,q)).length;
  const count=document.querySelector('[data-practice-count]');if(count)count.textContent=answered+' / '+practice.questions.length+' câu đã trả lời';
  document.querySelectorAll('[data-practice-jump]').forEach(button=>{const id=button.dataset.practiceJump,question=practice.questions.find(q=>q.id===id),has=question?hasPracticeAnswer(session,question):false;button.classList.toggle('is-answered',has);button.classList.toggle('is-flagged',session.flags.includes(id));button.setAttribute('aria-label','Câu '+button.textContent.replace('★','')+(has?' · đã trả lời':' · chưa trả lời')+(session.flags.includes(id)?' · đánh dấu xem lại':''));});
  const total=Math.floor(practiceElapsed(session)/1000),clock=document.querySelector('[data-practice-clock]');
  if(clock)clock.textContent=String(Math.floor(total/60)).padStart(2,'0')+':'+String(total%60).padStart(2,'0');
  const toggle=document.querySelector('[data-practice-pause]');if(toggle)toggle.textContent=practiceClockRunning(session)?'Tạm dừng đồng hồ':'Tiếp tục đồng hồ';
}
function renderToeicPractice(){
  window.LexiReadAloud?.clear();
  const practice=state.toeicSet,session=state.toeicSession,result=session.result;
  if(!Object.hasOwn(session,'clockStartedAt'))session.clockStartedAt=Date.now();
  if(result)pausePracticeClock();
  normalizePracticeFlags(session);
  const resultMap=new Map((result?.results||[]).map(row=>[row.question_id,row]));
  const question=(q,index)=>{const row=resultMap.get(q.id);return `<fieldset class="reading-question" id="practice-question-${esc(q.id)}" tabindex="-1" data-practice-correct="${row?String(row.correct):''}"><legend class="question-legend"><span>Câu ${index+1}: </span><span lang="en" data-no-i18n>${esc(q.prompt)}</span></legend><div class="reading-question-heading" aria-hidden="true"><span class="chip">${index+1} · Part ${q.part}</span><p lang="en" data-no-i18n>${esc(q.prompt)}</p></div><div class="reading-options" lang="en" data-no-i18n>${q.options.map((option,i)=>`<label class="reading-option ${row?(i===row.answer?'is-correct':i===row.submitted?'is-wrong':''):''}"><input type="radio" data-toeic-question="${esc(q.id)}" name="toeic-${esc(q.id)}" value="${i}" ${session.answers[q.id]===i?'checked':''} ${result?'disabled':''}><span class="choice-letter">${'ABCD'[i]}</span><span>${esc(option)}</span></label>`).join('')}</div>${row?`<div class="feedback ${row.correct?'':'wrong'}"><strong><span>${row.correct?'✓ Đúng':'Chưa đúng'}</span> · <span lang="en" data-no-i18n>${esc(q.options[row.answer])}</span></strong><p>${esc(row.explanation_vi)}</p>${row.evidence?`<blockquote class="quote" lang="en">${esc(row.evidence)}</blockquote>`:''}</div>`:`<button type="button" class="link-btn practice-flag" data-practice-flag="${esc(q.id)}" aria-pressed="${session.flags.includes(q.id)}">${session.flags.includes(q.id)?'★ Đã đánh dấu':'☆ Đánh dấu xem lại'}</button>`}</fieldset>`;};
  const documents=docs=>docs.length?`<div class="toeic-documents">${docs.map(doc=>`<article class="toeic-document" id="toeic-doc-${esc(doc.id)}" lang="en" data-no-i18n><span class="chip">${esc(doc.kind)}</span><h2>${esc(doc.heading)}</h2><div>${esc(doc.body)}</div></article>`).join('')}</div>`:'';
  let body='';
  if(practice.parts.includes(6)||practice.parts.includes(7)){
    const groups=new Map();practice.questions.forEach((q,i)=>{const key=(q.document_ids||[]).join('|');if(!groups.has(key))groups.set(key,[]);groups.get(key).push({q,i});});
    body=[...groups].map(([key,rows])=>`<section class="toeic-cluster">${documents(practice.documents.filter(d=>key.split('|').includes(d.id)))}<div class="toeic-questions">${rows.map(({q,i})=>question(q,i)).join('')}</div></section>`).join('');
  }else body=documents(practice.documents.filter(doc=>!practice.questions.some(q=>q.prompt.trim()===doc.body.trim())))+`<div class="toeic-questions">${practice.questions.map(question).join('')}</div>`;
  $('#main').innerHTML=`<a class="link-btn" href="#toeic">← Thư viện TOEIC Reading</a><div style="height:17px"></div>`+heading(practice.title,`${practice.mode_label} · ${String(practice.level||'').split('·')[0].trim()} · ${practice.question_count} câu · mục tiêu ${practice.duration_minutes} phút`)+`<p class="practice-instructions">${esc(practice.instructions)}</p><details class="lesson-about"><summary>Về bài luyện này</summary><p>${esc(practice.provenance||'Bài luyện do LexiRead biên soạn, không phải đề ETS.')}</p></details>`+
    (result?`<div class="reading-score toeic-score" role="status"><strong>${result.score} / ${result.total}</strong><div>${result.percentage}% chính xác<p>${Object.entries(result.by_part).map(([part,row])=>`Part ${part}: ${row.score}/${row.total}`).join(' · ')}. Đã lưu kết quả.</p></div><button class="btn secondary" data-action="reset-toeic">Làm lại</button></div><div class="practice-filter-results"><label><input type="checkbox" data-practice-wrong> Chỉ xem câu sai</label><a class="btn small" href="#guides/toeic">Ôn cách làm từng dạng →</a></div>`:`<section class="practice-progress" data-practice-progress><div class="practice-progress-top"><strong data-practice-count></strong><span>Đã làm <b class="practice-clock" data-practice-clock>00:00</b> / ${practice.duration_minutes} phút gợi ý</span><div class="button-row"><button type="button" class="btn small" data-practice-pause>Tạm dừng đồng hồ</button><button type="button" class="btn small secondary" data-practice-unanswered>Câu chưa trả lời →</button></div></div><p>Không tự nộp khi hết giờ. Chuyển trang vẫn giữ đáp án; tải lại trang sẽ làm lại.</p><details><summary>Chọn câu hỏi</summary><div class="question-map">${practice.questions.map((q,i)=>`<button type="button" data-practice-jump="${esc(q.id)}">${i+1}</button>`).join('')}</div></details></section>`)+body+`<div class="button-row toeic-submit">${result?'<button class="btn primary" data-action="reset-toeic">Làm lại bộ này</button><a class="btn" href="#toeic">Chọn bài khác</a>':'<button class="btn primary" data-action="submit-toeic">Nộp và xem giải thích</button>'}</div>`+
    (practice.focus_vocabulary.length?`<details class="panel source-context"><summary>Từ vựng trong bài</summary><div class="glossary-grid">${practice.focus_vocabulary.map(w=>`<article class="candidate-body"><div class="pronunciation-heading"><h3 lang="en">${esc(w.word)} <small>${esc(w.pos)}</small></h3>${window.LexiPronunciation?.button(w.word)||''}</div><p>${esc(w.meaning_vi)}</p>${lexicalDetails(w)}${lexicalContext(w)}</article>`).join('')}</div><button class="btn secondary" data-action="save-toeic-words">Lưu ${practice.focus_vocabulary.length} từ vào kho để ôn</button></details>`:'');
  const documentNodes=[...document.querySelectorAll('.toeic-document')];
  if(documentNodes.length){
    const audioHost=document.createElement('div');
    documentNodes[0].closest('.toeic-cluster,.toeic-documents').before(audioHost);
    const seen=new Set();
    window.LexiReadAloud?.mount(audioHost,documentNodes.filter(node=>{if(seen.has(node.id))return false;seen.add(node.id);return true;}).map(node=>({node,text:[node.querySelector('h2')?.textContent,node.querySelector('div')?.textContent].filter(Boolean).join('. ')})));
  }
  clearInterval(practiceClockInterval);if(!result)practiceClockInterval=setInterval(updatePracticeProgress,1000);updatePracticeProgress();
}
function jumpPracticeQuestion(id){const field=document.getElementById('practice-question-'+id);if(field){field.scrollIntoView({behavior:'instant',block:'start'});field.focus({preventScroll:true});}}
document.addEventListener('click',e=>{
  if(e.target.closest('[data-practice-pause]')){const s=state.toeicSession;if(!s)return;if(practiceClockRunning(s)){s.elapsedMs=practiceElapsed(s);s.clockStartedAt=null;}else s.clockStartedAt=Date.now();updatePracticeProgress();}
  const flag=e.target.closest('[data-practice-flag]');if(flag){const s=state.toeicSession;if(!s)return;const id=flag.dataset.practiceFlag;normalizePracticeFlags(s);s.flags=s.flags.includes(id)?s.flags.filter(x=>x!==id):[...s.flags,id];flag.setAttribute('aria-pressed',String(s.flags.includes(id)));flag.textContent=s.flags.includes(id)?'★ Đã đánh dấu':'☆ Đánh dấu xem lại';updatePracticeProgress();}
  const jump=e.target.closest('[data-practice-jump]');if(jump)jumpPracticeQuestion(jump.dataset.practiceJump);
  if(e.target.closest('[data-practice-unanswered]')){const q=state.toeicSet.questions.find(q=>!hasPracticeAnswer(state.toeicSession,q));if(q)jumpPracticeQuestion(q.id);else toast('Bạn đã trả lời đủ các câu. Có thể nộp và xem giải thích.');}
});
document.addEventListener('change',e=>{
  if(e.target.matches('[data-toeic-question]'))queueMicrotask(updatePracticeProgress);
  if(e.target.matches('[data-practice-wrong]'))document.querySelectorAll('[data-practice-correct]').forEach(q=>{q.hidden=e.target.checked&&q.dataset.practiceCorrect==='true';});
});
