'use strict';
/* Local, reusable art: concrete word objects first; a study-card motif otherwise.
 * User text never becomes an image URL. Abstract words aren't assigned a fake meaning.
 */
(() => {
  const objects = new Set(['book','calendar','clock','coffee','apple','house','plant','laptop','letter','receipt','travel','people','cards','compass','folder','pencil']);
  const themes = new Set(['reading','nature','school','work','travel','city','food','technology']);
  const asset = path => window.LEXI_ART_ASSETS?.[path] || path;
  const meanings = [
    ['book', /^(book|books|notebook|novel|read|reading|library|dictionary)$/],
    ['calendar', /^(calendar|appointment|schedule|reschedule|deadline|date)$/],
    ['clock', /^(clock|time|hour|minute|watch|punctual)$/],
    ['coffee', /^(coffee|tea|cup|mug|cafe|café)$/], ['apple', /^(apple|fruit|snack)$/],
    ['house', /^(house|home|apartment|accommodation)$/], ['plant', /^(plant|leaf|leaves|garden|gardening|grow)$/],
    ['laptop', /^(computer|laptop|software|technology|online)$/], ['letter', /^(letter|email|mail|envelope|message)$/],
    ['receipt', /^(receipt|invoice|bill|payment|refund)$/], ['travel', /^(luggage|suitcase|travel|trip|journey|baggage)$/],
    ['people', /^(friend|friends|family|people|colleague|team|staff)$/], ['pencil', /^(pencil|pen|write|writing)$/],
  ];
  function object(key, className='') {
    const chosen=objects.has(key)?key:'cards';
    const size=className==='small'?' visual-small':className==='large'?' visual-large':'';
    return `<img class="object-art${size}" src="${asset('/static/illustrations/words/'+chosen+'.svg')}" alt="" width="160" height="160" loading="lazy" decoding="async">`;
  }
  function word(value, size='') {
    const normalized=String(value||'').toLowerCase().trim();
    return object(meanings.find(([,pattern])=>pattern.test(normalized))?.[0]||'cards',size);
  }
  function theme(value) {
    const text=String(value||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d');
    return [['travel',/travel|transport|flight|hotel|holiday|journey|du lich|di chuyen/],['food',/food|cook|restaurant|meal|cafe|am thuc|nau an|an uong/],
      ['nature',/nature|environment|animal|garden|climate|energy|thien nhien|moi truong|dong vat/],['technology',/technology|digital|computer|internet|science|cong nghe|khoa hoc/],
      ['school',/school|education|study|grammar|vocabulary|truong hoc|giao duc|hoc tap/],['work',/toeic|work|business|office|email|meeting|cong viec|van phong/],
      ['city',/city|community|culture|building|thanh pho|cong dong|van hoa/]].find(([,p])=>p.test(text))?.[0]||'reading';
  }
  function cover(value, chosen='') {
    const key=themes.has(chosen)?chosen:theme(value);
    return `<div class="visual-cover"><img src="${asset('/static/illustrations/'+key+'.svg')}" alt="" width="640" height="360" loading="lazy" decoding="async"></div>`;
  }
  function guide(id) {
    const key=[['clock',/time/],['people',/features|ynng/],['book',/heading/],['folder',/information/],
      ['cards',/choice/],['calendar',/table/],['pencil',/completion|sentence|short/],
      ['letter',/toeic/]].find(([,pattern])=>pattern.test(String(id)))?.[0]||'compass';
    const sceneKey=key==='clock'?'spacing':key==='letter'?'import':key==='pencil'?'feedback':key==='cards'?'recall':'guide';
    return scene(sceneKey);
  }
  function scene(key) {
    const chosen=['guide','recall','spacing','feedback','video','grammar','words','import'].includes(key)?key:'guide';
    return `<div class="learning-scene"><img src="${asset('/static/illustrations/scenes/'+chosen+'.svg')}" alt="" width="560" height="240" loading="lazy" decoding="async"></div>`;
  }
  window.LexiVisuals=Object.freeze({object,word,cover,theme,guide,scene});
})();
