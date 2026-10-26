'use strict';
/* LexiRead: framework-free UI. All untrusted text is escaped before HTML rendering.
   The optional offline preview adapter is never loaded by the Django application. */
const $ = (s, root=document) => root.querySelector(s);
const $$ = (s, root=document) => [...root.querySelectorAll(s)];
const esc = value => String(value ?? '').replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const uid = () => crypto.randomUUID ? crypto.randomUUID() : '10000000-1000-4000-8000-100000000000'.replace(/[018]/g,c=>(c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c/4).toString(16));
const state = {boot:null,readings:[],reading:null,readingTab:'text',translation:true,selection:null,
  readingFilters:{q:'',status:'all',favorite:'all',sort:'updated',page:1},readingSources:[],
  vocab:[],filters:{q:'',tag:'',scope:'all',reading:'',sort:'newest',page:1},editId:null,editing:null,bulk:[],study:null,
  studySettings:{mode:'flashcard',scope:'due',tag:'',reading:'',limit:'20'},toeicSet:null,toeicSession:null,
  analyticsDays:30,lastTracked:null,routeEpoch:0};
const asList = value => Array.isArray(value) ? value.map(String) : typeof value==='string' ? value.split('|').map(s=>s.trim()).filter(Boolean) : [];
const modes = {flashcard:'Flashcard · Lật thẻ',meaning:'ABCD · Anh → Việt',reverse:'ABCD · Việt → Anh',
  synonym:'Chọn từ gần nghĩa',paraphrase:'Chọn cách diễn đạt tương đương',cloze:'Điền từ trong câu',typing:'Gõ từ tiếng Anh'};
