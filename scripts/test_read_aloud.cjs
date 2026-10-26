/* DOM + speech-engine contract tests; no network, browser or paid service. */
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {parseHTML}=require('linkedom');
const source=fs.readFileSync('static/read_aloud.js','utf8');
const english={voiceURI:'local-us',name:'English US',lang:'en-US',localService:true,default:true};
const british={voiceURI:'local-uk',name:'English UK',lang:'en-GB',localService:true};
const remote={voiceURI:'remote',name:'Cloud',lang:'en-US',localService:false};
const french={voiceURI:'fr',name:'French',lang:'fr-FR',localService:true};
function setup({voices=[english,british,remote,french],supported=true,saved=null,blockedStorage=false}={}) {
  const {window:dom}=parseHTML('<html><body><main><div id="audio"></div><p id="one" lang="en">A morning walk helps me think.</p><p id="two" lang="en">I like to walk beside the river.</p><p class="reader-vi">Tôi thích đi bộ.</p></main></body></html>');
  // linkedom exposes select.value as read-only; emulate the browser setter.
  Object.defineProperty(dom.HTMLSelectElement.prototype,'value',{configurable:true,
    get(){return [...this.options].find(o=>o.selected)?.value || this.options[0]?.value || '';},
    set(value){for(const option of this.options)option.removeAttribute('selected');const selected=[...this.options].find(o=>o.value===String(value));if(selected)selected.setAttribute('selected','');}});
  const {document}=dom,timers=new Map(),storage=new Map(saved?[['lexiread.readAloud',saved]]:[]),windowListeners={},voiceListeners=new Set();
  let timerId=0,cancels=0;
  const spoken=[],synth={getVoices:()=>voices,speak:u=>spoken.push(u),cancel(){cancels++;},
    addEventListener:(name,fn)=>voiceListeners.add(fn),removeEventListener:(name,fn)=>voiceListeners.delete(fn)};
  const win={LexiI18n:{language:'vi'},addEventListener:(name,fn)=>(windowListeners[name]??=[]).push(fn)};
  if(supported){win.speechSynthesis=synth;win.SpeechSynthesisUtterance=class{constructor(text){this.text=text;}};}
  const scope={window:win,document,MutationObserver:dom.MutationObserver,
    setTimeout:(fn,delay)=>{const id=++timerId;timers.set(id,{fn,delay});return id;},clearTimeout:id=>timers.delete(id),
    localStorage:{getItem:key=>{if(blockedStorage)throw Error();return storage.get(key);},setItem:(key,value)=>{if(blockedStorage)throw Error();storage.set(key,value);}}};
  vm.runInNewContext(source,scope);
  const $=selector=>document.querySelector(selector),host=$('#audio');
  const items=['one','two'].map(id=>({node:$('#'+id),text:$('#'+id).textContent}));
  const mount=(input=items)=>win.LexiReadAloud.mount(host,input);
  const click=selector=>$(selector).click();
  const change=(selector,value)=>{$(selector).value=value;$(selector).dispatchEvent(new dom.Event('change'));};
  return {dom,document,win,scope,$,host,items,mount,click,change,spoken,storage,timers,
    get cancels(){return cancels;},setVoices(value){voices=value;voiceListeners.forEach(fn=>fn());},
    fireTimer(delay){const entry=[...timers].find(([,t])=>t.delay===delay);assert.ok(entry);timers.delete(entry[0]);entry[1].fn();},
    event:name=>windowListeners[name].forEach(fn=>fn()),voiceListeners};
}

