/* Optional English passage audio. Only on-device voices; no text leaves the site. */
(() => {
  'use strict';
  const copy = {
    vi: {listen:'Nghe bài đọc',pause:'Tạm dừng',resume:'Tiếp tục',stop:'Dừng',settings:'Giọng & tốc độ',voice:'Giọng đọc',speed:'Tốc độ',loading:'Đang tải giọng đọc…',unavailable:'Thiết bị chưa có giọng đọc tiếng Anh. Hãy thêm giọng English trong cài đặt giọng nói của thiết bị, rồi mở lại trang.',unsupported:'Trình duyệt này chưa hỗ trợ đọc thành tiếng.',failed:'Chưa phát được âm thanh. Bạn hãy bấm nghe để thử lại.',done:'Đã nghe hết bài',part:'Đoạn',ready:'Sẵn sàng',starting:'Đang bắt đầu…'},
    en: {listen:'Listen to the passage',pause:'Pause',resume:'Resume',stop:'Stop',settings:'Voice & speed',voice:'Voice',speed:'Speed',loading:'Loading voices…',unavailable:'No English voice is installed. Add an English voice in your device’s speech settings, then reopen this page.',unsupported:'This browser does not support read-aloud.',failed:'Audio could not start. Press Listen to try again.',done:'Finished listening',part:'Section',ready:'Ready',starting:'Starting…'},
    fr: {listen:'Écouter le texte',pause:'Pause',resume:'Reprendre',stop:'Arrêter',settings:'Voix et vitesse',voice:'Voix',speed:'Vitesse',loading:'Chargement des voix…',unavailable:'Aucune voix anglaise n’est installée. Ajoutez-en une dans les paramètres vocaux de votre appareil, puis rouvrez cette page.',unsupported:'Ce navigateur ne prend pas en charge la lecture à voix haute.',failed:'La lecture n’a pas démarré. Appuyez sur Écouter pour réessayer.',done:'Lecture terminée',part:'Passage',ready:'Prêt',starting:'Démarrage…'},
    zh: {listen:'朗读文章',pause:'暂停',resume:'继续',stop:'停止',settings:'声音与语速',voice:'声音',speed:'语速',loading:'正在加载声音…',unavailable:'设备尚未安装英语语音。请在设备的语音设置中添加英语语音，然后重新打开此页面。',unsupported:'此浏览器不支持朗读。',failed:'无法播放音频，请点击朗读重试。',done:'朗读完毕',part:'段落',ready:'准备就绪',starting:'正在启动…'}
  };
  const synth = window.speechSynthesis;
  const supported = !!(synth && window.SpeechSynthesisUtterance);
  const rates = [0.75, 1, 1.25, 1.5];
  let active = null;
  const labels = () => copy[window.LexiI18n?.language] || copy.vi;
  const voiceKey = voice => `${voice.voiceURI}|${voice.lang}`;
  function preferences() {
    try {
      const value = JSON.parse(localStorage.getItem('lexiread.readAloud') || '{}');
      return {rate:rates.includes(value?.rate) ? value.rate : 1, voice:typeof value?.voice === 'string' ? value.voice : ''};
    } catch { return {rate:1, voice:''}; }
  }
  function save(player) {
    try { localStorage.setItem('lexiread.readAloud', JSON.stringify({rate:player.rate, voice:player.voice})); } catch {}
  }
  // Short utterances avoid engine limits on long passages. Keep the paragraph association.
  function chunks(text) {
    let rest = String(text || '').replace(/\s+/g, ' ').trim();
    const result = [];
    while (rest.length > 220) {
      const head = rest.slice(0, 220);
      const sentence = [...head.matchAll(/[.!?]["')]*\s/g)].pop();
      let end = sentence && sentence.index > 60 ? sentence.index + sentence[0].length : head.lastIndexOf(' ');
      if (end < 1) end = /[\uD800-\uDBFF]/.test(head.at(-1)) ? 219 : 220;
      result.push(rest.slice(0, end).trim());
      rest = rest.slice(end).trim();
    }
    if (rest) result.push(rest);
    return result;
  }
  function clearHighlight(player) {
    player.items.forEach(item => item.node?.classList.remove('is-reading-aloud'));
  }
  function cancel(player) {
    ++player.generation;
    clearTimeout(player.speechTimer);
    if (player.utterance) {
      player.utterance = null;
      try { synth.cancel(); } catch {}
    }
  }
  function stop(player, status = 'idle') {
    cancel(player);
    player.status = status;
    player.index = 0;
    player.offset = 0;
    player.started = false;
    clearHighlight(player);
    update(player);
  }
  function update(player) {
    if (active !== player || !player.host.isConnected) return;
    const t = labels(), busy = player.status === 'playing', paused = player.status === 'paused';
    player.host.dataset.state = player.status;
    player.play.textContent = (busy ? 'Ⅱ ' : '▶ ') + (busy ? t.pause : paused ? t.resume : t.listen);
    player.play.disabled = !supported || !player.voices.length;
    player.stop.disabled = !busy && !paused;
    player.stop.textContent = t.stop;
    player.summary.textContent = t.settings;
    player.voiceLabel.textContent = t.voice;
    player.rateLabel.textContent = t.speed;
    player.voiceSelect.disabled = !player.voices.length;
    player.rateSelect.disabled = !supported;
    const part = player.queue[player.index]?.part || 0;
    player.statusNode.textContent = !supported ? t.unsupported : !player.voices.length ? (player.loaded ? t.unavailable : t.loading) :
      player.status === 'error' ? t.failed : player.status === 'done' ? t.done :
      busy || paused ? `${!player.started && busy ? t.starting : paused ? t.pause : t.part} ${part + 1} / ${player.items.length}` : '';
    player.host.classList.toggle('read-aloud-unavailable', !player.voices.length);
  }
  function refreshVoices(player) {
    if (active !== player) return;
    let voices = [];
    try { voices = supported ? synth.getVoices() : []; } catch {}
    player.voices = voices.filter(v => v.localService === true && /^en(?:[-_]|$)/i.test(v.lang));
    if (voices.length) player.loaded = true;
    const selected = player.voices.find(v => voiceKey(v) === player.voice) || player.voices.find(v => v.default) || player.voices[0];
    if (selected) player.voice = voiceKey(selected);
    player.voiceSelect.replaceChildren();
    for (const voice of player.voices) {
      const option = document.createElement('option');
      option.value = voiceKey(voice);
      option.textContent = `${voice.name} · ${voice.lang}`;
      option.selected = option.value === player.voice;
      player.voiceSelect.append(option);
    }
    if (!player.voices.length && (player.status === 'playing' || player.status === 'paused')) stop(player);
    update(player);
  }
  function speak(player) {
    if (active !== player || !player.host.isConnected) { clear(); return; }
    const voice = player.voices.find(v => voiceKey(v) === player.voice);
    if (!voice) { stop(player, 'error'); return; }
    if (player.index >= player.queue.length) { stop(player, 'done'); return; }
    const chunk = player.queue[player.index], base = player.offset;
    const utterance = new window.SpeechSynthesisUtterance(chunk.text.slice(base));
    const generation = ++player.generation;
    const valid = () => active === player && generation === player.generation && player.host.isConnected;
    player.utterance = utterance; // Keep a reference until end/error, including on mobile.
    player.status = 'playing';
    player.started = false;
    utterance.voice = voice;
    utterance.lang = voice.lang;
    utterance.rate = player.rate;
    const fail = () => { if (valid()) stop(player, 'error'); };
    utterance.onstart = () => {
      if (!valid()) return;
      player.started = true;
      clearTimeout(player.speechTimer);
      player.speechTimer = setTimeout(fail, 90000);
      clearHighlight(player);
      player.items[chunk.part].node?.classList.add('is-reading-aloud');
      update(player);
    };
    utterance.onboundary = event => {
      if (valid() && Number.isInteger(event.charIndex) && event.charIndex >= 0 && event.charIndex < utterance.text.length) player.offset = base + event.charIndex;
    };
    utterance.onend = () => {
      if (!valid()) return;
      clearTimeout(player.speechTimer);
      player.utterance = null;
      player.index++;
      player.offset = 0;
      speak(player);
    };
    utterance.onerror = fail;
    player.speechTimer = setTimeout(fail, 12000);
    update(player);
    try { synth.speak(utterance); } catch { fail(); }
  }
  function clear() {
    if (!active) return;
    const player = active;
    stop(player);
    active = null;
    clearTimeout(player.voiceTimer);
    player.observer?.disconnect();
    synth?.removeEventListener?.('voiceschanged', player.refresh);
    document.removeEventListener('lexiread:language', player.translate);
    player.host.replaceChildren();
  }
  function mount(host, source) {
    clear();
    if (!host) return;
    const items = source.filter(item => String(item.text || '').trim());
    if (!items.length) { host.hidden = true; return; }
    host.hidden = false;
    host.classList.add('read-aloud');
    // This component owns its four UI languages. The passage itself stays English.
    host.setAttribute('data-no-i18n', '');
    host.innerHTML = `<div class="read-aloud-controls"><button type="button" class="btn secondary" data-audio-play></button><button type="button" class="btn" data-audio-stop></button><details class="read-aloud-settings"><summary></summary><div class="read-aloud-fields"><label><span data-audio-voice-label></span><select data-audio-voice></select></label><label><span data-audio-rate-label></span><select data-audio-rate>${rates.map(rate=>`<option value="${rate}">${rate}×</option>`).join('')}</select></label></div></details></div><p class="read-aloud-status" role="status" aria-live="polite"></p>`;
    const find = selector => host.querySelector(selector);
    const player = {host, items, queue:items.flatMap((item, part)=>chunks(item.text).map(text=>({text, part}))), ...preferences(), voices:[], status:'idle', index:0, offset:0, generation:0, loaded:false,
      play:find('[data-audio-play]'), stop:find('[data-audio-stop]'), summary:find('summary'), voiceLabel:find('[data-audio-voice-label]'), rateLabel:find('[data-audio-rate-label]'), voiceSelect:find('[data-audio-voice]'), rateSelect:find('[data-audio-rate]'), statusNode:find('[role="status"]')};
    active = player;
    player.rateSelect.value = String(player.rate);
    player.play.addEventListener('click', () => {
      if (player.status === 'playing') {
        // Cancel + resume from the last word boundary also works where native pause ends an utterance.
        cancel(player); player.status = 'paused'; update(player);
      } else if (player.voices.length) { save(player); speak(player); }
    });
    player.stop.addEventListener('click', () => stop(player));
    const change = () => {
      player.rate = Number(player.rateSelect.value);
      player.voice = player.voiceSelect.value;
      save(player);
      if (player.status === 'playing') { cancel(player); speak(player); }
    };
    player.voiceSelect.addEventListener('change', change);
    player.rateSelect.addEventListener('change', change);
    player.refresh = () => refreshVoices(player);
    player.translate = () => update(player);
    synth?.addEventListener?.('voiceschanged', player.refresh);
    document.addEventListener('lexiread:language', player.translate);
    player.voiceTimer = setTimeout(() => { player.loaded = true; refreshVoices(player); }, 2500);
    player.observer = new MutationObserver(() => { if (!host.isConnected && active === player) clear(); });
    player.observer.observe(document.body, {childList:true, subtree:true});
    refreshVoices(player);
  }
  window.addEventListener('pagehide', clear);
  window.addEventListener('hashchange', clear);
  window.LexiReadAloud = {mount, clear};
})();
