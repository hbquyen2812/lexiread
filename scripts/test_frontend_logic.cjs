/* Node-only logic checks, not a browser or visual/layout test. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const load=p=>JSON.parse(read(p));
const lessons=fs.readdirSync(path.join(root,'data/lessons')).filter(p=>p.endsWith('.json')).map(p=>load('data/lessons/'+p));
const storage=new Map();
const localStorage={getItem:key=>storage.get(key)||null,setItem:(key,value)=>storage.set(key,String(value))};

async function run(){
  const seed={words:[],text:'A private test paragraph.',analysis:{},lessons,toeic_sets:[]};
  const scope={PREVIEW_SEED:seed,localStorage,crypto:webcrypto,URL,URLSearchParams,FormData,setTimeout,window:{}};
  vm.runInNewContext(read('scripts/preview_adapter.js'),scope);
  const api=scope.window.LEXIREAD_PREVIEW.api;
  assert.equal((await api('/catalog/?track=general')).items.length,24);
  assert.equal((await api('/catalog/?track=ielts')).items.length,lessons.filter(l=>l.track==='ielts').length);
  const filtered=await api('/catalog/?track=ielts&kind=tfng');
  assert.ok(filtered.items.length>0);
  assert.ok(filtered.items.every(l=>l.question_types.includes('tfng')));
  assert.ok(filtered.items.every(l=>Number.isInteger(l.estimated_minutes)&&l.estimated_minutes>=5));
  assert.equal((await api('/catalog/?track=general&level=A2')).items.length,6);
  const paged=await api('/catalog/?track=general&limit=5&page=2');
  assert.equal(paged.items.length,5);assert.equal(paged.total,24);assert.equal(paged.has_more,true);
  const gap=structuredClone(lessons.find(l=>l.slug==='a-quiet-start'));
  gap.slug='logic-test-gap';gap.editorial={original:{answer:'private'}};
  gap.questions=[{id:'q1',kind:'gap_fill',prompt:'Name it.',options:[],answer:'routine',accepted_answers:['routine'],max_words:1,paragraph_index:0,evidence:'routine',explanation_vi:'Test'}];
  seed.lessons.push(gap);
  const reading=await api('/catalog/logic-test-gap/open/',{method:'POST',data:{}});
  assert.equal(reading.lesson.questions[0].max_words,1);
  assert.equal('answer' in reading.lesson.questions[0],false);assert.equal('editorial' in reading.lesson,false);
  const result=await api(`/readings/${reading.id}/quiz/`,{method:'POST',data:{token:webcrypto.randomUUID(),answers:{q1:' ROUTINE '}}});
  assert.equal(result.score,1);
  const wrong=await api(`/readings/${reading.id}/quiz/`,{method:'POST',data:{token:webcrypto.randomUUID(),answers:{q1:'morning routine'}}});
  assert.equal(wrong.score,0);
  console.log('PASS offline catalogue/track/pagination, text-answer scoring and private metadata');

  const doc={documentElement:{lang:'vi'},body:{},querySelectorAll:()=>[],createTreeWalker:()=>({nextNode:()=>false}),addEventListener:()=>{},dispatchEvent:()=>{}};
  const locale={window:{addEventListener:()=>{}},document:doc,localStorage,NodeFilter:{SHOW_TEXT:4},CustomEvent:class{}};
  vm.runInNewContext(read('static/i18n.js'),locale);
  const i18n=locale.window.LexiI18n;
  assert.equal(i18n.language,'vi');
  for(const [lang,title] of [['en','A good read at your level.'],['fr','Une lecture à votre portée.'],['zh','找到适合你的阅读。'],['vi','Một bài đọc vừa sức với bạn.']]){
    i18n.setLanguage(lang);assert.equal(i18n.t('library.title'),title);assert.equal(storage.get('lexiread.language'),lang);
  }
  i18n.setLanguage('invalid');assert.equal(i18n.language,'vi');
  assert.match(read('static/i18n.js'),/\[lang="en"\]:not\(html\)/);
  console.log('PASS four language dictionaries, Vietnamese default, preference persistence, invalid locale rejection');

  // Exercise the real HTML render helpers without a browser. No claim of visual QA.
  const app=read('static/app.js');
  const escape=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const lexicalScope={window:{},esc:escape,asList:value=>Array.isArray(value)?value:[]};
  vm.runInNewContext(app.slice(app.indexOf('function lexicalRelations'),app.indexOf('function blankEntry')),lexicalScope);
  const word={word:'depend',usage_pattern:'depend on + noun',example:'We depend on clean water.',context:'SOURCE PARAGRAPH '.repeat(100),synonyms:['rely'],paraphrases:['need something']};
  const html=lexicalScope.lexicalDetails(word);
  assert.match(html,/depend on \+ noun/);assert.match(html,/We depend on clean water/);
  assert.match(html,/rely/);assert.match(html,/need something/);assert.doesNotMatch(html,/SOURCE PARAGRAPH/);
  assert.match(lexicalScope.lexicalContext(word),/<details/);
  assert.doesNotMatch(lexicalScope.lexicalDetails({...word,example:word.context}),/SOURCE PARAGRAPH/);
  assert.doesNotMatch(lexicalScope.lexicalDetails({...word,example:'<img src=x onerror=alert(1)>',usage_pattern:'<script>x</script>'}),/<img|<script>/);
  const cardBody=app.slice(app.indexOf('content+=`<div class="flashcard"'),app.indexOf('}else if(s.question)'));
  assert.match(cardBody,/lexicalDetails\(v,false\)/);assert.match(cardBody,/<\/div>\$\{s.flipped&&!s.readingId\?lexicalContext\(v\)/);
  assert.doesNotMatch(cardBody,/esc\(v\.context\)/);
  const settingsHTML=app.slice(app.indexOf('function settingsPage'),app.indexOf('function download'));
  for(const forbidden of ['.env','OPENAI_API_KEY','docker compose','PostgreSQL','pg_dump','gpt-4.1'])assert.equal(settingsHTML.includes(forbidden),false);
  assert.match(settingsHTML,/\/account\//);assert.match(settingsHTML,/\/account\/password\//);
  assert.doesNotMatch(settingsHTML,/Không có analytics/);
  const profile=read('templates/registration/profile.html');assert.match(profile,/form.as_p/);
  for(const lang of ['vi','en','fr','zh']){i18n.setLanguage(lang);assert.notEqual(i18n.t('account.title'),'account.title');assert.notEqual(i18n.t('auth.signup'),'auth.signup');}
  console.log('PASS compact lexical cards, optional source context, XSS escaping, learner settings and account dictionaries');
}
run().catch(error=>{console.error(error);process.exitCode=1;});