async function main(){
  const p=setup();p.mount();
  assert.equal(p.spoken.length,0,'never autoplay');
  assert.equal(p.$('[data-audio-voice]').options.length,2,'only English on-device voices');
  assert.equal(p.$('[data-audio-stop]').disabled,true);
  p.click('[data-audio-play]');let u=p.spoken.at(-1);u.onstart();
  assert.equal(u.text,p.items[0].text);assert.equal(u.voice,english);assert.equal(u.rate,1);
  assert.equal(p.$('.is-reading-aloud').id,'one');
  u.onboundary({charIndex:10});p.click('[data-audio-play]');
  assert.equal(p.host.dataset.state,'paused');assert.equal(p.cancels,1);
  u.onend();u.onerror();assert.equal(p.spoken.length,1,'ignore canceled callbacks');
  p.click('[data-audio-play]');u=p.spoken.at(-1);assert.equal(u.text,p.items[0].text.slice(10));u.onstart();
  p.change('[data-audio-rate]','1.25');assert.equal(p.spoken.at(-1).rate,1.25);
  p.change('[data-audio-voice]','local-uk|en-GB');assert.equal(p.spoken.at(-1).voice,british);
  assert.deepEqual(JSON.parse(p.storage.get('lexiread.readAloud')),{rate:1.25,voice:'local-uk|en-GB'});
  const count=p.spoken.length,englishText=p.items.map(i=>i.node.textContent);
  for(const [language,label] of [['en','Pause'],['fr','Pause'],['zh','暂停'],['vi','Tạm dừng']]){
    p.win.LexiI18n.language=language;p.document.dispatchEvent(new p.dom.Event('lexiread:language'));
    assert.ok(p.$('[data-audio-play]').textContent.includes(label));
  }
  assert.equal(p.spoken.length,count,'language switch must not restart audio');
  assert.deepEqual(p.items.map(i=>i.node.textContent),englishText);
  p.spoken.at(-1).onend();u=p.spoken.at(-1);u.onstart();assert.equal(u.text,p.items[1].text);
  assert.equal(p.$('.is-reading-aloud').id,'two');u.onend();
  assert.equal(p.host.dataset.state,'done');assert.equal(p.$('.is-reading-aloud'),null);
  p.click('[data-audio-play]');assert.equal(p.spoken.at(-1).text,p.items[0].text);
  p.event('hashchange');assert.equal(p.host.children.length,0);assert.equal(p.voiceListeners.size,0);
  p.spoken.at(-1).onend();assert.equal(p.spoken.length,count+2);
  console.log('PASS opt-in playback, English/local voices, pause/resume, settings, four languages, completion and route cleanup');

  const late=setup({voices:[],saved:JSON.stringify({rate:1.5,voice:'local-uk|en-GB'})});late.mount();
  assert.equal(late.$('[data-audio-play]').disabled,true);late.fireTimer(2500);
  assert.match(late.$('[role=status]').textContent,/Thiết bị chưa có/);
  late.setVoices([english,british]);assert.equal(late.spoken.length,0);late.click('[data-audio-play]');
  assert.equal(late.spoken[0].voice,british);assert.equal(late.spoken[0].rate,1.5);
  late.spoken[0].onerror({error:'synthesis-failed'});assert.equal(late.host.dataset.state,'error');
  late.click('[data-audio-play]');late.fireTimer(12000);assert.equal(late.host.dataset.state,'error');
  late.click('[data-audio-play]');late.spoken.at(-1).onstart();late.fireTimer(90000);
  assert.equal(late.host.dataset.state,'error','hung playback recovers');
  late.click('[data-audio-play]');late.setVoices([remote]);assert.equal(late.$('[data-audio-play]').disabled,true);
  late.win.LexiReadAloud.clear();
  for(const options of [{supported:false},{voices:[remote,french]},{saved:'null'},{saved:'bad json'},{blockedStorage:true}]){
    const q=setup(options);q.mount();assert.equal(q.spoken.length,0);
    if(options.supported===false)assert.match(q.$('[role=status]').textContent,/chưa hỗ trợ/);
    if(options.voices)assert.equal(q.$('[data-audio-play]').disabled,true);
    q.win.LexiReadAloud.clear();
  }
  console.log('PASS asynchronous voices, remembered preferences, unsupported browser, blocked storage, speech errors and timeouts');

  const long=setup();const text=('A longer sentence with many familiar English words. ').repeat(55);
  long.mount([{text,node:long.items[0].node}]);long.click('[data-audio-play]');
  const chunks=[];
  while(long.host.dataset.state==='playing'){
    const current=long.spoken.at(-1);assert.ok(current.text.length<=220);chunks.push(current.text);current.onstart();current.onend();
  }
  assert.equal(chunks.join(' '),text.trim(),'long passage has no omissions');
  long.click('[data-audio-play]');long.spoken.at(-1).onstart();long.mount();
  assert.equal(long.$('.is-reading-aloud'),null);assert.equal(long.host.dataset.state,'idle');
  long.click('[data-audio-play]');long.host.remove();await new Promise(resolve=>setImmediate(resolve));
  assert.equal(long.voiceListeners.size,0,'removed host stops and unregisters');
  console.log('PASS long-passage queue, no omissions, remount and detached-host cleanup');

  // Exercise the actual reader renderer, including its translation and non-text tabs.
  const integration=setup();integration.document.body.innerHTML='<main id="main"></main>';
  const {scope}=integration;
  Object.assign(scope,{$:s=>integration.document.querySelector(s),esc:s=>String(s||''),highlight:s=>s,heading:()=>'',readingExtraTab:box=>box.innerHTML='Quiz',
    state:{reading:{id:'r1',title:'Practice',paragraphs:['English passage one.','English passage two.'],analysis:{translations:[{index:0,vi:'Bản dịch tiếng Việt.'}]},progress:{}},translation:true,readingTab:'text',boot:{},readerWords:[]}});
  const app=fs.readFileSync('static/app.js','utf8');
  vm.runInNewContext(app.slice(app.indexOf('function renderReader()'),app.indexOf('async function vocabPage(')),scope);
  scope.renderReader();integration.click('[data-audio-play]');assert.equal(integration.spoken[0].text,'English passage one.');
  assert.ok(integration.$('.reader-vi'));scope.state.readingTab='help';scope.renderReader();
  assert.equal(integration.$('.read-aloud'),null);assert.equal(integration.cancels,1);
  integration.win.LexiReadAloud.clear();
  console.log('PASS reader integration: original English only, translations preserved, tab switch stops audio');

  const toeic=setup();toeic.document.body.innerHTML='<main id="main"></main>';
  const question=(id,doc)=>({id,document_ids:[doc],part:7,prompt:'Which answer is correct?',options:['Secret answer','Wrong answer']});
  const practice={title:'Practice',parts:[7],documents:[{id:'d1',heading:'Office notice',body:'Please arrive at nine.',kind:'Notice'},{id:'d2',heading:'Reply',body:'Thank you for the update.',kind:'Email'}],questions:[question('q1','d1'),question('q2','d2'),question('q3','d1')],focus_vocabulary:[]};
  Object.assign(toeic.scope,{$:s=>toeic.document.querySelector(s),esc:s=>String(s||''),heading:()=>'',setInterval:()=>0,clearInterval:()=>{},state:{toeicSet:practice,toeicSession:{answers:{}}}});
  vm.runInNewContext(fs.readFileSync('static/practice_tools.js','utf8'),toeic.scope);
  toeic.scope.renderToeicPractice();toeic.click('[data-audio-play]');
  assert.equal(toeic.spoken[0].text,'Office notice. Please arrive at nine.');
  toeic.spoken[0].onend();assert.equal(toeic.spoken[1].text,'Reply. Thank you for the update.');
  toeic.spoken[1].onend();assert.equal(toeic.spoken.length,2,'questions and answers are not read');
  assert.equal(toeic.$('.read-aloud').dataset.state,'done');
  practice.documents=[];practice.parts=[5];toeic.scope.renderToeicPractice();assert.equal(toeic.$('.read-aloud'),null);
  toeic.win.LexiReadAloud.clear();
  console.log('PASS TOEIC integration: documents only, no answers or duplicates, no audio toolbar without passages');
}
if(require.main===module)main().catch(error=>{console.error(error);process.exitCode=1;});
module.exports={setup};