function toast(message, bad=false){
  const d=document.createElement('div');d.className='toast'+(bad?' error':'');d.textContent=message;
  $('#toasts').appendChild(d);setTimeout(()=>d.remove(),bad?9000:4500);
}
async function api(path,{method='GET',data=null}={}){
  if(window.LEXIREAD_PREVIEW) return window.LEXIREAD_PREVIEW.api(path,{method,data});
  const headers={};let body;
  if(data instanceof FormData) body=data;
  else if(data!==null){headers['Content-Type']='application/json';body=JSON.stringify(data);}
  if(method!=='GET'){
    const c=document.cookie.split('; ').find(x=>x.startsWith('csrftoken='));
    headers['X-CSRFToken']=c?decodeURIComponent(c.split('=').slice(1).join('=')):'';
  }
  let r;
  try{r=await fetch('/api'+path,{method,headers,body,credentials:'same-origin'});}
  catch(e){throw new Error('Chưa kết nối được. Bạn kiểm tra mạng rồi thử lại nhé.');}
  const json=(r.headers.get('content-type')||'').includes('application/json');
  const result=json?await r.json():await r.text();
  if(r.status===401){location.href='/login/';throw new Error('Phiên đăng nhập đã hết hạn.');}
  if(!r.ok)throw new Error(json?result.error:(r.status===403?'Phiên bảo mật đã hết hạn. Tải lại trang rồi thử lại.':'Chưa thực hiện được lúc này. Bạn thử lại sau nhé.'));
  return result;
}
async function busy(button,fn,label='Đang xử lý…'){
  const old=button?.innerHTML;
  if(button){button.disabled=true;button.textContent=label;}
  try{return await fn();}finally{if(button?.isConnected){button.disabled=false;button.innerHTML=old;}}
}
function tagOptions(selected=''){
  return '<option value="">Tất cả bộ từ</option>'+(state.boot?.tags||[]).map(t=>`<option value="${esc(t)}" ${selected===t?'selected':''}>${esc(t)}</option>`).join('');
}
function scopeOptions(selected='all'){
  return Object.entries({all:'Tất cả từ',due:'Đến hạn ôn',overdue:'Đã quá hạn',new:'Từ mới',learning:'Đang học',mastered:'Đã ghi nhớ tốt',weak:'Từ khó · quên ≥ 3 lần',mistakes:'Từng trả lời sai',unchecked:'Chưa xác nhận nghĩa'})
    .map(([v,l])=>`<option value="${v}" ${selected===v?'selected':''}>${l}</option>`).join('');
}
function readingSourceOptions(selected=''){
  return '<option value="">Mọi bài nguồn</option>'+(state.readingSources||[])
    .map(r=>`<option value="${esc(r.id)}" ${selected===r.id?'selected':''}>${esc(r.title)}</option>`).join('');
}
function chips(tags){return (tags||[]).slice(0,4).map(t=>`<span class="chip">${esc(t)}</span>`).join('');}
function empty(title,desc,button=''){return `<div class="empty-state"><h2>${esc(title)}</h2><p>${esc(desc)}</p>${button}</div>`;}
function formatDate(s){return new Date(s).toLocaleDateString(window.LexiI18n?.language==='zh'?'zh-CN':window.LexiI18n?.language||'vi',{day:'2-digit',month:'2-digit',year:'numeric'});}
function count(value){const n=Number(value);return Number.isFinite(n)&&n>0?Math.floor(n):0;}
function formatNextDue(value){
  const due=new Date(value),minutes=Math.max(1,Math.round((due-Date.now())/60000));
  if(!Number.isFinite(due.getTime()))return '';
  if(minutes<60)return `khoảng ${minutes} phút nữa`;
  if(minutes<48*60)return `khoảng ${Math.round(minutes/60)} giờ nữa`;
  return formatDate(value);
}
function dailyReviewCallout(stats,showAction=true){
  const goal=Math.max(1,count(stats.daily_goal)||20),progress=count(stats.daily_progress ?? stats.daily_goal_progress),shown=Math.min(progress,goal);
  const percent=Math.min(100,Math.round(progress/goal*100)),study=stats.study||{},streak=count(study.current);
  const t=(key,vars)=>esc(window.LexiI18n.t(key,vars)),locale=({vi:'vi-VN',en:'en-GB',fr:'fr-FR',zh:'zh-CN'})[window.LexiI18n.language]||'vi-VN';
  const week=(study.week||[]).map(day=>{
    const date=new Date(day.date+'T12:00:00Z'),label=date.toLocaleDateString(locale,{weekday:'short',timeZone:'UTC'});
    const title=date.toLocaleDateString(locale,{day:'numeric',month:'long',timeZone:'UTC'})+' · '+window.LexiI18n.t(day.active?'streak.studied':'streak.noActivity');
    return `<li class="${day.active?'is-active ':''}${day.today?'is-today':''}" aria-label="${esc(title)}" ${day.today?'aria-current="date"':''}><span>${esc(label)}</span><b aria-hidden="true">${day.active?'✓':date.getUTCDate()}</b><small>${day.today?t('streak.today'):'&nbsp;'}</small></li>`;
  }).join('');
  return `<section class="motivation-card ${showAction?'':'compact'}" data-motivation="${showAction?'full':'compact'}" data-no-i18n><div class="motivation-heading"><span class="streak-symbol" aria-hidden="true">🌱</span><div><span class="eyebrow">${t('streak.eyebrow')}</span><h2>${t('streak.count',{count:streak})}</h2><p>${t(study.active_today?'streak.done':streak?'streak.keep':'streak.start')}</p></div>${showAction?`<a class="btn primary" href="#${count(stats.due)?'study':'catalog'}">${t(count(stats.due)?'streak.review':'streak.read')}</a>`:''}</div>${showAction?`<div class="streak-body"><div><ol class="streak-week" aria-label="${t('streak.week')}">${week}</ol><p class="streak-rule">${t('streak.rule')}</p></div><div class="streak-milestone"><span>${t('streak.best',{count:count(study.longest)})}</span><strong>${t('streak.target',{count:count(study.next_milestone)||3})}</strong><div class="progress-track" role="progressbar" aria-label="${t('streak.milestone')}" aria-valuemin="0" aria-valuemax="${count(study.next_milestone)||3}" aria-valuenow="${streak}"><div class="progress-fill" style="width:${Math.min(100,count(study.milestone_percent))}%"></div></div></div></div>`:''}<div class="daily-review-goal"><div><span>${t('streak.daily')}</span><b>${shown} / ${goal}</b></div><div class="progress-track" role="progressbar" aria-label="${t('streak.daily')}" aria-valuemin="0" aria-valuemax="${goal}" aria-valuenow="${shown}"><div class="progress-fill" style="width:${percent}%"></div></div><small>${t(progress>=goal?'streak.goalDone':'streak.goalNote')}</small></div></section>`;
}
document.addEventListener('lexiread:language',()=>{
  if(state.boot?.stats)document.querySelectorAll('[data-motivation]').forEach(card=>{card.outerHTML=dailyReviewCallout(state.boot.stats,card.dataset.motivation==='full');});
});
async function refreshBoot(){
  state.boot=await api('/bootstrap/');
  $('#ai-status').textContent=state.boot.ai_enabled?'● AI đã kết nối':'○ Không dùng API';
  $('#avatar').textContent=(state.boot.user||'Q').charAt(0).toUpperCase();
  $('#nav-due').textContent=state.boot.stats.due||'';
  $('#analytics-nav')?.classList.toggle('hidden',!state.boot.is_staff);
}
function heading(title,desc,buttons=''){return `<div class="page-heading"><div><h1>${esc(title)}</h1><p>${esc(desc)}</p></div><div class="button-row">${buttons}</div></div>`;}
function readingStatus(r){return r.status==='completed'?'Đã đọc':'Đang đọc';}
function readingCard(r){return `<article class="reading-card"><div class="tags"><span class="chip">${readingStatus(r)}</span>${r.favorite?'<span class="chip warm">★ Yêu thích</span>':''}${r.has_analysis?'<span class="chip warm">Có bản dịch</span>':''}</div><h3 data-no-i18n>${esc(r.title)}</h3><p class="muted" style="font-size:12px;margin:0">${count(r.word_count)} từ · cập nhật ${formatDate(r.updated_at)}</p><div class="card-footer"><span class="muted" style="font-size:11px">${esc(r.source_name||'Bài đọc của bạn')}</span><div class="button-row"><button class="link-btn" data-action="toggle-reading-favorite" data-id="${esc(r.id)}" data-favorite="${r.favorite?'true':'false'}" aria-pressed="${r.favorite?'true':'false'}" aria-label="${r.favorite?'Bỏ yêu thích':'Thêm yêu thích'} ${esc(r.title)}">${r.favorite?'★':'☆'}</button><a href="#reading/${esc(r.id)}" class="btn small secondary">Mở bài →</a></div></div></article>`;}
async function homePage(epoch){return readingHome(epoch);}
async function readingsPage(epoch){
  const f=state.readingFilters,q=new URLSearchParams({...f,limit:12});
  const r=await api('/readings/?'+q);if(epoch!==state.routeEpoch)return;state.readings=r.items||[];
  const total=Number.isFinite(Number(r.total))?Number(r.total):state.readings.length,page=Number(r.page)||f.page,limit=Number(r.limit)||12;
  if(!state.readings.length&&total&&page>1){state.readingFilters.page=Math.max(1,Math.ceil(total/limit));return readingsPage(epoch);}
  $('#main').innerHTML=heading('Bài đọc của tôi','Nội dung bạn tự nhập: đọc, tra từ và hỏi đáp. Không tự chia sẻ vào thư viện chung.',`<button class="btn primary" data-action="new-reading">+ Thêm bài đọc</button>`)+
    `<div class="toolbar"><input type="search" id="reading-search" class="search" placeholder="Tìm tiêu đề, nguồn hoặc nội dung…" value="${esc(f.q)}" aria-label="Tìm bài đọc"><select id="reading-status" aria-label="Tiến độ bài đọc">${[['all','Mọi tiến độ'],['in_progress','Đang đọc'],['completed','Đã đọc']].map(([v,l])=>`<option value="${v}" ${f.status===v?'selected':''}>${l}</option>`).join('')}</select><select id="reading-favorite" aria-label="Bài yêu thích">${[['all','Tất cả bài'],['yes','Chỉ yêu thích'],['no','Chưa yêu thích']].map(([v,l])=>`<option value="${v}" ${f.favorite===v?'selected':''}>${l}</option>`).join('')}</select><select id="reading-sort" aria-label="Sắp xếp bài đọc">${[['updated','Mới cập nhật'],['newest','Mới thêm'],['oldest','Cũ nhất'],['title','Theo tiêu đề']].map(([v,l])=>`<option value="${v}" ${f.sort===v?'selected':''}>${l}</option>`).join('')}</select><button class="btn secondary" data-action="filter-readings">Lọc</button></div>`+
    (state.readings.length?`<div class="section-title"><h2>${total} bài phù hợp</h2><span class="fineprint">Bài và tiến độ chỉ thuộc tài khoản này</span></div><div class="card-grid">${state.readings.map(readingCard).join('')}</div><div class="pagination"><span>Trang ${page} / ${Math.max(1,Math.ceil(total/limit))}</span><div class="button-row"><button class="btn small" data-action="readings-prev" ${page<=1?'disabled':''}>← Trước</button><button class="btn small" data-action="readings-next" ${page*limit>=total?'disabled':''}>Sau →</button></div></div>`:empty(total?'Không có bài ở trang này':'Không có bài phù hợp',f.q||f.status!=='all'||f.favorite!=='all'?'Thử đổi từ khóa hoặc bộ lọc.':'Dán nội dung tiếng Anh hoặc nhập file để bắt đầu.'));
}
function escapeRegex(s){return String(s).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}
function highlight(text,terms){
  const words=[...new Set(terms||[])].filter(x=>x&&x.length<161).sort((a,b)=>b.length-a.length).slice(0,100);
  if(!words.length)return esc(text);
  const re=new RegExp('(?<!\\w)('+words.map(escapeRegex).join('|')+')(?!\\w)','gi');
  let out='',last=0;
  for(const match of text.matchAll(re)){out+=esc(text.slice(last,match.index))+'<mark>'+esc(match[0])+'</mark>';last=match.index+match[0].length;}
  return out+esc(text.slice(last));
}
async function readerPage(id,epoch){
  const [r,words]=await Promise.all([api('/readings/'+id+'/'),api('/vocabulary/?reading='+id+'&limit=500')]);
  if(epoch!==state.routeEpoch)return;ensureReadingState(r);state.reading=r;state.readerWords=words.items;
  const history=await api('/readings/'+id+'/questions/');if(epoch!==state.routeEpoch)return;state.qaHistory=history.items;
  $$('[data-nav]').forEach(a=>a.classList.toggle('active',a.dataset.nav===(r.catalog_slug?'catalog':'readings')));renderReader();
}
function renderReader(){
  const r=state.reading,a=r.analysis||{},v=a.vocabulary||[],g=a.grammar||[],curated=!!r.catalog_slug;
  const hasTranslations=!!a.translations?.length, showTranslation=state.translation&&hasTranslations;
  const hasHelp=!!(state.boot?.ai_enabled||r.lesson?.faqs?.length||state.qaHistory?.length||state.readingTab==='help');
  const tabs=[['text','Bài đọc'],...(v.length?[['words',`Từ gợi ý (${v.length})`]]:[]),...(g.length?[['grammar','Cách dùng trong bài']]:[]),...(curated?[['quiz','Hiểu bài']]:[]),...(hasHelp?[['help','Giải thích thêm']]:[])];
  if(!tabs.some(([key])=>key===state.readingTab))state.readingTab='text';
  $('#main').innerHTML=`<a href="${curated?(r.lesson?.track==='ielts'?'#ielts':'#catalog'):'#readings'}" class="link-btn">← ${curated?(r.lesson?.track==='ielts'?'Luyện IELTS Reading':'Thư viện luyện đọc'):'Bài đọc của tôi'}</a><div style="height:17px"></div>`+
   heading(r.title,`${curated?(r.lesson?.level+' · '+window.LexiLibrary.topicLabel(r.lesson?.topic)+' · '):''}${r.word_count} từ · ${r.paragraphs.length} đoạn`,
   `<button class="btn small" data-action="toggle-reading-favorite" data-id="${esc(r.id)}" data-favorite="${r.favorite?'true':'false'}" aria-pressed="${r.favorite?'true':'false'}">${r.favorite?'★ Đã yêu thích':'☆ Yêu thích'}</button>${!curated?'<button class="btn small" data-action="edit-reading">Sửa bài</button><button class="btn small danger" data-action="delete-reading">Xóa</button>':''}<button class="btn small secondary" data-action="study-reading">Ôn từ đã lưu từ bài này ↗</button>`)+
   `${curated?`<details class="lesson-about"><summary>Về bài luyện này</summary><p>${esc(r.lesson?.provenance||'Bài luyện do LexiRead biên soạn.')} ${esc(r.lesson?.level_note||'')}</p><small>Bản bạn đang học: ${r.lesson?.revision||1}.</small></details>`:''}
   <div class="toolbar">${!curated?`<details class="lesson-about"><summary>Thêm bản dịch và gợi ý</summary><div class="button-row">${state.boot?.ai_enabled?`<button class="btn primary" data-action="analyse-reading">✦ ${r.has_analysis?'Tạo lại gợi ý':'Dịch và gợi ý từ'}</button>`:''}<button class="btn" data-action="reading-prompt">Nhập gợi ý từ công cụ khác</button></div></details>`:''}${hasTranslations?`<label class="check-label"><input type="checkbox" id="translation-toggle" ${state.translation?'checked':''}> Hiện bản dịch</label>`:'<span class="fineprint">Chưa có bản dịch</span>'}<label class="font-control">Cỡ chữ<select id="reading-font">${[17,19,22].map(n=>`<option value="${n}" ${(state.readerFont||19)===n?'selected':''}>${n}</option>`).join('')}</select></label></div>
   <div class="reading-progress-bar"><button class="link-btn" data-action="jump-bookmark">Dấu trang: đoạn ${(r.progress?.paragraph||0)+1} ↗</button><span>${r.progress?.quiz_total?`Hiểu bài: tốt nhất ${r.progress.quiz_best}/${r.progress.quiz_total}`:''}</span><button class="btn small ${r.progress?.completed?'secondary':''}" data-action="complete-reading">${r.progress?.completed?'✓ Đã đọc · bỏ đánh dấu':'Đánh dấu đã đọc'}</button></div>
   <div class="reader-tabs">${tabs.map(([k,l])=>`<button data-action="reader-tab" data-tab="${k}" class="${state.readingTab===k?'active':''}">${l}</button>`).join('')}</div><div id="reader-content" style="--reading-font-size:${state.readerFont||19}px"></div>`;
  const box=$('#reader-content');
  if(state.readingTab==='text'){
    const tr=new Map((a.translations||[]).map(t=>[t.index,t.vi]));
    box.innerHTML='<p class="fineprint">Bôi đen từ để tra nghĩa, nghe phát âm hoặc lưu lại.</p>'+
      (showTranslation?'<div class="reader-labels"><b>ENGLISH · VĂN BẢN GỐC</b><span>TIẾNG VIỆT · BẢN DỊCH THAM KHẢO</span></div>':'')+
      r.paragraphs.map((p,i)=>`<section class="parallel-row ${showTranslation?'':'single'}" data-paragraph="${i}"><div><div class="paragraph-tools"><span class="paragraph-index">ĐOẠN ${String(i+1).padStart(2,'0')}</span><button class="link-btn" data-action="bookmark-paragraph" data-index="${i}">${r.progress?.paragraph===i?'◆':'◇'} Đọc đến đây</button>${state.boot?.ai_enabled?`<button class="link-btn" data-action="ask-paragraph" data-index="${i}">Hỏi đoạn này</button>`:''}</div><p class="reader-en" data-index="${i}">${highlight(p,[...v.map(w=>w.word),...(state.readerWords||[]).map(w=>w.word)])}</p></div>${showTranslation?`<div><span class="paragraph-index">BẢN DỊCH ${String(i+1).padStart(2,'0')}</span><p class="reader-vi">${esc(tr.get(i)||'Chưa dịch đoạn này.')}</p></div>`:''}</section>`).join('');
  }else if(state.readingTab==='words'){
    box.innerHTML=v.length?`<div class="section-title"><div><h2>Chọn những từ bạn cần học</h2><p>Chưa lưu tự động. Bạn có thể sửa lại từng thẻ sau khi lưu.</p></div><button class="btn primary" data-action="save-candidates">Lưu mục đã chọn</button></div><label class="check-label" style="margin-bottom:15px"><input id="select-all-candidates" type="checkbox"> Chọn tất cả</label>`+
      v.map((w,i)=>`<article class="candidate"><input class="candidate-check" type="checkbox" value="${i}" aria-label="Chọn ${esc(w.word)}"><div class="candidate-body"><h3>${esc(w.word)} <small class="muted">${esc(w.pos)}</small></h3><p>${esc(w.meaning_vi)}</p>${lexicalDetails(w)}${lexicalContext(w)}${r.catalog_slug?'':'<span class="chip warm">Gợi ý AI · cần bạn kiểm tra</span>'}</div></article>`).join(''):empty('Chưa có từ gợi ý','Phân tích bài đọc để chọn từ; hoặc bôi đen từ trong phần tiếng Anh.');
  }else if(state.readingTab==='grammar'){
    box.innerHTML=g.length?g.map(x=>`<article class="panel grammar-card"><h3 class="pattern">${esc(x.pattern)}</h3><blockquote class="quote">${esc(x.evidence)}</blockquote><p>${esc(x.explanation_vi)}</p><div class="notice"><b>Ví dụ luyện tập:</b> ${esc(x.example)}<br>${esc(x.example_vi)}</div></article>`).join(''):empty('Chưa có cấu trúc gợi ý','Dùng phân tích bài đọc hoặc nhập kết quả JSON theo mẫu.');
  }else{readingExtraTab(box,r);}
  if(a.warnings?.length)box.insertAdjacentHTML('beforeend',`<div class="notice">${a.warnings.map(esc).join('<br>')}</div>`);
}
async function vocabPage(epoch){
  const f=state.filters,q=new URLSearchParams({...f,limit:24});
  const [data,sources]=await Promise.all([api('/vocabulary/?'+q),api('/vocabulary/sources/')]);
  if(epoch!==state.routeEpoch)return;state.vocab=data.items;state.vocabTotal=data.total;
  if(!state.vocab.length&&data.total&&f.page>1){state.filters.page=Math.max(1,Math.ceil(data.total/data.limit));return vocabPage(epoch);}
  state.readingSources=[...new Map((sources.items||[]).map(r=>[r.id,r])).values()].sort((a,b)=>a.title.localeCompare(b.title,'vi'));
  $('#main').innerHTML=heading('Kho từ của tôi',`${data.total} thẻ theo bộ lọc hiện tại. Từ, nghĩa, ngữ cảnh và lịch ôn — trong cùng một nơi.`,
     '<a class="btn primary" href="#word-import">Nhập bộ từ cá nhân →</a><button class="btn secondary" data-action="new-word">+ Thêm một từ</button>')+
     (f.tag?`<div class="button-row deck-library-actions"><button class="btn small" data-action="study-deck">Ôn bộ này</button><button class="btn small" data-action="export-deck">Tải bộ từ</button></div>`:'')+
     `<div class="toolbar"><input type="search" id="vocab-search" class="search" placeholder="Tìm từ, nghĩa hoặc ghi chú…" value="${esc(f.q)}" aria-label="Tìm từ"><select id="vocab-tag" aria-label="Bộ từ">${tagOptions(f.tag)}</select><select id="vocab-reading" aria-label="Bài nguồn">${readingSourceOptions(f.reading)}</select><select id="vocab-scope" aria-label="Trạng thái">${scopeOptions(f.scope)}</select><select id="vocab-sort" aria-label="Sắp xếp từ">${[['newest','Mới thêm'],['oldest','Cũ nhất'],['word','Theo từ A–Z'],['due','Lịch ôn gần nhất']].map(([v,l])=>`<option value="${v}" ${f.sort===v?'selected':''}>${l}</option>`).join('')}</select><button class="btn secondary" data-action="filter-vocab">Lọc</button></div>`+
     (data.items.length?`<div class="table-wrap"><table><thead><tr><th>TỪ / CỤM TỪ</th><th>NGHĨA ĐANG HỌC</th><th>BỘ TỪ & TIẾN ĐỘ</th><th></th></tr></thead><tbody>${data.items.map(v=>`<tr><td><div class="word">${esc(v.word)}</div><span class="muted">${esc(v.pos||'Từ / cụm từ')}${v.verified?' · Đã duyệt':''}</span></td><td class="meaning-cell">${esc(v.meaning_vi)}${lexicalRelations(v)}<details class="source-context"><summary>Cấu trúc & ví dụ</summary>${lexicalDetails({...v,synonyms:[],paraphrases:[]})}</details></td><td><div class="tags">${chips(v.tags)}</div><span class="muted">${v.due?'Đến hạn ôn':'Ôn tiếp '+formatDate(v.due_at)}${v.lapses?' · '+v.lapses+' lần quên':''}</span>${v.reading_id?`<div><a class="link-btn" href="#reading/${esc(v.reading_id)}">${esc(v.source_label||'Mở bài nguồn')} →</a></div>`:''}</td><td><button class="btn small" data-action="edit-word" data-id="${esc(v.id)}">Sửa</button></td></tr>`).join('')}</tbody></table></div><div class="pagination"><span>Trang ${data.page} / ${Math.max(1,Math.ceil(data.total/data.limit))}</span><div class="button-row"><button class="btn small" data-action="vocab-prev" ${f.page<=1?'disabled':''}>← Trước</button><button class="btn small" data-action="vocab-next" ${f.page*data.limit>=data.total?'disabled':''}>Sau →</button></div></div>`:
       empty('Chưa có từ ở đây','Nhập một bộ theo chủ đề để có sẵn từ, ví dụ và lịch ôn.', '<a class="btn primary" href="#word-import">Nhập bộ từ đầu tiên →</a>'));
}
function openModal(title,content,footer='',drawer=false){
  const m=$('#modal');if(m.open)m.close();m.className=drawer?'drawer':'';
  $('#modal-content').innerHTML=`<header class="modal-header"><h2 id="modal-title">${esc(title)}</h2><button class="icon-btn" data-action="close-modal" aria-label="Đóng cửa sổ">×</button></header><div class="modal-body">${content}</div>${footer?`<footer class="modal-footer">${footer}</footer>`:''}`;
  m.showModal();
}
function closeModal(){ window.LexiDictionary?.stopAudio(); $('#modal').close(); }
function readingModal(edit=false){
  state.editReading=edit;
  const r=edit?state.reading:{};
  openModal(edit?'Chỉnh sửa bài đọc':'Thêm một bài đọc mới',`<form id="reading-form"><label>Tiêu đề<input id="reading-title" value="${esc(r.title||'')}" maxlength="200" placeholder="Ví dụ: Set in Metal" required></label>${!edit?'<label class="upload-zone">Nhập file (tùy chọn)<input type="file" id="reading-file" accept=".txt,.md,.pdf,.docx"><span class="field-hint">Tối đa 8 MB, PDF tối đa 30 trang. PDF scan chưa được hỗ trợ.</span></label>':''}<label>Văn bản tiếng Anh<textarea id="reading-text" rows="12" placeholder="Dán passage ở đây. Giữ một dòng trống giữa các đoạn.">${esc(r.text||'')}</textarea><span class="field-hint">Tối đa 60.000 ký tự. Phân tích AI một lần: tối đa 16.000 ký tự. Kiểm tra thứ tự đoạn sau khi nhập PDF/DOCX.</span></label>${edit?'<div class="notice">Sửa nội dung gốc sẽ xóa kết quả phân tích cũ. Các thẻ đã lưu vẫn được giữ lại.</div>':''}</form>`,
    '<button class="btn" data-action="close-modal">Hủy</button><button class="btn primary" data-action="save-reading">Lưu bài đọc</button>');
}
async function saveReading(btn){
  const title=$('#reading-title').value.trim(),text=$('#reading-text').value.trim(),file=$('#reading-file')?.files[0];
  if(!title)throw new Error('Hãy nhập tiêu đề bài đọc.');
  if(!file&&!text)throw new Error('Dán nội dung hoặc chọn một file.');
  if(file&&text&&!confirm('Bạn đã chọn file và dán văn bản. Nhập nội dung từ file và bỏ phần văn bản vừa dán?'))return;
  await busy(btn,async()=>{
    let data={title,text};
    if(file&&!state.editReading){data=new FormData();data.append('title',title);data.append('file',file);}
    const r=await api(state.editReading?'/readings/'+state.reading.id+'/':'/readings/',{method:state.editReading?'PATCH':'POST',data});
    closeModal();await refreshBoot();state.readingTab='text';
    if(location.hash==='#reading/'+r.id)await route();else location.hash='reading/'+r.id;
    toast('Đã lưu bài đọc.');
  });
}

