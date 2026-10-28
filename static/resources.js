'use strict';
/* Official resource links only: no third-party exam content is copied or embedded. */
(() => {
  const html = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const safeURL = value => { try { const u = new URL(value); return u.protocol === 'https:' ? u.href : ''; } catch { return ''; } };
  const copy = {
    vi: {eyebrow:'TỪ NGUỒN CHÍNH THỨC',title:'Một góc luyện thi, rộng hơn.',intro:'Khám phá bài mẫu IELTS và TOEIC công khai từ đơn vị tổ chức thi. Mở đề và đáp án tại nguồn; tiến độ làm bài ở trang ngoài không được lưu vào Lexivela.',all:'Tất cả',search:'Tìm đơn vị, dạng câu hỏi hoặc bài mẫu…',searchLabel:'Tìm tài liệu chính thức',format:'Mọi định dạng',open:'Mở bài mẫu',answers:'Đáp án',source:'Trang nguồn',checked:'Kiểm tra',more:'Xem thêm tài liệu',empty:'Chưa tìm thấy tài liệu phù hợp. Thử từ khóa khác nhé.',count:'tài liệu',note:'Các liên kết gồm bài tập, bộ mẫu và trang hướng dẫn; số tài liệu không phải số đề thi đầy đủ.',reset:'Xóa bộ lọc'},
    en: {eyebrow:'OFFICIAL SOURCES',title:'A little more room to practise.',intro:'Explore public IELTS and TOEIC samples from test providers. Open tasks and answers at the source; work on external sites is not saved to Lexivela.',all:'All',search:'Search provider, question type or sample…',searchLabel:'Search official resources',format:'All formats',open:'Open sample',answers:'Answers',source:'Source page',checked:'Checked',more:'Show more resources',empty:'No matching resources. Try another search.',count:'resources',note:'Links include exercises, sample sets and guides; the resource count is not a count of full tests.',reset:'Clear filters'},
    fr: {eyebrow:'SOURCES OFFICIELLES',title:'Un peu plus de place pour pratiquer.',intro:'Découvrez les exemples publics IELTS et TOEIC des organismes officiels. Les exercices et corrigés s’ouvrent à la source ; la progression externe n’est pas enregistrée dans Lexivela.',all:'Tous',search:'Organisme, type de question ou exemple…',searchLabel:'Rechercher une ressource officielle',format:'Tous les formats',open:'Ouvrir l’exemple',answers:'Corrigé',source:'Page source',checked:'Vérifié',more:'Voir plus de ressources',empty:'Aucune ressource correspondante. Essayez un autre terme.',count:'ressources',note:'Les liens comprennent des exercices, exemples et guides ; le nombre de ressources ne correspond pas au nombre de tests complets.',reset:'Effacer les filtres'},
    zh: {eyebrow:'官方资源',title:'多一点练习空间。',intro:'探索考试机构公开提供的雅思和托业样题。在来源网站打开题目和答案；外部网站的进度不会保存到 Lexivela。',all:'全部',search:'搜索机构、题型或样题…',searchLabel:'搜索官方资源',format:'所有格式',open:'打开样题',answers:'答案',source:'来源页面',checked:'已检查',more:'显示更多资源',empty:'没有匹配的资源，请尝试其他关键词。',count:'份资源',note:'链接包括练习、样题集和指南；资源数量不代表完整试卷的数量。',reset:'清除筛选'}
  };
  const formats = {
    vi: {pdf:'PDF',interactive:'Tương tác',collection:'Bộ tài liệu'},
    en: {pdf:'PDF',interactive:'Interactive',collection:'Collection'},
    fr: {pdf:'PDF',interactive:'Interactif',collection:'Collection'},
    zh: {pdf:'PDF',interactive:'互动练习',collection:'资源合集'}
  };
  const verificationLabels = {
    vi: {publisher_page_checked:'Nguồn đã kiểm tra',target_checked:'Liên kết đã kiểm tra'},
    en: {publisher_page_checked:'Source page checked',target_checked:'Link checked'},
    fr: {publisher_page_checked:'Page source vérifiée',target_checked:'Lien vérifié'},
    zh: {publisher_page_checked:'来源页面已检查',target_checked:'链接已检查'}
  };
  const text = () => copy[window.LexiI18n?.language] || copy.vi;
  const formatLabel = value => (formats[window.LexiI18n?.language] || formats.vi)[value] || value;
  const normalize = value => String(value ?? '').toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d').replaceAll('_',' ');
  const states = new WeakMap();
  function readItems() {
    try { const data=JSON.parse(document.getElementById('official-resources-data')?.textContent || '[]'); return Array.isArray(data) ? data.filter(r=>safeURL(r.url)) : []; } catch { return []; }
  }
  function link(url,label,className='link-btn',context='') {
    const safe=safeURL(url); return safe ? `<a class="${className}" href="${html(safe)}"${context?` aria-label="${html(label+' · '+context)}"`: ""} target="_blank" rel="noopener noreferrer">${html(label)} ↗</a>` : '';
  }
  function card(item) {
    const t=text(), language=window.LexiI18n?.language || 'vi';
    const description=language==='vi' ? item.description_vi : (item.description_en || '');
    const context=item.variant+' · '+item.title,verified=(verificationLabels[language] || verificationLabels.vi)[item.verification] || t.checked;
    return `<article class="resource-card"><div class="resource-card-top"><span class="resource-exam ${item.exam==='toeic'?'toeic':''}">${html(item.exam.toUpperCase())}</span><span>${html(formatLabel(item.format))}</span></div><p class="resource-variant" lang="en">${html(item.variant)}</p><p class="resource-publisher">${html(item.publisher)}</p><h3 lang="en">${html(item.title)}</h3>${description?`<p class="resource-description" lang="${language==='vi'?'vi':'en'}">${html(description)}</p>`:''}<div class="resource-types" lang="en">${(item.question_types || []).slice(0,3).map(x=>`<span>${html(x.replaceAll('_',' '))}</span>`).join('')}</div><div class="resource-actions">${link(item.url,t.open,'btn small secondary',context)}${item.answer_url?link(item.answer_url,t.answers,'link-btn',context):''}</div><div class="resource-provenance">${link(item.source_url,t.source,'link-btn',item.publisher+' · '+context)}<span>${html(verified)} <time datetime="${html(item.last_checked)}">${html(item.last_checked)}</time></span></div></article>`;
  }
  function update(root,focusMore=false) {
    const s=states.get(root),t=text(),q=normalize(s.q).trim();
    const items=s.items.filter(r=>(!s.exam || r.exam===s.exam)&&(!s.format || r.format===s.format)&&(!q || normalize([r.title,r.publisher,r.exam,r.variant,r.description_vi,r.description_en,...(r.question_types||[])].join(' ')).includes(q)));
    const shown=items.slice(0,s.limit),previous=root.querySelectorAll('.resource-card').length;
    root.querySelector('[data-resource-results]').innerHTML=shown.length?shown.map(card).join(''):`<p class="empty-state">${t.empty}</p>`;
    root.querySelector('[data-resource-count]').textContent=`${items.length} ${t.count}`;
    root.querySelector('[data-resource-more]').hidden=items.length<=shown.length;
    root.querySelector('[data-resource-reset]').hidden=!(s.q || s.exam || s.format);
    root.querySelectorAll('[data-resource-exam]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.resourceExam===s.exam)));
    if(focusMore)root.querySelectorAll('.resource-card')[previous]?.querySelector('a')?.focus();
  }
  function mount(root,exam='',existing=null) {
    if(!root)return;
    const t=text(),s=existing || {items:readItems(),exam:['ielts','toeic'].includes(exam)?exam:'',format:'',q:'',limit:6};
    states.set(root,s);root.dataset.noI18n='';root.classList.add('official-resources');
    const titleTag=root.closest('#main')?'h1':'h2';
    root.innerHTML=`<div class="section-title"><div><span class="eyebrow">${t.eyebrow}</span><${titleTag}>${t.title}</${titleTag}><p>${t.intro}</p></div><span class="resource-bookmark" aria-hidden="true">↗</span></div><div class="resource-controls"><div class="filter-chips" role="group" aria-label="IELTS / TOEIC">${[['',t.all],['ielts','IELTS'],['toeic','TOEIC']].map(([v,l])=>`<button type="button" class="filter-chip" data-resource-exam="${v}" aria-pressed="${s.exam===v}">${l}</button>`).join('')}</div><label class="resource-search"><span class="sr-only">${t.searchLabel}</span><input type="search" data-resource-search placeholder="${t.search}" value="${html(s.q)}"></label><select data-resource-format aria-label="${t.format}"><option value="">${t.format}</option>${[...new Set(s.items.map(r=>r.format))].sort().map(v=>`<option value="${html(v)}" ${v===s.format?'selected':''}>${html(formatLabel(v))}</option>`).join('')}</select></div><div class="resource-result-line"><span role="status" data-resource-count></span><button class="link-btn" type="button" data-resource-reset>${t.reset}</button></div><div class="resource-grid" data-resource-results></div><div class="show-more-row"><button type="button" class="btn" data-resource-more>${t.more} ↓</button></div><p class="resource-note">${t.note}</p>`;
    update(root);
  }
  document.addEventListener('input',e=>{if(!e.target.matches('[data-resource-search]'))return;const root=e.target.closest('.official-resources'),s=states.get(root);s.q=e.target.value;s.limit=6;update(root);});
  document.addEventListener('change',e=>{if(!e.target.matches('[data-resource-format]'))return;const root=e.target.closest('.official-resources'),s=states.get(root);s.format=e.target.value;s.limit=6;update(root);});
  document.addEventListener('click',e=>{const b=e.target.closest('[data-resource-exam],[data-resource-more],[data-resource-reset]');if(!b)return;const root=b.closest('.official-resources'),s=states.get(root);if(b.hasAttribute('data-resource-exam')){s.exam=b.dataset.resourceExam;s.limit=6;}else if(b.hasAttribute('data-resource-reset')){mount(root);root.querySelector('[data-resource-search]').focus();return;}else s.limit+=6;update(root,b.hasAttribute('data-resource-more'));});
  document.addEventListener('lexiread:language',()=>document.querySelectorAll('.official-resources').forEach(root=>mount(root,'',states.get(root))));
  document.addEventListener('DOMContentLoaded',()=>document.querySelectorAll('[data-official-resources]').forEach(root=>mount(root)));
  window.LexiResources={mount};
})();
