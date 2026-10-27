const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {setup}=require('./test_read_aloud.cjs');
const tick=()=>new Promise(resolve=>setImmediate(resolve));
const read=file=>fs.readFileSync(file,'utf8');
function boot(options={}){
  const p=setup(options),recordings=[];
  p.win.Audio=class{
    constructor(src){this.src=src;this.paused=true;recordings.push(this);}
    play(){this.paused=false;return new Promise((resolve,reject)=>{this.resolve=resolve;this.reject=reject;});}
    pause(){this.paused=true;}
  };
  vm.runInNewContext(read('static/pronunciation.js'),p.scope);
  const controls=p.document.createElement('section');p.document.body.append(controls);
  const add=(text='routine',kind='word',src='')=>{
    controls.insertAdjacentHTML('beforeend',p.win.LexiPronunciation.button(text,kind,src,true));
    return [...controls.querySelectorAll('[data-pronounce]')].at(-1);
  };
  return {...p,recordings,controls,add,stop:()=>{p.win.LexiPronunciation.stop();p.win.LexiReadAloud.clear();}};
}

async function main(){
  const p=boot({saved:JSON.stringify({rate:0.75,voice:'local-uk|en-GB'})});
  const word=p.add(),sentence=p.add('I keep a simple morning routine.','sentence');
  assert.equal(p.spoken.length,0);word.click();let u=p.spoken.at(-1);
  assert.equal(u.text,'routine');assert.equal(u.voice.lang,'en-GB');assert.equal(u.rate,0.75);
  assert.equal(word.getAttribute('aria-pressed'),'true');u.onstart();
  assert.equal(word.nextElementSibling.textContent,'Đang đọc');
  for(const [language,label] of [['en','Stop reading'],['fr','Arrêter la lecture'],['zh','停止朗读'],['vi','Dừng đọc']]){
    p.win.LexiI18n.language=language;p.document.dispatchEvent(new p.dom.Event('lexiread:language'));
    assert.ok(word.getAttribute('aria-label').startsWith(label));
  }
  assert.equal(p.spoken.length,1,'changing UI language does not restart speech');
  sentence.click();u.onend();u.onerror();assert.equal(p.spoken.length,2,'stale callback cannot restart old word');
  assert.equal(p.spoken.at(-1).text,sentence.dataset.pronounce);sentence.click();assert.equal(sentence.getAttribute('aria-pressed'),'false');
  p.mount();p.click('[data-audio-play]');p.spoken.at(-1).onstart();word.click();
  assert.equal(p.host.dataset.state,'idle');assert.ok(p.$('[data-audio-play]'),'word playback keeps passage controls');
  p.click('[data-audio-play]');assert.equal(word.getAttribute('aria-pressed'),'false','reading playback stops word');
  p.stop();
  const malicious=p.add('<img src=x onerror="bad()">','word','https://evil.example/private');
  assert.equal(malicious.dataset.pronounceSrc,undefined);assert.equal(p.controls.querySelector('img'),null);
  assert.equal(malicious.dataset.pronounce,'<img src=x onerror="bad()">');
  assert.equal(p.win.LexiPronunciation.button('x'.repeat(4001)),'');
  console.log('PASS no autoplay, English/local preference, safe HTML/media, word/sentence controls, locales and passage coordination');

  const media=boot(),src='/api/dictionary/audio/'+'a'.repeat(64)+'/';
  const a=media.add('travel','word',src);a.click();const original=media.recordings[0];
  assert.equal(original.src,src);assert.equal(media.spoken.length,0,'prefer existing local recording');
  original.onplaying();assert.equal(a.nextElementSibling.textContent,'Đang đọc');
  const staleError=original.onerror;original.onerror();assert.equal(media.spoken.length,1,'failed recording falls back to device voice');
  staleError();original.reject(Error());await tick();assert.equal(media.spoken.length,1,'fall back once');
  media.stop();a.click();const cancelled=media.recordings.at(-1);media.stop();cancelled.reject(Error());await tick();
  assert.equal(media.spoken.length,1,'rejected canceled media cannot restart speech');
  a.click();media.fireTimer(6000);assert.equal(media.spoken.length,2);media.stop();
  const recordingOnly=boot({supported:false}),r=recordingOnly.add('travel','word',src);r.click();
  recordingOnly.recordings[0].onplaying();recordingOnly.recordings[0].onended();
  assert.equal(r.getAttribute('aria-pressed'),'false');recordingOnly.stop();
  const shared=boot();shared.controls.className='dictionary-panel';
  const sharedButton=shared.add('travel','word',src),sharedAudio=shared.document.createElement('audio');
  sharedAudio.setAttribute('src',src);shared.controls.append(sharedAudio);
  sharedAudio.pause=()=>{sharedAudio.onpause?.();};
  sharedAudio.play=()=>{sharedAudio.dispatchEvent(new shared.dom.Event('play',{bubbles:true}));sharedAudio.onplaying();return Promise.resolve();};
  sharedButton.click();assert.equal(shared.recordings.length,0,'reuse visible dictionary player');
  assert.equal(sharedButton.getAttribute('aria-pressed'),'true','own native play event does not cancel itself');
  sharedAudio.pause();assert.equal(sharedButton.getAttribute('aria-pressed'),'false','native pause resets speaker button');shared.stop();
  const native=p.document.createElement('audio');native.pause=()=>native.pausedForTest=true;p.document.body.append(native);
  word.click();native.dispatchEvent(new p.dom.Event('play',{bubbles:true}));assert.equal(word.getAttribute('aria-pressed'),'false');
  p.mount();p.click('[data-audio-play]');assert.equal(native.pausedForTest,true);p.stop();
  console.log('PASS stored recording priority, unsupported-speech recording playback, media rejection/timeout fallback and no overlapping audio');

  const late=boot({voices:[]}),b=late.add();b.click();assert.equal(late.spoken.length,0);
  late.setVoices([{name:'Local',voiceURI:'local',lang:'en-US',localService:true}]);assert.equal(late.spoken.length,1);late.stop();
  const empty=boot({voices:[]}),c=empty.add();c.click();empty.fireTimer(2500);assert.match(c.nextElementSibling.textContent,/chưa có giọng/);
  empty.setVoices([{name:'Cloud',voiceURI:'cloud',lang:'en-US',localService:false}]);c.click();empty.fireTimer(2500);assert.equal(empty.spoken.length,0);empty.stop();
  const missing=boot({supported:false}),d=missing.add();d.click();assert.match(d.nextElementSibling.textContent,/chưa hỗ trợ/);missing.stop();
  const lifecycle=boot(),e=lifecycle.add();e.click();lifecycle.fireTimer(12000);assert.match(e.nextElementSibling.textContent,/Chưa phát được/);
  e.click();lifecycle.spoken.at(-1).onstart();lifecycle.fireTimer(90000);assert.match(e.nextElementSibling.textContent,/Chưa phát được/);
  e.click();lifecycle.controls.hidden=true;await tick();assert.equal(e.getAttribute('aria-pressed'),'false');
  lifecycle.controls.hidden=false;e.click();e.parentElement.remove();await tick();assert.equal(e.getAttribute('aria-pressed'),'false');
  const dialog=lifecycle.document.createElement('dialog');dialog.open=true;lifecycle.document.body.append(dialog);
  dialog.innerHTML=lifecycle.win.LexiPronunciation.button('hello');const f=dialog.querySelector('button');f.click();
  dialog.dispatchEvent(new lifecycle.dom.Event('close',{bubbles:true}));assert.equal(f.getAttribute('aria-pressed'),'false');
  const g=lifecycle.add();g.click();lifecycle.event('hashchange');assert.equal(g.getAttribute('aria-pressed'),'false');lifecycle.stop();
  console.log('PASS delayed/missing voices, no remote voice fallback, speech errors/timeouts, hidden/removed controls, modal and route cleanup');

  const long=boot(),text='This example explains a familiar daily activity. '.repeat(25),longButton=long.add(text,'sentence');longButton.click();
  const chunks=[];while(longButton.getAttribute('aria-pressed')==='true'){const u=long.spoken.at(-1);assert.ok(u.text.length<=220);chunks.push(u.text);u.onend();}
  assert.equal(chunks.join(' '),text.trim());long.stop();

  const render=boot(),scope=render.scope;
  for(const module of ['dictionary','grammar_reference','grammar_course'])vm.runInNewContext(read(`static/${module}.js`),scope);
  const grammar=JSON.parse(read('data/grammar_lessons.json')).lessons[0];
  render.controls.innerHTML=render.win.LexiGrammar.lessonHTML(grammar,'','<form>Practice</form>');
  assert.equal(render.controls.querySelectorAll('[data-pronounce]').length,grammar.explanation.length+1);
  assert.equal(render.controls.querySelector('.grammar-quick-check [data-pronounce]'),null,'hidden answers have no audio shortcut');
  assert.equal(render.controls.querySelector('[data-grammar-panel=practice] [data-pronounce]'),null);
  const english=render.controls.querySelector('.grammar-explanation [lang=en]').textContent;
  render.controls.querySelector('[data-pronounce]').click();assert.equal(render.spoken.at(-1).text,english);render.stop();
  render.controls.innerHTML=render.win.LexiDictionary.render({word:'routine',local_entries:[{example:'I keep a routine.',meaning_vi:'thói quen'}],dictionary:{entries:[]}});
  const targets=[...render.controls.querySelectorAll('[data-pronounce]')].map(b=>b.dataset.pronounce);
  assert.deepEqual(targets,['routine','I keep a routine.']);
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  render.document.body.innerHTML='<section id="study-stage"></section>';
  Object.assign(scope,{$:s=>render.document.querySelector(s),esc,asList:x=>x||[],chips:()=>'',modes:{flashcard:'Flashcard'},state:{studySettings:{limit:20},study:{mode:'flashcard',idx:0,done:0,cards:[{word:'routine',example:'I keep a routine.',meaning_vi:'thói quen'}],flipped:false}}});
  const app=read('static/app.js');
  vm.runInNewContext(app.slice(app.indexOf('function lexicalRelations'),app.indexOf('function blankEntry')),scope);
  vm.runInNewContext(app.slice(app.indexOf('function renderStage()'),app.indexOf('async function startStudy')),scope);
  scope.renderStage();assert.equal(render.$('.flashcard [data-pronounce]'),null,'no button nested in clickable flashcard');
  assert.equal(render.document.querySelectorAll('[data-pronounce]').length,1);
  render.$('[data-pronounce]').click();assert.equal(scope.state.study.flipped,false,'audio does not flip card');
  scope.state.study.flipped=true;scope.renderStage();assert.equal(render.document.querySelectorAll('[data-pronounce]').length,2);
  assert.equal(render.$('.flashcard [data-pronounce]'),null);render.stop();
  console.log('PASS long sentences, real grammar/dictionary/flashcard renderers, English-only targets and no nested buttons or hidden-answer leaks');
}
main().catch(error=>{console.error(error);process.exitCode=1;});