function lexicalRelations(w){
  return (asList(w.synonyms).length?`<div class="syn-line"><b>Từ gần nghĩa (synonyms):</b> <span lang="en">${esc(asList(w.synonyms).join(' · '))}</span></div>`:'')+
    (asList(w.paraphrases).length?`<div class="syn-line"><b>Diễn giải nghĩa (paraphrase):</b> <span lang="en">${esc(asList(w.paraphrases).join(' · '))}</span></div>`:'');
}
function lexicalDetails(w){
  const example=String(w.example||'').trim();
  const shortExample=example.length<=240&&example.split(/\s+/).length<=35&&!example.includes('\n')?example:'';
  return `<div class="lexical-detail"><p><span class="lexical-label">CẤU TRÚC / CỤM TỪ THƯỜNG DÙNG</span>${w.usage_pattern?`<span lang="en">${esc(w.usage_pattern)}</span>`:'<span class="muted">Chưa có cấu trúc dùng từ.</span>'}</p><div class="lexical-example"><span class="lexical-label">VÍ DỤ CƠ BẢN</span>${shortExample?`<p lang="en">${esc(shortExample)}</p>${w.example_vi?`<p class="muted">${esc(w.example_vi)}</p>`:''}`:'<p class="muted">Chưa có ví dụ ngắn. Bạn có thể bổ sung trong Sửa thẻ.</p>'}</div>${lexicalRelations(w)}</div>`;
}
function lexicalContext(w){
  return w.context||w.note?`<details class="source-context"><summary>Xem ngữ cảnh gốc & lưu ý</summary>${w.context?`<blockquote class="quote" lang="en">${esc(w.context)}</blockquote>`:''}${w.note?`<p class="fineprint">${esc(w.note)}</p>`:''}<p class="fineprint">Từ gần nghĩa và diễn giải không phải lúc nào cũng thay thế trực tiếp được.</p></details>`:'';
}

