'use strict';
/* Bundled teaching material: search and self-review run locally. */
(()=>{
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fold=value=>String(value??'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replaceAll('đ','d');
  const labels={affirmative:'Khẳng định',negative:'Phủ định',question:'Câu hỏi'};
  const toolsHTML=()=>`<nav class="grammar-tools" aria-label="Tra cứu ngữ pháp"><a href="#learn/verbs"><span aria-hidden="true">Aa</span><div><strong>Động từ bất quy tắc</strong><small>Tra V1 · V2 · V3 và tự ôn</small></div><b aria-hidden="true">↗</b></a><a href="#learn/tenses"><span aria-hidden="true">↔</span><div><strong>Phân biệt các thì</strong><small>Cách dùng, cấu trúc và ví dụ</small></div><b aria-hidden="true">↗</b></a></nav>`;
  function tenseHTML(t){
    return `<article class="tense-guide"><header><span class="eyebrow">DÙNG ĐÚNG THEO NGỮ CẢNH</span><h2>${esc(t.title)}</h2></header><section><h3>Khi nào dùng?</h3><ul class="tense-uses">${t.uses.map(s=>`<li>${esc(s)}</li>`).join('')}</ul><blockquote class="tense-example"><p lang="en" data-no-i18n>${esc(t.example)}</p><p>${esc(t.translation_vi)}</p></blockquote></section><section><h3>Cách đặt câu</h3><p class="grammar-key">S = chủ ngữ · V = động từ nguyên mẫu · V2 = quá khứ · V3 = quá khứ phân từ</p><dl class="tense-forms">${Object.entries(t.forms).map(([key,value])=>`<div><dt>${labels[key]}</dt><dd data-no-i18n>${esc(value)}</dd></div>`).join('')}</dl><p class="tense-note">${esc(t.note)}</p>${t.id==='future-simple'?`<div class="tense-alternatives"><p><strong>Ý định / dự đoán có căn cứ:</strong> S + am/is/are going to + V.<br><span lang="en" data-no-i18n>Look at those clouds. It is going to rain.</span> — Nhìn mây kìa, trời sắp mưa rồi.</p><p><strong>Lịch hẹn đã thu xếp:</strong> S + am/is/are + V-ing.<br><span lang="en" data-no-i18n>I am meeting Lan at six.</span> — Tôi có hẹn gặp Lan lúc sáu giờ.</p></div>`:''}${/V[23]/.test(Object.values(t.forms).join(' '))?'<a class="link-btn" href="#learn/verbs">Tra dạng V2 và V3 →</a>':''}</section><section><h3>Dấu hiệu thường gặp</h3><dl class="tense-signals">${t.signals.map(s=>`<div><dt lang="en" data-no-i18n>${esc(s.word)}</dt><dd>${esc(s.meaning)}</dd></div>`).join('')}</dl><p class="grammar-key">Xem cả ý nghĩa và mốc thời gian của câu. Một từ như <span lang="en" data-no-i18n>for, since, when</span> có thể xuất hiện với nhiều thì.</p></section></article>`;
  }
  function comparisonHTML(c){
    return `<section class="tense-comparison"><h2>${esc(c.title)}</h2><div class="tense-pair">${c.sides.map(s=>`<article><h3>${esc(s.title)}</h3><p>${esc(s.use)}</p><blockquote><p lang="en" data-no-i18n>${esc(s.example)}</p><p>${esc(s.translation_vi)}</p></blockquote></article>`).join('')}</div><p class="tense-decision"><strong>Cách chọn:</strong> ${esc(c.tip)}</p></section>`;
  }
  function guideHTML(guide){return guide.tenses.map(tenseHTML).join('')+guide.comparisons.map(comparisonHTML).join('');}
  function group(row){
    const forms=[row.base,...row.past,...row.participle];
    if(new Set(forms).size===1)return 'same';
    if(row.past.join('/')===row.participle.join('/'))return 'past-same';
    return 'different';
  }
  function filterVerbs(rows,q='',pattern=''){
    const terms=fold(q).trim().split(/\s+/).filter(Boolean);
    return rows.filter(r=>(!pattern||group(r)===pattern)&&terms.every(t=>fold([r.base,...r.past,...r.participle,r.meaning_vi].join(' ')).includes(t)));
  }
  function verbsHTML(rows,hidden=false){
    const form=(values)=>hidden?'<span aria-label="Đang ẩn để tự ôn">•••</span>':`<span lang="en" data-no-i18n>${esc(values.join(' / '))}</span>`;
    return `<div class="verb-table-wrap"><table class="verb-table"><caption class="sr-only">Động từ bất quy tắc: nguyên mẫu, quá khứ, quá khứ phân từ và nghĩa</caption><thead><tr><th scope="col">V1 · Nguyên mẫu</th><th scope="col">V2 · Quá khứ</th><th scope="col">V3 · Phân từ</th><th scope="col">Nghĩa</th></tr></thead><tbody>${rows.map(r=>`<tr><th scope="row" data-label="V1"><span lang="en" data-no-i18n>${esc(r.base)}</span></th><td data-label="V2">${form(r.past)}</td><td data-label="V3">${form(r.participle)}</td><td class="verb-meaning" data-label="Nghĩa">${esc(r.meaning_vi)}${r.note?`<details><summary>Lưu ý</summary><p>${esc(r.note)}</p></details>`:''}</td></tr>`).join('')}</tbody></table></div>`;
  }
  async function page(area,section,active){
    const data=await api('/learn/grammar-reference/');if(!active())return;
    const back='<a class="link-btn" href="#learn/grammar">← Học ngữ pháp</a>';
    if(section==='verbs'){
      area.innerHTML=back+`<header class="academy-heading"><span class="eyebrow">TRA NHANH, NHỚ QUA VÍ DỤ</span><h1>Động từ bất quy tắc</h1><p>${data.verbs.length} động từ thường gặp. Tra bằng từ nguyên mẫu, dạng quá khứ hoặc nghĩa tiếng Việt.</p></header><div class="verb-how"><p><strong>V2</strong> dùng trong câu khẳng định quá khứ đơn: <span lang="en" data-no-i18n>I went home.</span></p><p><strong>V3</strong> dùng sau have/has/had trong các thì hoàn thành và sau be trong câu bị động: <span lang="en" data-no-i18n>I have gone home. The door was closed.</span></p><p>Học vài từ mỗi lần rồi đặt câu. Những dạng cách nhau bằng dấu / là các biến thể; mở Lưu ý nếu có để xem cách dùng.</p></div><div class="academy-filters"><label>Tìm động từ<input type="search" data-verb-search placeholder="Ví dụ: went, written, đọc…" autocomplete="off"></label><label>Nhóm biến đổi<select data-verb-group><option value="">Tất cả nhóm</option><option value="same">V1 = V2 = V3</option><option value="past-same">V2 = V3, khác V1</option><option value="different">Các dạng còn lại</option></select></label></div><div class="verb-controls"><p role="status" data-verb-count></p><button type="button" class="btn secondary small" data-verb-hide aria-pressed="false">Ẩn V2, V3 để tự ôn</button></div><div data-verbs></div><nav class="verb-pagination" aria-label="Trang bảng động từ"><button class="btn secondary small" type="button" data-verb-prev>← Trang trước</button><span data-verb-page></span><button class="btn secondary small" type="button" data-verb-next>Trang sau →</button></nav>`;
      let current=0,hidden=false;const size=24;
      const draw=()=>{
        const rows=filterVerbs(data.verbs,area.querySelector('[data-verb-search]').value,area.querySelector('[data-verb-group]').value),total=Math.max(1,Math.ceil(rows.length/size));
        current=Math.min(current,total-1);const start=current*size;
        area.querySelector('[data-verb-count]').textContent=rows.length?`${rows.length} động từ · Đang xem ${start+1}–${Math.min(start+size,rows.length)}`:'Không tìm thấy động từ. Thử từ khóa khác.';
        area.querySelector('[data-verbs]').innerHTML=rows.length?verbsHTML(rows.slice(start,start+size),hidden):'<p class="empty-state">Bạn có thể tìm bằng V1, V2, V3 hoặc nghĩa tiếng Việt.</p>';
        area.querySelector('[data-verb-page]').textContent=`${current+1} / ${total}`;
        area.querySelector('[data-verb-prev]').disabled=current===0;
        area.querySelector('[data-verb-next]').disabled=current===total-1;
        area.querySelector('.verb-pagination').hidden=rows.length<=size;
      };
      area.querySelector('[data-verb-search]').oninput=()=>{current=0;draw();};
      area.querySelector('[data-verb-group]').onchange=()=>{current=0;draw();};
      area.querySelector('[data-verb-hide]').onclick=ev=>{hidden=!hidden;ev.currentTarget.setAttribute('aria-pressed',String(hidden));ev.currentTarget.textContent=hidden?'Hiện V2, V3':'Ẩn V2, V3 để tự ôn';draw();};
      for(const [selector,step] of [['prev',-1],['next',1]])area.querySelector(`[data-verb-${selector}]`).onclick=()=>{current+=step;draw();area.querySelector('.verb-controls').scrollIntoView({block:'start'});};
      draw();
    }else{
      area.innerHTML=back+`<header class="academy-heading"><span class="eyebrow">NHÌN NGỮ CẢNH, CHỌN ĐÚNG THÌ</span><h1>Các thì trong tiếng Anh</h1><p>Tra 12 dạng thì thường học, rồi đối chiếu những cách dùng dễ nhầm.</p></header><label class="tense-picker">Bạn muốn xem thì nào?<select data-tense-select>${data.tenses.map(t=>`<option value="${esc(t.id)}">${esc(t.title)}</option>`).join('')}</select></label><div data-tense-content></div><div class="tense-compare-picker"><h2>Phân biệt các thì dễ nhầm</h2><label>Chọn cặp cần so sánh<select data-compare-select>${data.comparisons.map(c=>`<option value="${esc(c.id)}">${esc(c.title)}</option>`).join('')}</select></label></div><div data-compare-content></div>`;
      const drawTense=()=>{const t=data.tenses.find(t=>t.id===area.querySelector('[data-tense-select]').value);area.querySelector('[data-tense-content]').innerHTML=tenseHTML(t)+(t.lesson_id?`<a class="btn primary" href="#grammar/${encodeURIComponent(t.lesson_id)}">Học bài này và làm bài tập →</a>`:'');};
      const drawCompare=()=>{area.querySelector('[data-compare-content]').innerHTML=comparisonHTML(data.comparisons.find(c=>c.id===area.querySelector('[data-compare-select]').value));};
      area.querySelector('[data-tense-select]').onchange=drawTense;area.querySelector('[data-compare-select]').onchange=drawCompare;drawTense();drawCompare();
    }
    const credits=section==='verbs'
      ? [['https://learnenglish.britishcouncil.org/free-resources/grammar/english-grammar-reference/irregular-verbs','British Council'],['https://dictionary.cambridge.org/grammar/british-grammar/table-of-irregular-verbs','Cambridge Grammar']]
      : [['https://learnenglish.britishcouncil.org/free-resources/grammar/b1-b2/present-perfect-simple-continuous','Present perfect'],['https://learnenglish.britishcouncil.org/free-resources/grammar/b1-b2/future-continuous-future-perfect','Future forms']];
    area.insertAdjacentHTML('beforeend',`<p class="grammar-reference-credit">Nội dung do LexiRead biên soạn. Đối chiếu: ${credits.map(([url,title])=>`<a href="${url}" target="_blank" rel="noopener noreferrer">${title}</a>`).join(' · ')}.</p>`);
  }
  window.LexiGrammarReference={page,toolsHTML,tenseHTML,comparisonHTML,guideHTML,filterVerbs,verbsHTML};
})();
