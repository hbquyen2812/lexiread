/* Real DOM regression tests, without a browser or network. npm ci; npm run test:i18n */
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {parseHTML}=require('linkedom');
const read=name=>fs.readFileSync(name,'utf8');
const tick=()=>new Promise(resolve=>setImmediate(resolve));

async function main(){
  const {window}=parseHTML(`<html lang="vi"><body>
    <button id="label">Học ngữ pháp</button><button id="key" data-i18n="auth.submit"></button>
    <p id="count">Câu 6</p><p id="spaces">  Học   ngữ pháp  </p>
    <a id="account" aria-label="Tài khoản của tôi" title="Tài khoản của tôi">Tài khoản của tôi</a>
    <p id="english" lang="en">I like music. Học ngữ pháp</p>
    <div data-no-i18n><span id="protected-key" data-i18n="auth.submit">Học ngữ pháp</span></div>
    <p id="mixed" data-i18n="auth.submit">Học ngữ pháp <b lang="en">am/is/are</b></p>
    <textarea id="draft" placeholder="Tìm bài học">Học ngữ pháp</textarea>
    <input id="typed" value="Học ngữ pháp"><input id="answer" type="radio" name="q1" value="1">
    <span id="personal" data-no-i18n>Học ngữ pháp</span>
    <table><tbody><tr><td id="meaning">Học ngữ pháp</td><td lang="en" id="verb">read / read / read</td></tr></tbody></table>
    <div id="late"></div><div id="lesson"></div>
  </body></html>`);
  const {document}=window,values=new Map(),storageListeners={};
  // Keep the DOM implementation separate from the VM's browser globals.
  const appWindow={addEventListener:(event,fn)=>storageListeners[event]=fn};
  const scope={URL,window:appWindow,document,NodeFilter:{SHOW_TEXT:4},MutationObserver:window.MutationObserver,
    requestAnimationFrame:fn=>queueMicrotask(fn),CustomEvent:window.CustomEvent,
    localStorage:{getItem:key=>values.get(key),setItem:(key,value)=>values.set(key,value)}};
  vm.runInNewContext(read('static/i18n_catalog.js'),scope);
  vm.runInNewContext(read('static/i18n.js'),scope);
  for(const script of ['grammar_reference','grammar_course','academy'])vm.runInNewContext(read(`static/${script}.js`),scope);
  const i18n=appWindow.LexiI18n;
  document.dispatchEvent(new window.Event('DOMContentLoaded'));
  const lessons=JSON.parse(read('data/grammar_lessons.json')).lessons;
  const lesson={...lessons[0],is_read:false};
  document.querySelector('#lesson').innerHTML=appWindow.LexiGrammar.lessonHTML(lesson,'',appWindow.LexiAcademy.quizHTML(lesson.questions));
  const quizRadio=document.querySelector('.academy-quiz input');quizRadio.checked=true;
  document.querySelector('#answer').checked=true;
  const texts=()=>[...document.body.querySelectorAll('[lang="en"],[data-no-i18n]')].map(el=>el.textContent);
  const originalEnglish=texts(),originalLesson=document.querySelector('#lesson').textContent;
  const prompt=lesson.questions[0].prompt;
  for(const [lang,label,question,title] of [
    ['en','Learn grammar','Question 6','How do English sentences work?'],
    ['fr','Apprendre la grammaire','Question 6','Comment construire une phrase en anglais ?'],
    ['zh','学习语法','第 6 题','英语句子是怎样构成的？']
  ]){
    i18n.setLanguage(lang);await tick();
    assert.equal(document.documentElement.lang,lang==='zh'?'zh-Hans':lang);
    assert.equal(document.querySelector('#label').textContent,label);
    assert.equal(document.querySelector('#meaning').textContent,label);
    assert.equal(document.querySelector('#count').textContent,question);
    assert.equal(document.querySelector('#spaces').textContent,`  ${label}  `);
    assert.equal(i18n.translate(lesson.title),title);
    assert.notEqual(document.querySelector('.academy-question-heading p').textContent,prompt);
    assert.ok(document.querySelector('.academy-question-heading p').textContent.includes('“Lan likes music”'));
    assert.deepEqual(texts(),originalEnglish,'English examples, options, and personal data must stay unchanged');
    assert.equal(document.querySelector('#draft').value,'Học ngữ pháp');
    assert.equal(document.querySelector('#typed').value,'Học ngữ pháp');
    assert.equal(document.querySelector('#answer').checked,true);
    assert.equal(quizRadio.checked,true,'Switching language must not replace the quiz');
    assert.notEqual(document.querySelector('#account').title,'Tài khoản của tôi');
    assert.equal(values.get('lexiread.language'),lang);
  }
  i18n.setLanguage('vi');await tick();
  assert.equal(document.querySelector('#lesson').textContent,originalLesson,'Lossless Vietnamese round trip');
  assert.equal(document.querySelector('#spaces').textContent,'  Học   ngữ pháp  ');
  assert.equal(document.querySelector('#account').title,'Tài khoản của tôi');
  i18n.setLanguage('en');
  assert.equal(document.querySelector('#draft').getAttribute('placeholder'),'Find a lesson');
  document.querySelector('#late').innerHTML='<button title="Tài khoản của tôi">Học ngữ pháp</button>';
  await tick();await tick();
  assert.equal(document.querySelector('#late button').textContent,'Learn grammar');
  assert.equal(document.querySelector('#late button').title,'My account');
  document.querySelector('#late button').textContent='Câu 27';await tick();await tick();
  assert.equal(document.querySelector('#late button').textContent,'Question 27');
  storageListeners.storage({key:'lexiread.language',newValue:'fr'});await tick();
  assert.equal(document.querySelector('#late button').textContent,'Question 27');
  assert.equal(document.querySelector('#label').textContent,'Apprendre la grammaire');
  i18n.setLanguage('invalid');assert.equal(i18n.language,'fr');
  vm.runInNewContext(read('static/dictionary.js'),scope);
  document.querySelector('#late').innerHTML=appWindow.LexiDictionary.render({word:'routine',
    local_entries:[{label:'Đã lưu',word:'routine',meaning_vi:'Từ vựng',example_vi:'Tôi thích âm nhạc.'}],
    dictionary:{status:'ok',entries:[{phonetics:[],meanings:[{pos:'noun',definitions:[{definition:'an unvarying or habitual method or procedure'}]}],sources:[],license:{name:'CC BY 4.0',url:'https://creativecommons.org/licenses/by/4.0/'}}]}});
  await tick();await tick();
  assert.equal(document.querySelector('.dictionary-section-title').textContent,'Définitions en anglais');
  assert.equal(document.querySelector('.dictionary-local strong').textContent,'Từ vựng');
  assert.equal(document.querySelector('.dictionary-senses').textContent,'an unvarying or habitual method or procedure');

  const catalog=appWindow.LEXI_INTERFACE_LOCALES;
  for(const [source,...translations] of catalog){
    assert.equal(translations.length,3);
    assert.ok(translations.every(t=>typeof t==='string'&&t.trim()),source);
    const placeholders=s=>(s.match(/\{\d+\}/g)||[]).sort();
    for(const text of translations){assert.deepEqual(placeholders(text),placeholders(source),source);assert.doesNotMatch(text,/__TERM\d+__|XQZ\d+QZX/);}
  }
  console.log(`PASS ${catalog.length} local translations; all 4 languages, dynamic content, attributes, English boundaries, personal data and quiz state`);
}
main().catch(error=>{console.error(error);process.exitCode=1;});