function blankEntry(){return {word:'',pos:'',meaning_vi:'',synonyms:[],paraphrases:[],example:'',example_vi:'',usage_pattern:'',context:'',note:'',tags:[],verified:false,origin:'manual',source_label:'',reading_id:null};}
function editor(v=null,id=null){
  if(v!==null){state.editing={...blankEntry(),...v};state.editId=id;}
  const w=state.editing||blankEntry();
  openModal(state.editId?'Sửa thẻ từ vựng':'Giữ lại một từ mới',`<form id="word-form"><div class="form-grid"><label>Từ / cụm từ<input id="word-word" value="${esc(w.word)}" maxlength="160" required></label><label>Từ loại<input id="word-pos" value="${esc(w.pos)}" placeholder="adj, n, v, phrase…" maxlength="40"></label><label class="span-2">Nghĩa tiếng Việt — theo ngữ cảnh<textarea id="word-meaning" rows="2" required>${esc(w.meaning_vi)}</textarea></label><label class="span-2">Ngữ cảnh gốc<textarea id="word-context" rows="3">${esc(w.context)}</textarea><span class="field-hint">Giữ nguyên câu gốc để phân biệt những nghĩa khác nhau.</span></label><div class="span-2 button-row" style="margin-bottom:18px">${state.boot?.ai_enabled?'<button type="button" class="btn small secondary" data-action="lookup-word">✦ Gợi ý nghĩa</button>':''}<details class="lesson-about"><summary>Thêm gợi ý từ công cụ khác</summary><button type="button" class="btn small" data-action="word-prompt">Mở hướng dẫn nhập</button></details></div><label>Từ gần nghĩa<input id="word-synonyms" value="${esc(asList(w.synonyms).join(' | '))}" placeholder="relevant | applicable"><span class="field-hint">Ngăn cách các mục bằng dấu |</span></label><label>Cách diễn đạt tương đương<input id="word-paraphrases" value="${esc(asList(w.paraphrases).join(' | '))}" placeholder="directly related to the topic"></label><label class="span-2">Cấu trúc / cụm từ thường dùng<input id="word-usage-pattern" value="${esc(w.usage_pattern||'')}" maxlength="300" placeholder="depend on + noun / be interested in + V-ing"></label><label>Ví dụ ngắn (một câu cơ bản)<textarea id="word-example" rows="2">${esc(w.example)}</textarea></label><label>Nghĩa của ví dụ<textarea id="word-example-vi" rows="2">${esc(w.example_vi)}</textarea></label><label class="span-2">Lưu ý khi dùng từ<textarea id="word-note" rows="2">${esc(w.note)}</textarea></label><label class="span-2">Nhãn để dễ tìm lại<input id="word-tags" value="${esc(asList(w.tags).join(' | '))}" placeholder="Từ cá nhân | Công việc"></label><label class="span-2 check-label"><input type="checkbox" id="word-verified" ${w.verified?'checked':''}> Tôi đã kiểm tra nghĩa và ngữ cảnh của thẻ này.</label></div></form><div class="notice">Một từ có nhiều nghĩa có thể có nhiều thẻ. Gợi ý AI không tự được đánh dấu “đã duyệt”.</div>`,
      `${state.editId?'<button class="btn danger" style="margin-right:auto" data-action="delete-word">Xóa thẻ</button>':''}<button class="btn" data-action="close-modal">Hủy</button><button class="btn primary" data-action="save-word">Lưu thẻ</button>`,true);
}
function readEditor(){
  const list=id=>$('#'+id).value.split('|').map(x=>x.trim()).filter(Boolean);
  return {...state.editing,word:$('#word-word').value.trim(),pos:$('#word-pos').value.trim(),meaning_vi:$('#word-meaning').value.trim(),context:$('#word-context').value.trim(),synonyms:list('word-synonyms'),paraphrases:list('word-paraphrases'),usage_pattern:$('#word-usage-pattern').value.trim(),example:$('#word-example').value.trim(),example_vi:$('#word-example-vi').value.trim(),note:$('#word-note').value.trim(),tags:list('word-tags'),verified:$('#word-verified').checked};
}
async function saveWord(btn){
  const v=readEditor();if(!v.word||!v.meaning_vi)throw new Error('Cần có từ và nghĩa tiếng Việt.');
  await busy(btn,async()=>{
    const result=await api(state.editId?'/vocabulary/'+state.editId+'/':'/vocabulary/',{method:state.editId?'PATCH':'POST',data:v});
    closeModal();clearSelection();await refreshBoot();await route();
    toast(result.skipped?'Thẻ này đã có; giữ nguyên tiến độ cũ.':'Đã lưu thẻ và lịch ôn.');
  });
}
function clearSelection(){state.selection=null;$('#selection-bar').hidden=true;}
function captureSelection(){
  const sel=window.getSelection();
  if($('#modal').open)return;
  if(!sel||sel.isCollapsed||!state.reading){clearSelection();return;}
  const node=sel.anchorNode?.nodeType===1?sel.anchorNode:sel.anchorNode?.parentElement;
  const end=sel.focusNode?.nodeType===1?sel.focusNode:sel.focusNode?.parentElement;
  const p=node?.closest('.reader-en'),p2=end?.closest('.reader-en');
  if(!p||p!==p2){clearSelection();return;}
  const word=sel.toString().trim();
  if(!word||word.length>4000){clearSelection();return;}
  $('[data-action=selected-dictionary]').hidden=!window.LexiDictionary.canLookup(word);
  $('[data-action=selected-word]').disabled=word.length>160||word.split(/\s+/).length>16;
  const para=state.reading.paragraphs[Number(p.dataset.index)];
  let context=para;
  if(context.length>4000){const start=Math.max(0,para.indexOf(word)-400);context=para.slice(start,start+1600);}
  state.selection={word,context,reading_id:state.reading.id,source_label:state.reading.title,tags:[state.reading.title]};
  $('#selected-word').textContent=word;$('#selection-bar').hidden=false;
}
function cloudConsent(subject){
  if(!state.boot.ai_enabled){toast('Chưa cấu hình API. Dùng Copy prompt / Dán JSON hoặc xem phần Cài đặt.',true);return false;}
  return confirm(subject+' sẽ được gửi tới OpenAI để xử lý. API có thể phát sinh phí riêng; chỉ gửi nội dung bạn được phép sử dụng. Tiếp tục?');
}
function showPrompt(prompt,task){
  state.promptTask=task;
  openModal('Dùng AI mà không cần nối API',`<p class="muted" style="font-size:13px">Copy prompt bên dưới, dán vào ChatGPT hoặc AI bạn đang dùng. Sau đó dán đúng kết quả JSON vào ô thứ hai. Ứng dụng không tự gửi nội dung ở bước này.</p><label>Prompt đã kèm dữ liệu và cấu trúc JSON<textarea id="prompt-text" rows="5" readonly>${esc(prompt)}</textarea></label><button class="btn small secondary" data-action="copy-prompt">Sao chép prompt</button><label style="margin-top:20px">Dán kết quả JSON<textarea id="result-json" rows="9" placeholder='{"translations": [...], "vocabulary": [...], "grammar": [...]}'></textarea></label><div class="notice">Kết quả được kiểm tra cấu trúc trước khi lưu. Nếu AI bỏ sót đoạn hoặc bịa trích dẫn, ứng dụng sẽ báo lỗi hoặc loại gợi ý đó.</div>`,
    '<button class="btn" data-action="close-modal">Đóng</button><button class="btn primary" data-action="apply-prompt">Nhập kết quả JSON</button>');
}
function parseJSONInput(text){return JSON.parse(text.trim().replace(/^```(?:json)?\s*/i,'').replace(/\s*```$/,''));}
async function applyPrompt(btn){
  const text=$('#result-json').value.trim();if(!text)throw new Error('Chưa có kết quả JSON.');
  let data;try{data=parseJSONInput(text);}catch(e){throw new Error('JSON chưa hợp lệ. Chỉ dán khối JSON trả về từ AI.');}
  if(state.promptTask==='question'){
    const q=state.pendingQuestion;if(!q)throw new Error('Câu hỏi đã thay đổi. Tạo prompt mới.');
    await busy(btn,async()=>{const answer=await api('/readings/'+q.reading_id+'/questions/',{method:'POST',data:{...q,result:data}});closeModal();if(state.reading?.id===q.reading_id){state.qaHistory=[answer,...state.qaHistory].slice(0,30);state.readingTab='help';renderReader();}toast('Đã lưu lời giải và trích dẫn để bạn kiểm tra.');});return;
  }
  if(state.promptTask==='word'){state.editing={...state.editing,...data,origin:'ai',verified:false};editor();return;}
  if(state.promptTask==='words'){previewBulk(data.vocabulary||data);return;}
  await busy(btn,async()=>{await api('/readings/'+state.reading.id+'/analyse/',{method:'POST',data:{result:data}});closeModal();await route();toast('Đã nhập bản dịch và các gợi ý. Chưa tự lưu thẻ từ.');});
}
function bulkModal(){
  openModal('Thêm nhiều từ — không chép từng thẻ',`<label>Danh sách từ — mỗi dòng một mục<textarea id="bulk-text" rows="9" placeholder="pertinent\naptitude\nflawed = defective\n\nHoặc nhập sẵn nghĩa:\npertinent | liên quan trực tiếp | relevant"></textarea></label><div class="button-row"><button class="btn primary" data-action="bulk-ai">✦ AI điền nghĩa</button><button class="btn" data-action="bulk-prompt">Copy prompt / Dán JSON</button><button class="btn small secondary" data-action="bulk-parse">Đọc dòng có sẵn nghĩa</button></div><div class="notice">AI: tối đa 50 dòng/lần. Không API: dùng định dạng <b>word | nghĩa Việt | synonym 1; synonym 2</b> hoặc import JSON/CSV trong Cài đặt & dữ liệu.</div>`,
    '<button class="btn" data-action="close-modal">Đóng</button>');
}
function previewBulk(items){
  if(!Array.isArray(items)||!items.length||items.length>100)throw new Error('Cần danh sách từ gồm 1–100 mục.');
  state.bulk=items.map(v=>({...blankEntry(),...v,synonyms:asList(v.synonyms),paraphrases:asList(v.paraphrases),tags:asList(v.tags).length?asList(v.tags):['Từ cá nhân']}));
  openModal('Duyệt các thẻ trước khi lưu',`<p class="fineprint">Sửa từ hoặc nghĩa ngay trong bảng. Các mục trùng từ + nghĩa không đặt lại tiến độ cũ.</p><div class="table-wrap"><table><thead><tr><th></th><th>TỪ</th><th>NGHĨA</th></tr></thead><tbody>${state.bulk.map((v,i)=>`<tr><td><input class="bulk-check" type="checkbox" value="${i}" checked aria-label="Chọn mục ${i+1}"></td><td><input id="bulk-word-${i}" value="${esc(v.word)}" aria-label="Từ"><span class="muted">${esc(v.note)}</span></td><td><textarea id="bulk-meaning-${i}" rows="2" aria-label="Nghĩa">${esc(v.meaning_vi)}</textarea><span class="muted">${esc(v.synonyms.join(' · '))}</span></td></tr>`).join('')}</tbody></table></div>`,
    '<button class="btn" data-action="close-modal">Hủy</button><button class="btn primary" data-action="bulk-save">Lưu các mục đã chọn</button>');
}
function renderStudy(){
  const p=state.studySettings,s=state.boot.stats;
  $('#main').innerHTML=heading('Luyện nhớ, không học vẹt.','Chọn cách ôn phù hợp. Mỗi lượt trả lời được lưu vào lịch ôn của từng nghĩa.')+
    dailyReviewCallout(s,false)+
    `<section class="stats">${[[count(s.overdue ?? s.due),'Đã quá hạn','Ưu tiên ôn trước'],[count(s.new),'Từ mới','Chưa bắt đầu lịch ôn'],[count(s.learning),'Đang học','Đang tạo trí nhớ dài hạn'],[count(s.mastered),'Đã ghi nhớ tốt','Vẫn sẽ quay lại đúng lịch'],[count(s.weak),'Từ khó','Quên từ 3 lần · nên sửa ngữ cảnh']].map(([n,l,h])=>`<div class="stat"><div class="stat-top">${l}</div><div class="stat-value">${n}</div><div class="stat-note">${h}</div></div>`).join('')}</section>`+
    `<div class="study-controls"><label>Dạng luyện<select id="study-mode">${Object.entries(modes).map(([k,v])=>`<option value="${k}" ${p.mode===k?'selected':''}>${v}</option>`).join('')}</select></label><label>Bộ từ<select id="study-tag">${tagOptions(p.tag)}</select></label><label>Bài nguồn<select id="study-reading">${readingSourceOptions(p.reading)}</select></label><label>Phạm vi<select id="study-scope">${scopeOptions(p.scope)}</select></label><label>Số thẻ ban đầu<select id="study-limit">${[10,20,30,50].map(n=>`<option ${String(n)===String(p.limit)?'selected':''}>${n}</option>`).join('')}</select></label><button class="btn primary" data-action="start-study">Bắt đầu →</button></div><div class="study-stage" id="study-stage"></div>`;
  renderStage();
}
function renderStage(){
  const s=state.study,stage=$('#study-stage');if(!stage)return;
  if(!s){stage.innerHTML=empty('Một lượt ôn nhỏ, một bước tiến','Flashcard để nhớ nghĩa. ABCD và gõ từ để tự kiểm tra. Bạn không cần đặt câu dài.');return;}
  if(s.finished){
    stage.innerHTML=`<div class="session-finish"><div class="finish-icon">✓</div><h2>Bạn đã hoàn thành lượt ôn.</h2><p class="muted">${s.mode==='flashcard'?`${s.initialCount} thẻ gốc · ${s.done} lượt đánh giá${s.retryCount?` · ${s.retryCount} thẻ được gặp lại`:''}.`:`${s.done} câu đã được lưu tiến độ. Đúng ${s.correct}/${s.done} câu.`}</p><p class="fineprint">Mỗi thẻ sẽ được hẹn ôn lại theo mức bạn vừa chọn.</p><div class="button-row"><button class="btn primary" data-action="start-study">Luyện lượt khác</button><a class="btn" href="#vocabulary">Xem kho từ</a></div></div>`;return;
  }
  const count=s.mode==='flashcard'?s.cards.length:Number(state.studySettings.limit);
  let content=`<div class="study-top"><span>${esc(modes[s.mode])}${s.mode==='flashcard'&&s.retryCount?` · ${s.retryCount} lượt học lại`:''}</span><span>${s.done} / ${count}</span></div><div class="progress-track"><div class="progress-fill" style="width:${Math.min(100,s.done/count*100)}%"></div></div>${s.lastReview?`<div class="notice success">Đã lưu “${esc(s.lastReview.word)}”. Ôn tiếp ${esc(formatNextDue(s.lastReview.due_at))}.</div>`:''}`;
  if(s.mode==='flashcard'){
    const v=s.cards[s.idx];if(!v){s.finished=true;renderStage();return;}
    content+=`<div class="flashcard" role="button" tabindex="0" data-action="flip-card" aria-label="Lật thẻ"><span class="eyebrow">${s.flipped?'MEANING · ĐÁP ÁN':'THỬ NHỚ NGHĨA TRƯỚC KHI LẬT'}${v._retry?' · LƯỢT GẶP LẠI':''}</span><div class="word">${esc(v.word)}</div><span class="muted">${esc(v.pos)}</span>${s.flipped?`<div class="meaning">${esc(v.meaning_vi)}</div>${lexicalDetails(v)}`:`<p class="prompt">Nhấn vào thẻ hoặc phím Space để xem nghĩa.</p><div class="tags">${chips(v.tags)}</div>`}</div>${s.flipped?lexicalContext(v):''}${s.flipped?`<div class="ratings">${[['again','Quên','1 · gặp lại sau 3 thẻ'],['hard','Khó','2 · cần gặp lại'],['good','Nhớ','3 · tiếp tục'],['easy','Dễ','4 · giãn cách hơn']].map(([r,l,h])=>`<button class="rating" data-action="rate-card" data-rating="${r}" ${s.busy?'disabled':''}>${l}<small>${h}</small></button>`).join('')}</div>`:''}`;
  }else if(s.question){
    const q=s.question,result=s.result;
    content+=`<div class="question-card"><span class="eyebrow">${esc(q.caption)}</span><div class="question-prompt">${esc(q.prompt)}</div>${q.pos?`<p class="fineprint">Từ loại: ${esc(q.pos)}</p>`:''}${q.context?`<blockquote class="quote">${esc(q.context)}</blockquote>`:''}${q.mode==='typing'?`<form id="typing-form"><label>Gõ đúng từ/cụm từ đã lưu<input id="typing-answer" autocomplete="off" spellcheck="false" ${result?'disabled':''} value="${esc(result?.submitted_answer||'')}"></label>${!result?'<button class="btn primary" type="submit">Kiểm tra</button>':''}</form>`:`<div class="options">${q.options.map((x,i)=>`<button class="option ${result?(x===result.answer?'correct':x===result.submitted_answer?'wrong':''):''}" data-action="answer-quiz" data-index="${i}" ${result||s.busy?'disabled':''}><span class="letter">${String.fromCharCode(65+i)}</span><span>${esc(x)}</span></button>`).join('')}</div>`}${result?`<div class="feedback ${result.correct?'':'wrong'}"><strong>${result.correct?'✓ Chính xác.':'Chưa đúng theo nghĩa của thẻ này.'}</strong>Đáp án: <b>${esc(result.answer)}</b><div style="margin-top:7px">${esc(result.note)}</div></div><div class="button-row" style="justify-content:end;margin-top:18px"><button class="btn primary" data-action="next-quiz">Câu tiếp theo →</button></div>`:''}</div><p class="fineprint" style="margin-top:14px">Bài luyện tạo từ dữ liệu đã lưu, không phải đề IELTS chính thức. Nếu thấy hai đáp án đều hợp lý, hãy sửa nghĩa/synonym của thẻ trong kho từ.</p>`;
  }else content+=empty('Đang chọn thẻ…','');
  stage.innerHTML=content;
}
async function startStudy(btn){
  if(state.study&&!state.study.finished&&state.study.done>0&&!confirm('Bắt đầu lượt mới? Tiến độ các thẻ đã trả lời vẫn được giữ.'))return;
  state.studySettings={mode:$('#study-mode').value,tag:$('#study-tag').value,reading:$('#study-reading').value,scope:$('#study-scope').value,limit:$('#study-limit').value};
  const p=state.studySettings;
  await busy(btn,async()=>{
    state.study={mode:p.mode,cards:[],idx:0,done:0,correct:0,flipped:false,seen:[],finished:false,busy:false,token:uid(),question:null,result:null,initialCount:0,retryCount:0,retried:new Set(),lastReview:null};
    if(p.mode==='flashcard'){
      const priority=['due','overdue'].includes(p.scope),r=await api('/vocabulary/?'+new URLSearchParams({tag:p.tag,reading:p.reading,scope:p.scope,sort:priority?'due':'newest',limit:500}));
      state.study.cards=(priority?r.items:shuffle(r.items)).slice(0,Number(p.limit));state.study.initialCount=state.study.cards.length;
      if(!r.items.length){state.study=null;renderStage();throw new Error('Không có thẻ phù hợp. Hãy đổi sang “Tất cả từ” hoặc một bộ từ khác.');}
      renderStage();
    }else await loadNextQuiz();
  });
}
function shuffle(a){const b=[...a];for(let i=b.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[b[i],b[j]]=[b[j],b[i]];}return b;}
async function rateCard(rating){
  const s=state.study;if(!s||s.busy||!s.flipped)return;
  s.busy=true;renderStage();
  try{
    const current=s.cards[s.idx],result=await api('/vocabulary/'+current.id+'/review/',{method:'POST',data:{rating,token:s.token}});
    if(rating==='again'&&!s.retried.has(current.id)){
      s.retried.add(current.id);s.retryCount++;
      s.cards.splice(Math.min(s.cards.length,s.idx+4),0,{...current,_retry:true});
    }
    s.lastReview={word:current.word,due_at:result.due_at};s.idx++;s.done++;s.flipped=false;s.token=uid();if(s.idx>=s.cards.length)s.finished=true;await refreshBoot();
  }
  finally{s.busy=false;renderStage();}
}
async function loadNextQuiz(){
  const s=state.study;if(!s)return;
  if(s.done>=Number(state.studySettings.limit)){s.finished=true;renderStage();return;}
  s.question=null;s.result=null;renderStage();
  const p=state.studySettings;
  try{s.question=await api('/exercises/next/?'+new URLSearchParams({mode:p.mode,scope:p.scope,tag:p.tag,reading:p.reading,exclude:s.seen.join(',')}));renderStage();}
  catch(e){if(s.done){s.finished=true;renderStage();toast(e.message,true);}else{state.study=null;renderStage();throw e;}}
}
async function answerQuiz(value){
  const s=state.study;if(!s||!s.question||s.result||s.busy)return;
  if(!String(value).trim())throw new Error('Hãy nhập đáp án.');
  s.busy=true;const q=s.question;
  // Disable controls without re-rendering a typed answer while the request is pending.
  $$('.option,#typing-form button').forEach(b=>b.disabled=true);
  try{s.result=await api('/exercises/'+q.id+'/answer/',{method:'POST',data:{answer:value}});s.done++;if(s.result.correct)s.correct++;s.seen.push(q.word_id);await refreshBoot();}
  finally{s.busy=false;renderStage();}
}
function toeicModeCard(mode,items){
  const meta=mode==='parts-5-6'?{number:'01',title:'Ngữ pháp & từ vựng',parts:'Part 5–6',desc:'Củng cố dạng từ, giới từ, liên từ và hoàn thành văn bản.'}:{number:'02',title:'Đọc hiểu',parts:'Part 7',desc:'Đọc email, thông báo, bài đơn và bài kép trong ngữ cảnh công việc.'};
  return `<section class="toeic-mode panel"><div class="toeic-mode-number">${meta.number}</div><span class="eyebrow">${meta.parts}</span><h2>${meta.title}</h2><p>${meta.desc}</p><div class="toeic-set-list">${items.map(item=>`<article><div><strong>${esc(item.title)}</strong><span>${esc(item.level)} · ${item.question_count} câu · ${item.duration_minutes} phút</span>${item.attempt_count?`<small>Đã làm ${item.attempt_count} lượt · tốt nhất ${item.best_score}/${item.question_count}</small>`:'<small>Chưa làm lần nào</small>'}</div><a class="btn small primary" href="#toeic-set/${esc(item.slug)}">${item.attempt_count?'Luyện lại':'Bắt đầu'} →</a></article>`).join('')}</div></section>`;
}
async function toeicPage(epoch,part=''){
  const data=await api('/toeic/');if(epoch!==state.routeEpoch)return;
  $('#main').innerHTML=heading('Thư viện TOEIC Reading','Chọn Part, chủ đề và thời gian. Làm bài, đối chiếu bằng chứng rồi lưu từ để ôn.')+
    `<div class="practice-entry">${[[5,'Ngữ pháp & từ vựng'],[6,'Hoàn thành văn bản'],[7,'Đọc hiểu văn bản']].map(([p,t])=>`<a href="#toeic/${p}"><strong>Part ${p}</strong><span>${t}</span></a>`).join('')}</div><div class="guide-shortcut"><p><b>Chưa chắc cách làm?</b><br>Có hướng dẫn từng Part, ví dụ nhỏ để thử và những bẫy thường gặp.</p><a class="btn secondary" href="#guides/toeic">Mở cẩm nang →</a></div><div data-toeic-library></div><div class="catalog-note"><b>Bài luyện kỹ năng tự biên soạn</b><span>Không phải đề ETS chính thức hoặc bài thi thử đầy đủ; không quy đổi điểm TOEIC. TOEIC Reading chính thức có 100 câu trong 75 phút.</span><a class="link-btn" href="#resources/toeic">Tài liệu chính thức từ ETS ↗</a></div>`;
  window.LexiHub.toeicCatalog($('[data-toeic-library]'),data.items,part);
}
function renderToeicSet(){renderToeicPractice();}
async function toeicSetPage(slug,epoch){
  const practice=await api('/toeic/'+encodeURIComponent(slug)+'/');if(epoch!==state.routeEpoch)return;
  state.toeicSet=practice;
  if(state.toeicSession?.slug!==slug||state.toeicSession?.revision!==practice.revision)state.toeicSession={slug,revision:practice.revision,answers:{},token:uid(),startedAt:Date.now(),result:null};
  renderToeicSet();
}
const analyticsPageLabels={learn:'Lộ trình học',grammar:'Ngữ pháp',collection:'Bộ từ theo trình độ',home:'Tổng quan',catalog:'Thư viện',ielts:'IELTS',resources:'Đề mẫu chính thức',guides:'Cẩm nang cách làm',lesson:'Bài thư viện',toeic:'TOEIC',
  'toeic-set':'Bộ TOEIC',readings:'Bài cá nhân',reading:'Đang đọc',vocabulary:'Kho từ','word-import':'Tạo bộ từ',study:'Ôn từ',settings:'Cài đặt',analytics:'Thống kê',login:'Đăng nhập'};
