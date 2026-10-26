'use strict';
/* Authored lessons and server-graded practice. No AI requests. */
(()=>{
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const levels=['A1','A2','B1','B2','C1','C2'];
  const groups={A1:'Bắt đầu với câu đơn',A2:'Nói về những việc quen thuộc',B1:'Diễn đạt rõ ý hơn',B2:'Dùng cấu trúc linh hoạt',C1:'Ngữ pháp nâng cao',C2:'Sắc thái và văn phong'};
  const preferences={level:'basic',q:'',status:''};
  const fold=value=>String(value??'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replaceAll('đ','d');
  function filterLessons(rows,selection){return rows.filter(r=>(!selection.status||(selection.status==='read'?r.is_read:!r.is_read))&&(!selection.level||(selection.level==='basic'?['A1','A2'].includes(r.level):r.level===selection.level))&&(!selection.q||fold(selection.q).trim().split(/\s+/).every(term=>fold(r.title+' '+r.description).includes(term))));}
  function cardsHTML(rows){
    return levels.map(level=>{
      const lessons=rows.filter(r=>r.level===level);if(!lessons.length)return '';
      return `<section class="grammar-course-group"><div class="section-title"><div><span class="level-pill">${level}</span><h2>${groups[level]}</h2></div><span class="muted">${lessons.length} bài học</span></div><div class="academy-grid">${lessons.map(r=>`<article class="academy-card grammar-course-card"><div class="tags"><span class="eyebrow">BÀI ${r.number}</span><span class="reading-status ${r.is_read?'completed':'new'}">${r.is_read?'✓ Đã đọc':'Chưa đọc'}</span></div><h3>${esc(r.title)}</h3><p>${esc(r.description)}</p><div class="academy-card-bottom"><small>${r.question_count} câu bài tập · ${r.minutes} phút</small><a class="btn secondary small" href="#grammar/${encodeURIComponent(r.id)}">${r.is_read||r.progress?'Ôn bài này':'Học bài này'} →</a></div></article>`).join('')}</div></section>`;
    }).join('');
  }
  async function catalogue(area,active){
    const data=await api('/learn/overview/?kind=grammar');if(!active())return;
    const counts={};const items=data.items.map(row=>({...row,number:counts[row.level]=(counts[row.level]||0)+1}));
    const basic=items.filter(r=>['A1','A2'].includes(r.level));
    const first=basic[0];
    area.innerHTML=`<header class="academy-heading"><h1>Học ngữ pháp từng bước</h1><p>Giải thích bằng tiếng Việt, cấu trúc rõ ràng và ví dụ gần gũi. Học xong, làm bài tập để kiểm tra và xem lời giải.</p></header>${first?`<section class="grammar-start"><div><span class="eyebrow">DÀNH CHO NGƯỜI MỚI BẮT ĐẦU</span><h2>Từ câu đầu tiên đến đoạn văn ngắn</h2><p>${basic.length} bài A1–A2, sắp xếp từ cách ghép câu đến các thì và cách nối ý.</p></div><a class="btn primary" href="#grammar/${encodeURIComponent(first.id)}">Bắt đầu từ bài 1 →</a></section>`:''}${window.LexiGrammarReference.toolsHTML()}<div class="progress-tabs" role="group" aria-label="Tiến độ ngữ pháp">${[['','Tất cả'],['unread','Chưa đọc'],['read','Đã đọc']].map(([v,l])=>`<button type="button" data-grammar-status="${v}" aria-pressed="${preferences.status===v}">${l}</button>`).join('')}</div><div class="academy-filters"><label>Chọn trình độ<select data-grammar-level><option value="basic" ${preferences.level==='basic'?'selected':''}>Cơ bản · A1–A2</option><option value="" ${!preferences.level?'selected':''}>Tất cả trình độ</option>${levels.map(l=>`<option value="${l}" ${preferences.level===l?'selected':''}>${l}</option>`).join('')}</select></label><label>Tìm bài học<input type="search" data-grammar-search value="${esc(preferences.q)}" placeholder="Ví dụ: câu đơn, hiện tại, giới từ…"></label></div><p role="status" data-grammar-count></p><div data-grammar-cards></div>`;
    const draw=()=>{const rows=filterLessons(items,preferences);area.querySelectorAll('[data-grammar-status]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.grammarStatus===preferences.status)));area.querySelector('[data-grammar-count]').textContent=`${rows.length} bài học · ${rows.reduce((s,r)=>s+r.question_count,0)} câu bài tập`;area.querySelector('[data-grammar-cards]').innerHTML=rows.length?cardsHTML(rows):'<p class="empty-state">Chưa tìm thấy bài phù hợp. Thử đổi từ khóa hoặc trình độ.</p>';};
    area.querySelectorAll('[data-grammar-status]').forEach(b=>b.onclick=()=>{preferences.status=b.dataset.grammarStatus;draw();});
    area.querySelector('[data-grammar-level]').onchange=ev=>{preferences.level=ev.target.value;draw();};
    area.querySelector('[data-grammar-search]').oninput=ev=>{preferences.q=ev.target.value;draw();};draw();
  }
  function navigationHTML(data){
    const link=(r,label)=>r?`<a href="#grammar/${encodeURIComponent(r.id)}"><small><span>${label}</span> · ${esc(r.level)}</small><strong>${esc(r.title)}</strong></a>`:'';
    return `<nav class="grammar-next" aria-label="Bài ngữ pháp tiếp theo">${link(data.navigation?.previous,'← Bài trước')}${link(data.navigation?.next,'Bài tiếp theo →')}</nav>`;
  }
  function lessonHTML(data,references,quiz){
    const t=data.teaching;
    return `<div class="grammar-mode" role="group" aria-label="Chọn phần bài học"><button type="button" class="btn" data-grammar-mode="lesson" aria-pressed="true" aria-controls="grammar-lesson-panel">1. Bài học</button><button type="button" class="btn" data-grammar-mode="practice" aria-pressed="false" aria-controls="grammar-practice-panel">2. Bài tập (${data.questions.length} câu)</button></div><section id="grammar-lesson-panel" data-grammar-panel="lesson" tabindex="-1">${t?`<p class="grammar-objective"><strong>Sau bài này, bạn có thể:</strong> ${esc(t.objective)}</p>`:''}${data.tense_guide?window.LexiGrammarReference.guideHTML(data.tense_guide):`<div class="grammar-sections">${data.explanation.map((s,i)=>`<article class="grammar-explanation"><span class="eyebrow">PHẦN ${i+1}</span><h2>${esc(s.title)}</h2><p>${esc(s.body)}</p>${s.pattern?`<div class="grammar-formula"><small>Cấu trúc cần nhớ</small><p>${esc(s.pattern)}</p></div>`:''}<blockquote><p lang="en" data-no-i18n>${esc(s.example)}</p>${window.LexiPronunciation?.button(s.example,'sentence')||''}<p>${esc(s.translation_vi)}</p></blockquote></article>`).join('')}</div>`}${t?`<section class="grammar-walkthrough"><span class="eyebrow">CÙNG PHÂN TÍCH MỘT VÍ DỤ</span><h2>Áp dụng vào câu như thế nào?</h2><p>${esc(t.context)}</p><blockquote><strong lang="en" data-no-i18n>${esc(t.example)}</strong>${window.LexiPronunciation?.button(t.example,'sentence')||''}<p>${esc(t.translation_vi)}</p></blockquote><ol>${t.steps.map(s=>`<li>${esc(s)}</li>`).join('')}</ol><div class="grammar-quick-check"><h3>Thử tự làm</h3><p>${esc(t.quick_check.prompt)}</p><details><summary>Xem đáp án và cách làm</summary><p lang="en" data-no-i18n><strong>${esc(t.quick_check.answer)}</strong></p><p>${esc(t.quick_check.explanation_vi)}</p></details></div></section><section class="grammar-recap"><h2>Nhớ hai ý chính</h2><ul>${t.takeaways.map(s=>`<li>${esc(s)}</li>`).join('')}</ul></section>`:''}<details class="academy-guide"><summary>Những lỗi thường gặp</summary><ul>${(data.pitfalls||[]).map(s=>`<li>${esc(s)}</li>`).join('')}</ul></details><div class="grammar-practice-callout"><div><h2>Thử áp dụng ngay</h2><p>${data.questions.length} câu bài tập, có đáp án và lời giải sau khi nộp.</p></div><button class="btn primary" type="button" data-start-grammar-practice>Làm bài tập →</button></div><div class="grammar-read-control"><button type="button" class="btn secondary" data-grammar-read="${esc(data.id)}" aria-pressed="${!!data.is_read}">${data.is_read?'✓ Đã đọc · Bỏ đánh dấu':'Đánh dấu đã đọc'}</button><span role="status" data-grammar-read-note></span></div>${references}</section><section id="grammar-practice-panel" data-grammar-panel="practice" tabindex="-1" hidden><p class="grammar-practice-help">Chọn một đáp án cho mỗi câu. Bạn có thể quay lại phần Bài học mà vẫn giữ các lựa chọn.</p><div data-quiz>${quiz}</div></section>${navigationHTML(data)}`;
  }
  function attachLesson(area){
    const readButton=area.querySelector('[data-grammar-read]');
    if(readButton)readButton.onclick=async()=>{
      if(readButton.disabled)return;
      readButton.disabled=true;const note=area.querySelector('[data-grammar-read-note]');note.textContent='';
      try{
        const result=await api('/learn/grammar/'+encodeURIComponent(readButton.dataset.grammarRead)+'/read/',{method:'POST',data:{is_read:readButton.getAttribute('aria-pressed')!=='true'}});
        readButton.setAttribute('aria-pressed',String(result.is_read));
        readButton.textContent=result.is_read?'✓ Đã đọc · Bỏ đánh dấu':'Đánh dấu đã đọc';
        note.textContent=result.is_read?'Đã lưu vào tài khoản của bạn.':'Đã chuyển về chưa đọc.';
      }catch(error){note.textContent=error.message||'Chưa lưu được. Bạn thử lại nhé.';}finally{readButton.disabled=false;}
    };
    const buttons=area.querySelectorAll('[data-grammar-mode]');
    const show=mode=>{buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.grammarMode===mode)));area.querySelectorAll('[data-grammar-panel]').forEach(p=>p.hidden=p.dataset.grammarPanel!==mode);const panel=area.querySelector(`[data-grammar-panel="${mode}"]`);panel.focus({preventScroll:true});area.querySelector('.grammar-mode').scrollIntoView({behavior:'smooth',block:'start'});};
    buttons.forEach(b=>b.onclick=()=>show(b.dataset.grammarMode));
    area.querySelector('[data-start-grammar-practice]').onclick=()=>show('practice');
  }
  window.LexiGrammar={catalogue,filterLessons,cardsHTML,lessonHTML,attachLesson};
})();
