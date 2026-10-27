/* Small, opt-in audio controls for explicitly selected English words/examples. */
(() => {
  'use strict';
  const strings = {
    vi:{word:'Nghe từ',sentence:'Nghe câu',stop:'Dừng đọc',loading:'Đang chuẩn bị âm thanh…',playing:'Đang đọc',failed:'Chưa phát được âm thanh. Bấm loa để thử lại.',unavailable:'Thiết bị chưa có giọng tiếng Anh. Thêm giọng English trong cài đặt giọng nói rồi mở lại trang.',unsupported:'Trình duyệt này chưa hỗ trợ giọng đọc. Bạn vẫn có thể nghe các bản thu có sẵn.'},
    en:{word:'Listen to the word',sentence:'Listen to the sentence',stop:'Stop reading',loading:'Preparing audio…',playing:'Reading aloud',failed:'Audio could not play. Press the speaker to try again.',unavailable:'No English voice is installed. Add an English voice in your device’s speech settings, then reopen this page.',unsupported:'This browser does not support speech synthesis. Available recordings can still be played.'},
    fr:{word:'Écouter le mot',sentence:'Écouter la phrase',stop:'Arrêter la lecture',loading:'Préparation de l’audio…',playing:'Lecture en cours',failed:'Lecture impossible. Appuyez sur le haut-parleur pour réessayer.',unavailable:'Aucune voix anglaise installée. Ajoutez-en une dans les paramètres vocaux de votre appareil, puis rouvrez cette page.',unsupported:'Ce navigateur ne prend pas en charge la synthèse vocale. Les enregistrements restent disponibles.'},
    zh:{word:'听单词',sentence:'听例句',stop:'停止朗读',loading:'正在准备音频…',playing:'正在朗读',failed:'无法播放音频，请点击喇叭重试。',unavailable:'设备尚未安装英语语音。请在设备的语音设置中添加英语语音，然后重新打开此页面。',unsupported:'此浏览器不支持语音合成，仍可播放已有录音。'}
  };
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const labels=()=>strings[window.LexiI18n?.language]||strings.vi;
  const safeRecording=value=>/^\/api\/dictionary\/audio\/[a-f0-9]{64}\/$/.test(value||'')?value:'';
  const speaker='<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M11 4 6 8H3v8h3l5 4V4Zm4 4a6 6 0 0 1 0 8m3-11a10 10 0 0 1 0 14"/></svg>';
  let current=null;
  function button(text,kind='word',recording='',caption=false) {
    text=String(text||'').replace(/\s+/g,' ').trim();
    if(!text||text.length>4000)return '';
    kind=kind==='sentence'?'sentence':'word';
    const label=labels()[kind]+': '+text.slice(0,100);
    return `<span class="pronunciation" data-no-i18n><button type="button" class="pronunciation-button${caption?' with-label':''}" data-pronounce="${esc(text)}" data-pronounce-kind="${kind}"${safeRecording(recording)?` data-pronounce-src="${esc(recording)}"`:''} aria-label="${esc(label)}" title="${esc(label)}" aria-pressed="false">${speaker}${caption?`<span data-pronounce-caption>${esc(labels()[kind])}</span>`:''}</button><span class="pronunciation-status" role="status" aria-live="polite"></span></span>`;
  }
  function updateButton(button) {
    const active=current?.button===button;
    const label=(active?labels().stop:labels()[button.dataset.pronounceKind]||labels().word)+': '+button.dataset.pronounce.slice(0,100);
    button.setAttribute('title',label);
    button.setAttribute('aria-label',label);
    button.setAttribute('aria-pressed',String(active));
    button.classList.toggle('is-playing',active);
    button.classList.toggle('is-loading',active&&current.status==='loading');
    const caption=button.querySelector('[data-pronounce-caption]');
    if(caption)caption.textContent=active?labels().stop:labels()[button.dataset.pronounceKind];
  }
  function status(player,key) {
    player.status=key;
    player.note.dataset.message=key;
    player.note.textContent=labels()[key]||'';
    player.note.classList.toggle('has-error',['failed','unavailable','unsupported'].includes(key));
    updateButton(player.button);
  }
  function stop() {
    if(!current)return;
    const player=current;current=null;
    clearTimeout(player.timer);
    player.observer?.disconnect();
    window.speechSynthesis?.removeEventListener?.('voiceschanged',player.voicesChanged);
    if(player.audio){player.audio.onended=player.audio.onerror=player.audio.onplaying=player.audio.onpause=null;player.audio.pause();}
    if(player.utterance){player.utterance=null;try{window.speechSynthesis.cancel();}catch{}}
    player.note.textContent='';delete player.note.dataset.message;player.note.classList.remove('has-error');
    updateButton(player.button);
  }
  const visible=player=>{
    if(!player.button.isConnected)return false;
    for(let node=player.button.parentElement;node;node=node.parentElement){
      if(node.hidden||(node.tagName==='DIALOG'&&!node.open)||(node.tagName==='DETAILS'&&!node.hasAttribute('open')))return false;
    }
    return true;
  };
  function fail(player,key='failed') { if(current!==player)return;stop();status(player,key); }
  function pauseRecordings(except=null) { document.querySelectorAll('audio').forEach(audio=>{if(audio!==except)audio.pause();}); }
  function speak(player) {
    if(current!==player)return;
    if(!visible(player)){stop();return;}
    const settings=window.LexiReadAloud.getVoice();
    if(!settings.voice){fail(player,'unavailable');return;}
    if(!player.queue.length){stop();return;}
    const utterance=new window.SpeechSynthesisUtterance(player.queue.shift());
    player.utterance=utterance;
    utterance.voice=settings.voice;utterance.lang=settings.voice.lang;utterance.rate=settings.rate;
    const valid=()=>current===player&&player.utterance===utterance;
    status(player,'loading');
    clearTimeout(player.timer);player.timer=setTimeout(()=>{if(valid())fail(player);},12000);
    utterance.onstart=()=>{if(!valid())return;status(player,'playing');clearTimeout(player.timer);player.timer=setTimeout(()=>{if(valid())fail(player);},90000);};
    utterance.onend=()=>{if(!valid())return;clearTimeout(player.timer);player.utterance=null;speak(player);};
    utterance.onerror=()=>{if(valid())fail(player);};
    try{window.speechSynthesis.speak(utterance);}catch{fail(player);}
  }
  function useDeviceVoice(player) {
    if(current!==player)return;
    clearTimeout(player.timer);
    if(!window.speechSynthesis||!window.SpeechSynthesisUtterance||!window.LexiReadAloud){fail(player,'unsupported');return;}
    if(window.LexiReadAloud.getVoice().voice){speak(player);return;}
    status(player,'loading');
    player.voicesChanged=()=>{
      if(current!==player||!window.LexiReadAloud.getVoice().voice)return;
      window.speechSynthesis.removeEventListener('voiceschanged',player.voicesChanged);
      clearTimeout(player.timer);speak(player);
    };
    window.speechSynthesis.addEventListener('voiceschanged',player.voicesChanged);
    player.timer=setTimeout(()=>fail(player,'unavailable'),2500);
  }
  function play(button) {
    if(current?.button===button){stop();return;}
    stop();window.LexiReadAloud?.interrupt();pauseRecordings();
    const text=button.dataset.pronounce;
    if(!text||text.length>4000)return;
    const player={button,note:button.parentElement.querySelector('[role="status"]'),queue:window.LexiReadAloud?.chunks(text)||[text]};
    current=player;
    if(!visible(player)){stop();return;}
    player.observer=new MutationObserver(()=>{if(current===player&&!visible(player))stop();});
    player.observer.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden','open']});
    const src=safeRecording(button.dataset.pronounceSrc);
    if(!src||!window.Audio){useDeviceVoice(player);return;}
    status(player,'loading');
    const existing=[...(button.closest('.dictionary-panel')?.querySelectorAll('audio')||[])].find(audio=>audio.getAttribute('src')===src);
    const audio=existing||new window.Audio(src);player.audio=audio;audio.preload='none';
    try{audio.currentTime=0;}catch{}
    audio.playbackRate=window.LexiReadAloud?.getVoice().rate||1;
    // One failed recording may fall back once; stale media callbacks cannot restart speech.
    const fallback=()=>{if(current!==player||player.audio!==audio)return;audio.onended=audio.onerror=audio.onplaying=audio.onpause=null;audio.pause();player.audio=null;useDeviceVoice(player);};
    audio.onplaying=()=>{if(current!==player||player.audio!==audio)return;clearTimeout(player.timer);status(player,'playing');player.timer=setTimeout(fallback,30000);};
    audio.onended=()=>{if(current===player&&player.audio===audio)stop();};
    audio.onpause=()=>{if(current===player&&player.audio===audio)stop();};
    audio.onerror=fallback;
    player.timer=setTimeout(fallback,6000);
    try{audio.play()?.catch(fallback);}catch{fallback();}
  }
  document.addEventListener('click',event=>{
    const button=event.target.closest('[data-pronounce]');
    if(!button)return;
    event.preventDefault();event.stopPropagation();play(button);
  });
  document.addEventListener('play',event=>{if(event.target.tagName==='AUDIO'){if(current?.audio!==event.target)stop();window.LexiReadAloud?.interrupt();pauseRecordings(event.target);}},true);
  document.addEventListener('close',event=>{if(current&&current.button.closest('dialog')===event.target)stop();},true);
  document.addEventListener('lexiread:language',()=>{
    document.querySelectorAll('[data-pronounce]').forEach(updateButton);
    document.querySelectorAll('.pronunciation-status[data-message]').forEach(note=>{note.textContent=labels()[note.dataset.message]||'';});
  });
  window.addEventListener('pagehide',stop);
  window.addEventListener('hashchange',()=>{stop();pauseRecordings();});
  window.LexiPronunciation={button,stop,stopWithin:root=>{if(current&&root?.contains(current.button))stop();}};
})();
