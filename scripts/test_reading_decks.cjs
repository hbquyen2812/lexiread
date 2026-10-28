const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {webcrypto}=require('node:crypto');
const {environment}=require('./dom_test_env.cjs');
const read=p=>fs.readFileSync(p,'utf8');
const words=[{word:'confirm',meaning_vi:'xác nhận',synonyms:[],paraphrases:[],tags:[]},{word:'appointment',meaning_vi:'cuộc hẹn',synonyms:[],paraphrases:[],tags:[]}];

async function main(){
  const dom=environment(),{window}=dom,{document}=window,memory=new Map(),calls=[];
  const state={routeEpoch:1,reading:null,study:null,studySettings:{},filters:{tag:'old',q:'old',page:5},readingSources:[]};
  const scope={window,document,state,location:window.location,URL,URLSearchParams,FormData,setTimeout,crypto:webcrypto,
    localStorage:{getItem:k=>memory.get(k)||null,setItem:(k,v)=>memory.set(k,v)},
    PREVIEW_SEED:{words:[],text:'Please confirm your appointment.',analysis:{vocabulary:words},lessons:[],toeic_sets:[]},
    uid:()=>webcrypto.randomUUID(),refreshBoot:async()=>{},
    esc:value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),
    $:s=>document.querySelector(s),modes:{flashcard:'Flashcard'},chips:()=>'',formatNextDue:()=> 'tomorrow'};
  vm.createContext(scope);vm.runInContext(read('scripts/preview_adapter.js'),scope);
  const api=window.LEXIREAD_PREVIEW.api;
  scope.api=async(path,options)=>{calls.push([path,options?.method||'GET']);return api(path,options);};
  const app=read('static/app.js');
  for(const [start,end] of [['async function busy(', 'function tagOptions('],['function renderStage(', 'async function startStudy('],['async function rateCard(', 'async function loadNextQuiz(']]){
    vm.runInContext(app.slice(app.indexOf(start),app.indexOf(end)),scope);
  }
  vm.runInContext(read('static/reading_decks.js'),scope);
  const decks=window.LexiReadingDecks,root=document.querySelector('main');
  const reading=(await api('/readings/')).items[0];state.reading=reading;
  const path='/readings/'+reading.id+'/vocabulary-deck/';
  assert.equal((await api(path)).total,0,'GET never creates cards');
  const button=document.createElement('button');button.textContent='Flashcard bài này';root.append(button);
  const creating=decks.create(button);assert.equal(button.disabled,true);await creating;
  assert.equal(window.location.hash,'#study/'+reading.id);
  await decks.page(root,reading.id,1);
  assert.equal(state.study.initialCount,2);assert.ok(root.querySelector('.flashcard'));
  assert.equal(root.querySelector('select,textarea,input[type=file]'),null,'no setup or import steps');
  assert.equal(calls.filter(([,m])=>m==='POST').length,1,'one click creates once');
  assert.equal(calls.filter(([,m])=>m==='GET').length,0,'immediate response reused');
  assert.equal(root.querySelector('.meaning'),null,'front never reveals the answer');
  state.study.flipped=true;scope.renderStage();
  assert.ok(root.querySelector('.meaning').textContent);
  assert.equal(root.querySelector('blockquote').textContent,'Please confirm your appointment.');
  const originalId=state.study.cards[0].id;
  await scope.rateCard('easy');
  assert.equal(state.study.done,1);
  await decks.page(root,reading.id,1);assert.equal(state.study.done,1,'reopening keeps current session');
  state.study.flipped=true;await scope.rateCard('good');
  assert.ok(root.querySelector('.session-finish'));assert.ok(root.querySelector('[data-reading-deck-words]'));
  const before=(await api('/vocabulary/')).items.find(w=>w.id===originalId);
  await decks.restart(root.querySelector('[data-action=start-study]'));
  assert.equal(state.study.done,0);assert.ok(root.querySelector('.flashcard'));
  assert.equal((await api(path,{method:'POST'})).created,0);
  const after=(await api('/vocabulary/')).items.find(w=>w.id===originalId);
  for(const key of ['id','due_at','repetitions','last_reviewed'])assert.equal(after[key],before[key]);
  root.querySelector('[data-reading-deck-words]').click();
  assert.equal(state.filters.reading,reading.id);assert.equal(state.filters.tag,'');assert.equal(state.filters.q,'');
  console.log('PASS one click -> saved deck -> flashcard -> review -> restart, source filter and idempotent progress');

  let resolve;scope.api=()=>new Promise(r=>resolve=r);
  window.location.hash='reading/'+reading.id;
  const stale=decks.create(button);state.routeEpoch++;
  resolve({reading,items:words});await stale;
  assert.equal(window.location.hash,'#reading/'+reading.id,'stale completion does not hijack navigation');
  scope.api=async()=>{throw new Error('Unavailable');};
  await assert.rejects(decks.create(button),/Unavailable/);
  assert.equal(window.location.hash,'#reading/'+reading.id);
  scope.api=api;
  const empty=await api('/readings/',{method:'POST',data:{title:'Empty',text:'Unknown quux.'}});
  state.study=null;await decks.page(root,empty.id,state.routeEpoch);
  assert.ok(root.textContent.includes('Bài này chưa có thẻ'));
  assert.equal(root.querySelector('.flashcard'),null);
  await assert.rejects(api('/readings/'+empty.id+'/vocabulary-deck/',{method:'POST'}),/Chưa tìm thấy từ/);
  console.log('PASS stale request, server errors and read-only empty deck');

  const malicious='<img src=x onerror=alert(1)>',fixture={reading:{id:reading.id,title:malicious},items:[{...words[0],id:originalId,context:malicious,note:malicious,meaning_vi:malicious}]};
  scope.api=async()=>fixture;state.study=null;
  await decks.page(root,reading.id,state.routeEpoch);state.study.flipped=true;scope.renderStage();
  assert.equal(root.querySelector('h1').textContent,malicious);
  assert.equal(root.querySelector('blockquote').textContent,malicious);
  assert.equal(root.querySelector('img,[onerror],script'),null);
  assert.ok(root.querySelector('h1[data-no-i18n]'));
  console.log('PASS title, meanings and context stay inert; learner content protected from UI translation');
  dom.window.close();
}
main().catch(error=>{console.error(error);process.exitCode=1;});
