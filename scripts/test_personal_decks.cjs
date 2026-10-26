/* Deterministic file and offline-storage contracts; visual QA runs separately. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const {webcrypto}=require('node:crypto');
const read=p=>fs.readFileSync(p,'utf8'),memory=new Map();
const scope={window:{},document:{addEventListener(){}},URL,URLSearchParams,FormData,TextEncoder,setTimeout,crypto:webcrypto,
  localStorage:{getItem:k=>memory.get(k)||null,setItem:(k,v)=>memory.set(k,v)},
  PREVIEW_SEED:{words:[],text:'A sample.',analysis:{},lessons:[],toeic_sets:[]}};
vm.runInNewContext(read('static/personal_decks.js'),scope);
vm.runInNewContext(read('scripts/preview_adapter.js'),scope);
const decks=scope.window.LexiDecks,api=scope.window.LEXIREAD_PREVIEW.api;
(async()=>{
  const input=decks.sample('Bộ từ của tôi');
  assert.equal(decks.normalize(input).items.length,2);
  input.vocabulary.push({...input.vocabulary[0],word:' CONFIRM '});
  assert.equal(decks.normalize(input).duplicates,1);
  const post=(deck,preview=false)=>api('/vocabulary/deck/',{method:'POST',data:{deck,preview}});
  assert.equal((await post(input,true)).new,2);
  assert.equal((await api('/vocabulary/')).total,0);
  assert.equal((await post(input)).created,2);
  let word=(await api('/vocabulary/')).items[0];
  await api(`/vocabulary/${word.id}/review/`,{method:'POST',data:{rating:'easy',token:webcrypto.randomUUID()}});
  const before=(await api('/vocabulary/')).items.find(w=>w.id===word.id);
  input.deck.name='Bộ thứ hai';input.vocabulary[0].note='Do not replace my notes';
  assert.equal((await post(input)).created,0);
  const after=(await api('/vocabulary/')).items.find(w=>w.id===word.id);
  for(const field of ['id','due_at','repetitions','note','example'])assert.equal(after[field],before[field]);
  const exported=await api('/vocabulary/deck/?name='+encodeURIComponent(input.deck.name));
  assert.equal(exported.vocabulary.length,2);assert.equal('id' in exported.vocabulary[0],false);
  assert.equal((await post(exported)).created,0);
  for(const malformed of [{}, {...input,version:true}, {...input,vocabulary:[{}]}, {...input,vocabulary:Array(501).fill(input.vocabulary[0])}])assert.throws(()=>decks.normalize(malformed));
  const bad=structuredClone(input);bad.vocabulary.push({word:'bad'});
  await assert.rejects(post(bad));assert.equal((await api('/vocabulary/')).total,2);
  const sample=JSON.parse(read('static/examples/lexiread-vocabulary.json'));assert.equal(decks.normalize(sample).items.length,2);
  assert.match(decks.prompt('Travel','booking a hotel','B1',20),/lexiread-vocabulary/);
  console.log('PASS portable deck validation, preview without writes, duplicate preservation, round-trip export and invalid-file atomicity');
})().catch(error=>{console.error(error);process.exitCode=1;});
