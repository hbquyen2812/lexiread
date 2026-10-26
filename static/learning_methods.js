'use strict';
(() => {
  const methods = [
    {id:'recall', title:'Tự nhớ lại trước khi xem đáp án', short:'Thử nói hoặc viết câu trả lời, rồi mới mở lời giải.',
      why:'Tự trả lời trước khi xem lại bài giúp bạn nhớ kiến thức lâu hơn và biết phần nào cần ôn thêm.',
      steps:['Đọc một đoạn ngắn, rồi nhìn sang chỗ khác và kể lại ý chính bằng lời của bạn.','Khi ôn thẻ, thử nhớ nghĩa và một câu ví dụ trước khi lật. Sau đó kiểm tra, sửa chỗ còn thiếu.'],
      example:'Với “appointment”, thử nói nghĩa và đặt câu: “I have an appointment at ten.” Bạn chưa nhớ được thì xem lại, rồi thử thêm một lần.',
      route:'study', action:'Thử với thẻ từ', source:'https://www.retrievalpractice.org/why-it-works', sourceName:'Retrieval Practice · Tự nhớ lại'},
    {id:'spacing', title:'Ôn cách quãng, mỗi lần một ít', short:'Quay lại kiến thức cũ sau một khoảng nghỉ.',
      why:'Chia việc ôn thành nhiều buổi giúp nhớ kiến thức lâu hơn so với dồn tất cả vào một lần.',
      steps:['Mở mục Luyện nhớ từ và ưu tiên từ đến hạn trước khi thêm từ mới.','Chọn mức độ bạn nhớ từ để điều chỉnh lịch ôn. Nếu chưa nhớ, xem lại nghĩa và ví dụ trước khi tiếp tục.'],
      example:'Bạn học “appointment” hôm nay. Lần sau, thử nhớ lại khi thẻ đến hạn thay vì mở đáp án liên tục trong cùng một buổi.',
      route:'study', action:'Ôn từ đến hạn', source:'https://www.retrievalpractice.org/spacing', sourceName:'Retrieval Practice · Ôn cách quãng'},
    {id:'feedback', title:'Hiểu vì sao sai, rồi làm lại', short:'Xem lời giải, tìm chỗ nhầm và thử một câu tương tự.',
      why:'Lời giải giúp bạn hiểu vì sao mình sai và biết cách sửa.',
      steps:['Sau khi nộp bài, chọn một câu sai và tìm bằng chứng hoặc quy tắc dẫn đến đáp án.','Tự giải thích bằng một câu ngắn. Ở buổi sau, làm lại hoặc thử một câu cùng dạng để kiểm tra mình đã hiểu.'],
      example:'Nhầm “since” và “for”? Ghi lại: “since + mốc bắt đầu”, “for + khoảng thời gian”, rồi tự đặt hai câu mới.',
      route:'learn/grammar', action:'Luyện ngữ pháp', source:'https://www.retrievalpractice.org/faq', sourceName:'Retrieval Practice · Vai trò của phản hồi'}
  ];
  const levels = {
    'A1–A2':'Chọn đoạn ngắn, lưu 3–5 từ thông dụng và thử kể ý chính bằng một câu. Có thể mở bản dịch sau khi tự đọc.',
    'B1–B2':'Tóm tắt đoạn bằng 2–3 câu, lưu cả cụm từ và giải thích vì sao đáp án đúng. Thử dùng cụm mới trong câu của bạn.',
    'C1–C2':'Chú ý lập luận, hàm ý và sắc thái từ. So sánh hai cách diễn đạt, rồi tự giải thích chúng khác nhau thế nào.'
  };
  const practiceHref = (route, isPublic) => isPublic ? '/login/?next='+encodeURIComponent('/#'+route) : '#'+route;
  function teaser(isPublic=false) {
    return `<aside class="method-note" lang="vi" data-no-i18n><div><strong>Nhớ lâu hơn, học nhẹ hơn.</strong><p>Tự nhớ lại · Hiểu vì sao sai · Ôn đúng lúc</p></div><a class="link-btn" href="${isPublic?'/guides/':''}#guides/methods">Xem cách học →</a></aside>`;
  }
  function community(data) {
    if (!data || !['active_learners','practice_attempts','word_reviews'].every(key=>Number.isSafeInteger(data[key])&&data[key]>=0)) return '';
    const metrics=[['active_learners','Tài khoản đã học'],['practice_attempts','Bài luyện đã làm'],['word_reviews','Lượt ôn từ']];
    return `<section class="community-summary" aria-label="Hoạt động học tập" lang="vi" data-no-i18n><header><h2>${data.is_demo?'Hoạt động bản thử nghiệm':'Cùng nhau học mỗi ngày'}</h2><span>30 ngày gần đây</span></header><dl class="community-metrics">${metrics.map(([key,label])=>`<div><dt>${label}</dt><dd>${data[key].toLocaleString('vi-VN')}</dd></div>`).join('')}</dl><details><summary>Cách tính số liệu</summary><p>Mỗi tài khoản có hoạt động học được tính một lần trong 30 ngày. Bài luyện là các lần nộp bài đọc, TOEIC, ngữ pháp và từ vựng; mỗi lần ôn một thẻ là một lượt ôn. Không tính tài khoản quản trị và tài khoản kiểm thử nội bộ. Số liệu tổng hợp từ hoạt động còn lưu trên hệ thống, không công khai danh tính.</p>${data.is_demo?'<p>Đây là dữ liệu của bản thử nghiệm, không phải số người dùng chính thức.</p>':''}</details></section>`;
  }
  function page(root) {
    const isPublic=!!document.querySelector('[data-guide-public]');
    root.classList.add('learning-hub');
    root.innerHTML=`${window.LexiChannels?.tabs('methods')||''}<article class="methods-page" lang="vi" data-no-i18n><header class="hub-heading"><span class="eyebrow">MỘT CHÚT MỖI NGÀY</span><h1>Học sao cho nhớ lâu?</h1><p>Thử ba cách học dưới đây với bài đọc và bộ từ của bạn.</p></header><div class="method-cards">${methods.map((m,i)=>`<section class="method-card"><span class="method-number" aria-hidden="true">0${i+1}</span><h2>${m.title}</h2><p>${m.short}</p><details><summary>Cách áp dụng</summary><p>${m.why}</p><ol>${m.steps.map(s=>`<li>${s}</li>`).join('')}</ol><p class="method-example">${m.example}</p><a class="link-btn" href="${m.source}" target="_blank" rel="noopener noreferrer">${m.sourceName} ↗</a></details><a class="btn secondary" href="${practiceHref(m.route,isPublic)}">${m.action} →</a></section>`).join('')}</div><section class="method-level"><div><h2>Bắt đầu vừa sức</h2><label>Trình độ của bạn <select data-method-level>${Object.keys(levels).map(l=>`<option>${l}</option>`).join('')}</select></label></div><p data-method-hint aria-live="polite">${levels['A1–A2']}</p></section><section class="method-routine"><div><h2>Thử một buổi 15 phút</h2><p>3 phút ôn từ cũ → 9 phút học một phần nhỏ → 3 phút tự nhắc lại kiến thức và xem lời giải.</p><small>Đây là gợi ý của LexiRead. Bạn có thể đổi thời lượng cho phù hợp.</small></div><a class="btn primary" href="${practiceHref('learn/plan',isPublic)}">Mở lộ trình của tôi →</a></section></article>`;
  }
  document.addEventListener('change',e=>{
    if(!e.target.matches('[data-method-level]'))return;
    const hint=e.target.closest('.method-level').querySelector('[data-method-hint]');
    hint.textContent=levels[e.target.value]||levels['A1–A2'];
  });
  window.LexiMethods={page,teaser,community};
})();