async function analyticsPage(epoch){
  const data=await api('/analytics/?days='+state.analyticsDays);if(epoch!==state.routeEpoch)return;
  const maxViews=Math.max(1,...data.series.map(day=>day.views));
  $('#main').innerHTML=heading('Thống kê truy cập','Số liệu first-party để theo dõi mức sử dụng thật, chỉ quản trị viên nhìn thấy.',
    `<select id="analytics-days" aria-label="Khoảng thống kê">${[7,30,90].map(days=>`<option value="${days}" ${data.days===days?'selected':''}>${days} ngày</option>`).join('')}</select><button class="btn secondary" data-action="reload-analytics">Cập nhật</button>`)+
    `<section class="stats">${[[data.totals.views,'Lượt xem','Tổng lượt chuyển trang'],[data.totals.visitors,'Khách duy nhất','Ước lượng theo phiên đã băm'],[data.totals.active_users,'Tài khoản hoạt động','Đã đăng nhập trong kỳ'],[Math.round(data.totals.views/Math.max(1,data.totals.visitors)),'Lượt / khách','Mức tương tác trung bình']].map(([n,l,h])=>`<div class="stat"><div class="stat-top">${l}</div><div class="stat-value">${count(n)}</div><div class="stat-note">${h}</div></div>`).join('')}</section>`+
    `<section class="panel analytics-panel"><div class="section-title"><div><h2>Hoạt động theo ngày</h2><p>Mỗi cột là tổng lượt xem; số bên dưới là khách duy nhất.</p></div></div><div class="traffic-chart">${data.series.map((day,index)=>`<div class="traffic-day" title="${esc(day.date)} · ${day.views} lượt xem · ${day.visitors} khách"><span>${day.views||''}</span><div style="height:${Math.max(3,Math.round(day.views/maxViews*150))}px"></div><small>${data.days<=30||index%7===0?esc(day.date.slice(5)):''}</small><b>${day.visitors}</b></div>`).join('')}</div></section>`+
    `<div class="grid-2 analytics-bottom"><section class="panel"><h2>Trang được xem nhiều</h2>${data.top_pages.length?`<div class="analytics-list">${data.top_pages.map(row=>`<div><span>${esc(analyticsPageLabels[row.page]||row.page)}</span><strong>${row.views}</strong></div>`).join('')}</div>`:empty('Chưa có lượt xem','Dữ liệu sẽ xuất hiện khi có người sử dụng website.')}</section><section class="panel"><h2>Dùng số liệu để tạo động lực</h2><p>Ưu tiên chỉ số có ích: ngày học đều, số lượt ôn, bài hoàn thành và tiến bộ TOEIC. Không hiển thị số giả hoặc tạo bảng xếp hạng công khai khi chưa có sự đồng ý.</p><div class="notice">${esc(data.privacy_note)}</div></section></div>`;
}
function trackVisit(page){
  if(page==='home')return;
  const allowed=analyticsPageLabels[page]?page:'home',now=Date.now();
  if(state.lastTracked?.page===allowed&&now-state.lastTracked.at<30000)return;
  state.lastTracked={page:allowed,at:now};
  api('/activity/visit/',{method:'POST',data:{page:allowed}}).catch(error=>console.warn('Không ghi được thống kê:',error.message));
}
function settingsPage(){
  const b=state.boot;
  $('#main').innerHTML=heading('Cài đặt & tài khoản','Quản lý thông tin cá nhân và giữ một bản sao dữ liệu học của bạn.')+
  `<div class="settings-grid"><section class="panel"><span class="eyebrow">TÀI KHOẢN CỦA BẠN</span><h2>${esc(b.user)}</h2><p>Chỉnh sửa tên, email khôi phục và bảo vệ tài khoản bằng mật khẩu riêng.</p>${window.LEXIREAD_PREVIEW?'<p class="notice">Bản xem trước chưa kết nối tài khoản thật.</p>':'<div class="button-row"><a class="btn primary" href="/account/">Chỉnh sửa thông tin</a><a class="btn" href="/account/password/">Đổi mật khẩu</a></div>'}<p class="fineprint">Đổi ngôn ngữ giao diện ở menu phía trên. Nội dung bài học tiếng Anh và giải nghĩa tiếng Việt được giữ nguyên.</p></section>
  <section class="panel"><h2>Sao lưu dữ liệu học</h2><p>Tải bản sao bài đọc, kho từ và tiến độ để lưu giữ hoặc chuyển tài khoản. Tệp sao lưu không chứa mật khẩu.</p><div class="button-row"><button class="btn primary" data-action="export-backup">↓ Sao lưu đầy đủ</button><button class="btn" data-action="export-csv">↓ Xuất danh sách từ</button></div><label>Chọn tệp sao lưu hoặc danh sách từ<input type="file" id="import-file" accept=".json,.csv"></label><button class="btn secondary" data-action="import-library">Nhập vào kho</button><p class="fineprint">Tệp tối đa 8 MB. Dữ liệu được gộp, không xóa thẻ hay đặt lại tiến độ đang có. Không chia sẻ tệp nếu có bài đọc riêng tư.</p></section>
  <section class="panel"><h2>Trợ giúp khi học</h2><p>${b.ai_enabled?'Trợ lý học tập đang sẵn sàng. Bạn sẽ được hỏi trước khi gửi bài đọc hoặc câu hỏi để phân tích.':'Bạn có thể học bài có sẵn, làm câu hỏi và ôn từ mà không cần trợ lý AI. Trợ lý hiện chưa được bật.'}</p><p>Gợi ý có thể chưa chính xác. Bạn luôn có thể sửa nghĩa, cấu trúc và ví dụ trong kho từ.</p></section>
  <section class="panel"><h2>Quyền riêng tư</h2><p>${window.LEXIREAD_PREVIEW?'Bản xem trước lưu dữ liệu trong trình duyệt hiện tại.':'Bài học và từ vựng riêng được lưu theo tài khoản. Hệ thống ghi nhận lượt truy cập và tiến độ để hiển thị hoạt động học; không công khai kho từ của bạn.'}</p><p>Khi bạn đồng ý dùng trợ lý, nội dung được chọn sẽ được gửi tới dịch vụ xử lý AI. Không đưa thông tin nhạy cảm vào nội dung gửi đi.</p></section></div>`;
}

