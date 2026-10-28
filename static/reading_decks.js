/* One click from a reading to its saved flashcards. Extraction runs on the server, without AI. */
(() => {
  'use strict';
  let pending = null;
  const endpoint = id => '/readings/' + encodeURIComponent(id) + '/vocabulary-deck/';
  const active = () => /^#study\/[^/]+$/.test(location.hash) && !!state.study?.readingId;
  const current = (id, epoch) => state.routeEpoch === epoch && state.reading?.id === id;

  function session(data) {
    const id = data.reading.id;
    state.readingSources = [...new Map([...(state.readingSources || []), data.reading].map(r => [r.id, r])).values()];
    state.studySettings = {mode:'flashcard', tag:'', reading:id, scope:'all', limit:data.items.length};
    state.study = {mode:'flashcard', cards:data.items, idx:0, done:0, correct:0, flipped:false, seen:[],
      finished:false, busy:false, token:uid(), question:null, result:null, initialCount:data.items.length,
      retryCount:0, retried:new Set(), lastReview:null, readingId:id, readingTitle:data.reading.title};
  }

  async function create(button) {
    const id = state.reading?.id, epoch = state.routeEpoch;
    if (!id) return;
    await busy(button, async () => {
      const data = await api(endpoint(id), {method:'POST'});
      await refreshBoot();
      if (!current(id, epoch)) return;
      pending = data;
      state.study = null;
      location.hash = 'study/' + id;
    });
  }

  function draw(root, data) {
    root.replaceChildren(window.LexiDOM.fragment(`<section class="reading-deck">
      <a class="text-link" href="#reading/${esc(data.reading.id)}">← Về bài đọc</a>
      <header class="reading-deck-header"><div><span class="eyebrow">Flashcard bài đọc</span>
      <h1 data-no-i18n>${esc(data.reading.title)}</h1></div>
      ${window.LexiVisuals?.scene('recall') || ''}</header>
      ${data.items.length ? '<div class="reading-deck-actions"><button class="btn small" data-reading-deck-words>Xem bộ từ</button></div><div class="study-stage" id="study-stage"></div>' :
      '<div class="notice">Bài này chưa có thẻ. Mở bài đọc rồi chọn “Flashcard bài này”.</div>'}</section>`));
    if (data.items.length) renderStage();
  }

  async function page(root, id, epoch) {
    const data = pending?.reading.id === id ? pending : await api(endpoint(id));
    pending = null;
    if (state.routeEpoch !== epoch) return;
    if (data.items.length && state.study?.readingId !== id) session(data);
    else if (!data.items.length) state.study = null;
    draw(root, data);
  }

  async function restart(button) {
    const id = state.study.readingId, epoch = state.routeEpoch;
    await busy(button, async () => {
      const data = await api(endpoint(id));
      if (state.routeEpoch !== epoch) return;
      if (data.items.length) session(data); else state.study = null;
      draw(document.querySelector('#main'), data);
    });
  }

  document.addEventListener('click', event => {
    if (!event.target.closest('[data-reading-deck-words]') || !active()) return;
    state.filters = {...state.filters, reading:state.study.readingId, tag:'', scope:'all', q:'', page:1};
    location.hash = 'vocabulary';
  });
  function cardBody(word) {
    return `${word.usage_pattern ? `<p class="reading-deck-pattern" lang="en" data-no-i18n>${esc(word.usage_pattern)}</p>` : ''}
      ${word.context ? `<blockquote class="quote" lang="en" data-no-i18n>${esc(word.context)}</blockquote>` : ''}
      ${word.note ? `<p class="muted" data-no-i18n>${esc(word.note)}</p>` : ''}`;
  }
  window.LexiReadingDecks = {create, page, restart, active, cardBody};
})();