function download(name,data,type='application/json'){
  const blob=new Blob([typeof data==='string'?data:JSON.stringify(data,null,2)],{type:type+';charset=utf-8'});
  const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
async function route(){
  const epoch=++state.routeEpoch;clearSelection();pausePracticeClock();
  $('.sidebar')?.classList.remove('menu-open');$('.mobile-menu-toggle')?.setAttribute('aria-expanded','false');
  const hash=(location.hash||'#home').slice(1),[page,id]=hash.split('/');
  const nav=['learn','grammar','collection'].includes(page)?'learn':page==='lesson'?'catalog':page==='reading'?'readings':page==='toeic-set'?'toeic':page==='word-import'?'vocabulary':page;
  $$('[data-nav]').forEach(a=>a.classList.toggle('active',a.dataset.nav===nav));
  $('#page-label').textContent=({learn:({plan:'Lộ trình học',grammar:'Học ngữ pháp',verbs:'Động từ bất quy tắc',tenses:'Các thì trong tiếng Anh',vocabulary:'Từ vựng theo chủ đề',dictionary:'Từ điển',sources:'Tài liệu tham khảo'})[id]||'Lộ trình học',grammar:'Ngữ pháp',collection:'Từ vựng theo chủ đề',home:'Tổng quan',catalog:'Thư viện luyện đọc',ielts:'Luyện IELTS Reading',lesson:'Đang mở bài',toeic:'Luyện TOEIC Reading','toeic-set':'Bộ luyện TOEIC',readings:'Bài đọc của tôi',reading:'Đang đọc',vocabulary:'Kho từ của tôi',study:'Luyện nhớ từ',analytics:'Thống kê truy cập',settings:'Cài đặt & dữ liệu'})[page]||'Tổng quan';
  try{
    if(!state.boot)await refreshBoot();
    if(page==='learn'){await window.LexiAcademy.page($('#main'),id||'plan',epoch);}
    else if((page==='grammar'||page==='collection')&&id){await window.LexiAcademy.detail($('#main'),page==='grammar'?'grammar':'vocabulary',id,epoch);}
    else if(page==='reading'&&id)await readerPage(id,epoch);
    else if(page==='catalog')await catalogPage(epoch);
    else if(page==='ielts')await ieltsPage(epoch,id||'');
    else if(page==='lesson'&&id)await lessonRoute(id,epoch);
    else if(page==='toeic')await toeicPage(epoch,id||'');
    else if(page==='guides'){window.LexiHub.guidePage($('#main'),id||'');$('#page-label').textContent=id==='youtube'?'Học qua YouTube':'Cẩm nang học tập';}
    else if(page==='resources'){
      $('#main').innerHTML='<section id="study-resources"></section>';
      window.LexiResources.mount($('#study-resources'),id);
      $('#page-label').textContent='Đề mẫu chính thức';
    }
    else if(page==='toeic-set'&&id)await toeicSetPage(id,epoch);
    else if(page==='readings')await readingsPage(epoch);
    else if(page==='vocabulary')await vocabPage(epoch);
    else if(page==='word-import'){window.LexiDecks.page($('#main'));$('#page-label').textContent='Tạo bộ từ của bạn';}
    else if(page==='study')renderStudy();
    else if(page==='analytics')await analyticsPage(epoch);
    else if(page==='settings')settingsPage();
    else await homePage(epoch);
    if(epoch===state.routeEpoch){
      if(state.lastRenderedRoute!==hash){
        window.scrollTo({top:0,behavior:'instant'});
        $('#main').focus({preventScroll:true});
        state.lastRenderedRoute=hash;
      }
      trackVisit(page);
    }
  }catch(e){if(epoch===state.routeEpoch){$('#main').innerHTML=empty('Chưa tải được dữ liệu',e.message,'<button class="btn primary" data-action="retry">Thử lại</button>');}toast(e.message,true);}
}
async function act(button){
  if(await platformAct(button))return;
  const action=button.dataset.action;
  switch(action){
  case 'skip-content':$('#main').focus();break;
  case 'retry':await refreshBoot();await route();break;
  case 'close-modal':closeModal();break;
  case 'new-reading':readingModal();break;
  case 'edit-reading':readingModal(true);break;
  case 'save-reading':await saveReading(button);break;
  case 'delete-reading':if(confirm('Xóa bài “'+state.reading.title+'”? Các thẻ đã lưu vẫn được giữ.'))await busy(button,async()=>{await api('/readings/'+state.reading.id+'/',{method:'DELETE'});await refreshBoot();location.hash='readings';toast('Đã xóa bài đọc.');});break;
  case 'filter-readings':state.readingFilters={q:$('#reading-search').value.trim(),status:$('#reading-status').value,favorite:$('#reading-favorite').value,sort:$('#reading-sort').value,page:1};await route();break;
  case 'readings-prev':state.readingFilters.page=Math.max(1,state.readingFilters.page-1);await route();break;
  case 'readings-next':state.readingFilters.page++;await route();break;
  case 'toggle-reading-favorite':await busy(button,async()=>{
    const id=button.dataset.id||state.reading?.id,current=button.dataset.favorite==='true',result=await api('/readings/'+id+'/progress/',{method:'POST',data:{favorite:!current}});
    const favorite=result.progress?.favorite ?? !current;
    if(state.reading?.id===id)state.reading={...state.reading,favorite,progress:result.progress||state.reading.progress};
    if(location.hash==='#readings')await route();else if(state.reading?.id===id)renderReader();
    toast(favorite?'Đã thêm vào bài yêu thích.':'Đã bỏ khỏi bài yêu thích.');
  });break;
  case 'reader-tab':state.readingTab=button.dataset.tab;renderReader();break;
  case 'reading-prompt':await busy(button,async()=>{const r=await api('/prompts/',{method:'POST',data:{task:'reading',reading_id:state.reading.id}});showPrompt(r.prompt,'reading');});break;
  case 'analyse-reading':if(cloudConsent('Toàn bộ bài “'+state.reading.title+'”'))await busy(button,async()=>{await api('/readings/'+state.reading.id+'/analyse/',{method:'POST',data:{allow_cloud:true}});await refreshBoot();await route();toast('Đã lưu bản dịch. Mở “Từ gợi ý” để chọn từ học.');},'AI đang phân tích…');break;
  case 'save-candidates':{
    const selected=$$('.candidate-check:checked').map(c=>Number(c.value));if(!selected.length)throw new Error('Chọn ít nhất một mục muốn học.');
    await busy(button,async()=>{const items=selected.map(i=>({...state.reading.analysis.vocabulary[i],tags:[...new Set([...(state.reading.analysis.vocabulary[i].tags||[]),state.reading.title])],verified:false,origin:state.reading.catalog_slug?'curated':'ai'}));const r=await api('/vocabulary/',{method:'POST',data:{items,reading_id:state.reading.id}});await refreshBoot();toast(`Đã thêm ${r.created} thẻ; ${r.skipped} mục đã có được giữ nguyên.`);});break;
  }
  case 'new-word':editor(blankEntry());break;
  case 'selected-dictionary':if(state.selection)await window.LexiDictionary.open(state.selection);break;
  case 'selected-word':if(state.selection){const candidate=(state.reading.analysis?.vocabulary||[]).find(w=>w.word.toLowerCase()===state.selection.word.toLowerCase());editor({...blankEntry(),...(candidate||{}),...state.selection});}break;
  case 'clear-selection':clearSelection();break;
  case 'edit-word':editor(state.vocab.find(v=>v.id===button.dataset.id),button.dataset.id);break;
  case 'save-word':await saveWord(button);break;
  case 'delete-word':if(confirm('Xóa thẻ này và lịch sử ôn tương ứng?'))await busy(button,async()=>{await api('/vocabulary/'+state.editId+'/',{method:'DELETE'});closeModal();await refreshBoot();await route();toast('Đã xóa thẻ.');});break;
  case 'lookup-word':state.editing=readEditor();if(!state.editing.word)throw new Error('Nhập từ cần tra.');if(cloudConsent('Từ và đoạn ngữ cảnh đang chọn'))await busy(button,async()=>{const r=await api('/ai/lookup/',{method:'POST',data:{word:state.editing.word,context:state.editing.context,reading_id:state.editing.reading_id,allow_cloud:true}});state.editing={...state.editing,...r,verified:false};editor();},'AI đang tra từ…');break;
  case 'word-prompt':state.editing=readEditor();if(!state.editing.word)throw new Error('Nhập từ cần tra.');await busy(button,async()=>{const r=await api('/prompts/',{method:'POST',data:{task:'word',word:state.editing.word,context:state.editing.context}});showPrompt(r.prompt,'word');});break;
  case 'copy-prompt':{
    const t=$('#prompt-text');try{await navigator.clipboard.writeText(t.value);toast('Đã copy prompt.');}catch(e){t.focus();t.select();toast('Nhấn Ctrl+C để sao chép phần đã chọn.');}break;
  }
  case 'apply-prompt':await applyPrompt(button);break;
  case 'filter-vocab':state.filters={q:$('#vocab-search').value.trim(),tag:$('#vocab-tag').value,reading:$('#vocab-reading').value,scope:$('#vocab-scope').value,sort:$('#vocab-sort').value,page:1};await route();break;
  case 'vocab-prev':state.filters.page=Math.max(1,state.filters.page-1);await route();break;
  case 'vocab-next':state.filters.page++;await route();break;
  case 'bulk-open':bulkModal();break;
  case 'study-deck':state.study=null;state.studySettings={...state.studySettings,tag:state.filters.tag,reading:'',scope:'all'};location.hash='study';break;
  case 'export-deck':await busy(button,async()=>download('lexiread-vocabulary.json',await api('/vocabulary/deck/?name='+encodeURIComponent(state.filters.tag))));break;
  case 'bulk-prompt':{const text=$('#bulk-text').value.trim();if(!text)throw new Error('Dán danh sách từ trước.');await busy(button,async()=>{const r=await api('/prompts/',{method:'POST',data:{task:'words',text}});showPrompt(r.prompt,'words');});break;}
  case 'bulk-ai':{const text=$('#bulk-text').value.trim();if(!text)throw new Error('Dán danh sách từ trước.');if(cloudConsent('Danh sách từ bạn vừa nhập'))await busy(button,async()=>{const r=await api('/ai/words/',{method:'POST',data:{text,allow_cloud:true}});await refreshBoot();previewBulk(r.vocabulary);},'AI đang tạo gợi ý…');break;}
  case 'bulk-parse':{
    const lines=$('#bulk-text').value.trim().split('\n').filter(l=>l.trim());
    const items=lines.map((line,i)=>{const [word,meaning_vi,synonyms='']=line.split('|').map(s=>s.trim());if(!word||!meaning_vi)throw new Error(`Dòng ${i+1} chưa có nghĩa. Dùng word | nghĩa Việt, hoặc nhờ AI điền.`);return {...blankEntry(),word,meaning_vi,synonyms:synonyms.split(';').map(x=>x.trim()).filter(Boolean),tags:['Từ cá nhân']};});previewBulk(items);break;
  }
  case 'bulk-save':{
    const items=$$('.bulk-check:checked').map(c=>{const i=Number(c.value);return {...state.bulk[i],word:$('#bulk-word-'+i).value.trim(),meaning_vi:$('#bulk-meaning-'+i).value.trim()};});if(!items.length)throw new Error('Chưa chọn mục nào.');
    await busy(button,async()=>{const r=await api('/vocabulary/',{method:'POST',data:{items}});closeModal();await refreshBoot();if(location.hash==='#vocabulary')await route();else location.hash='vocabulary';toast(`Đã thêm ${r.created} thẻ; bỏ qua ${r.skipped} mục trùng.`);});break;
  }
  case 'start-study':await startStudy(button);break;
  case 'flip-card':if(state.study?.mode==='flashcard'&&!state.study.busy){state.study.flipped=!state.study.flipped;renderStage();}break;
  case 'rate-card':await rateCard(button.dataset.rating);break;
  case 'answer-quiz':await answerQuiz(state.study.question.options[Number(button.dataset.index)]);break;
  case 'next-quiz':await busy(button,loadNextQuiz);break;
  case 'submit-toeic':{
    const session=state.toeicSession,missing=state.toeicSet.questions.filter(q=>!hasPracticeAnswer(session,q));
    if(missing.length){jumpPracticeQuestion(missing[0].id);throw new Error(`Bạn còn ${missing.length} câu chưa trả lời. Đã chuyển đến câu đầu tiên còn trống.`);}
    await busy(button,async()=>{session.result=await api('/toeic/'+encodeURIComponent(session.slug)+'/submit/',{method:'POST',data:{token:session.token,revision:state.toeicSet.revision,answers:session.answers,duration_seconds:Math.min(7200,Math.max(0,Math.round(practiceElapsed(session)/1000)))}});renderToeicSet();window.scrollTo({top:0,behavior:'smooth'});},'Đang chấm…');break;
  }
  case 'reset-toeic':state.toeicSession={slug:state.toeicSet.slug,revision:state.toeicSet.revision,answers:{},token:uid(),startedAt:Date.now(),result:null};renderToeicSet();window.scrollTo({top:0,behavior:'smooth'});break;
  case 'save-toeic-words':await busy(button,async()=>{const items=state.toeicSet.focus_vocabulary.map(word=>({...word,source_label:'TOEIC · '+state.toeicSet.title,tags:[...new Set([...(word.tags||[]),'TOEIC',state.toeicSet.title])]}));const result=await api('/vocabulary/',{method:'POST',data:{items}});await refreshBoot();toast(`Đã thêm ${result.created} từ; ${result.skipped} từ đã có được giữ nguyên.`);});break;
  case 'reload-analytics':state.analyticsDays=Number($('#analytics-days').value);await analyticsPage(++state.routeEpoch);break;
  case 'export-backup':await busy(button,async()=>download('lexiread-backup-'+new Date().toISOString().slice(0,10)+'.json',await api('/backup/')));break;
  case 'export-csv':await busy(button,async()=>download('lexiread-vocabulary.csv',await api('/export.csv'),'text/csv'));break;
  case 'import-library':{
    const file=$('#import-file').files[0];if(!file)throw new Error('Chọn file JSON hoặc CSV trước.');if(!confirm('Gộp dữ liệu từ file vào kho hiện tại? Các thẻ đã có sẽ không bị ghi đè.'))return;
    const data=new FormData();data.append('file',file);await busy(button,async()=>{const r=await api('/restore/',{method:'POST',data});await refreshBoot();settingsPage();toast(`Đã thêm ${r.created} thẻ, ${r.readings_created||0} bài đọc; ${r.skipped} thẻ trùng được giữ nguyên.`);});break;
  }
  }
}
document.addEventListener('click',e=>{const b=e.target.closest('[data-action]');if(!b||b.disabled)return;e.preventDefault();act(b).catch(err=>toast(err.message,true));});
document.addEventListener('change',e=>{
  if(e.target.id==='translation-toggle'){state.translation=e.target.checked;renderReader();}
  if(e.target.id==='select-all-candidates')$$('.candidate-check').forEach(c=>c.checked=e.target.checked);
  if(e.target.dataset.toeicQuestion&&state.toeicSession&&!state.toeicSession.result)state.toeicSession.answers[e.target.dataset.toeicQuestion]=Number(e.target.value);
});
document.addEventListener('submit',e=>{
  if(e.target.id==='typing-form'){e.preventDefault();answerQuiz($('#typing-answer').value).catch(err=>toast(err.message,true));}
  if(['word-form','reading-form'].includes(e.target.id))e.preventDefault();
});
document.addEventListener('mouseup',()=>setTimeout(captureSelection,10));
let selectionDelay;
document.addEventListener('selectionchange',()=>{clearTimeout(selectionDelay);selectionDelay=setTimeout(captureSelection,180);});
document.addEventListener('touchend',()=>setTimeout(captureSelection,40),{passive:true});
document.addEventListener('keyup',e=>{if(e.key==='Shift'||e.key.startsWith('Arrow'))captureSelection();});
document.addEventListener('keydown',e=>{
  if(e.target.id==='vocab-search'&&e.key==='Enter'){e.preventDefault();act($('[data-action=filter-vocab]')).catch(err=>toast(err.message,true));return;}
  if(e.target.id==='reading-search'&&e.key==='Enter'){e.preventDefault();act($('[data-action=filter-readings]')).catch(err=>toast(err.message,true));return;}
  if($('#modal').open||['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName)||!location.hash.startsWith('#study'))return;
  const s=state.study;if(!s||s.finished||s.busy)return;
  if((e.code==='Space'||e.key==='Enter')&&s.mode==='flashcard'&&(e.target===document.body||e.target.closest('.flashcard'))){e.preventDefault();s.flipped=!s.flipped;renderStage();}
  if(s.mode==='flashcard'&&s.flipped&&['1','2','3','4'].includes(e.key)){e.preventDefault();rateCard(['again','hard','good','easy'][Number(e.key)-1]).catch(err=>toast(err.message,true));}
  if(s.mode!=='flashcard'&&!s.result&&s.question&&['a','b','c','d'].includes(e.key.toLowerCase())){const answer=s.question.options['abcd'.indexOf(e.key.toLowerCase())];if(answer)answerQuiz(answer).catch(err=>toast(err.message,true));}
});
window.addEventListener('hashchange',route);
window.addEventListener('unhandledrejection',e=>{console.error(e.reason);toast('Có lỗi chưa xử lý. Tải lại trang và kiểm tra log.',true);});
route();
