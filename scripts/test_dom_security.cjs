/* Real sanitizer and DOM integration, including the 11 locations in PR #4. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const acorn = require('acorn');
const {environment} = require('./dom_test_env.cjs');
const read = file => fs.readFileSync(file, 'utf8');
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const tick = () => new Promise(resolve => setImmediate(resolve));
const attack = '<img src=x onerror="alert(1)"><svg onload="alert(2)"></svg>';
const modules = ['academy','app','personal_decks','reading_platform','topic_vocabulary'];

function assertSafe(root) {
  assert.equal(root.querySelector('script,iframe,object,embed,style'), null);
  for (const node of root.querySelectorAll('*')) {
    for (const attr of node.attributes) {
      assert.ok(!/^on/i.test(attr.name), 'no inline event handler: '+attr.name);
      if (['href','src','xlink:href','action','formaction'].includes(attr.name)) {
        assert.doesNotMatch(attr.value.replace(/[\x00-\x20]/g,''), /^(?:javascript|vbscript):/i);
      }
    }
  }
}

function setup() {
  const dom = environment(), {window} = dom, {document} = window;
  window.LexiLibrary = {cover:()=>'',levelPicker:()=>'',topicLabel:x=>x,savedLevel:()=>'',artwork:{school:'',work:'',reading:''}};
  window.LexiMethods = {teaser:()=>'',community:()=>''};
  window.LexiHub = {toeicCatalog:()=>{}};
  const scope = {window,document,URL,URLSearchParams,Blob,FormData:window.FormData,
    state:{routeEpoch:1,boot:{stats:{total:0}},studySettings:{}},
    $:selector=>document.querySelector(selector),esc:escape,
    heading:(title,description='')=>`<h1>${escape(title)}</h1><p>${escape(description)}</p>`,
    empty:()=>'<p>Empty</p>',count:n=>String(Number(n)),dailyReviewCallout:()=>'',
    uid:()=> 'test-token',toast:()=>{},refreshBoot:async()=>{},busy:async(_button,fn)=>fn()};
  vm.createContext(scope);
  for (const name of modules.filter(n=>n!=='app')) vm.runInContext(read(`static/${name}.js`),scope);
  const app=read('static/app.js');
  for (const node of acorn.parse(app,{ecmaVersion:'latest'}).body) {
    if(node.type==='FunctionDeclaration'&&['toeicPage','toeicModeCard'].includes(node.id.name)) vm.runInContext(app.slice(node.start,node.end),scope);
  }
  return {dom,window,document,scope,root:document.querySelector('main')};
}

async function run() {
  // Detect new raw sinks without suppressing the upstream security rules.
  let safeWrites=0;
  for (const name of modules) {
    const ast=acorn.parse(read(`static/${name}.js`),{ecmaVersion:'latest'});
    function walk(node) {
      if(!node||typeof node!=='object')return;
      if(node.type==='AssignmentExpression'&&['innerHTML','outerHTML'].includes(node.left.property?.name)) {
        assert.equal(node.right.type,'Literal',`${name}: dynamic HTML assignment`);
      }
      if(node.type==='CallExpression') {
        assert.notEqual(node.callee.property?.name,'insertAdjacentHTML');
        if(node.callee.property?.name==='fragment')safeWrites++;
      }
      for(const value of Object.values(node)) {
        if(Array.isArray(value))value.forEach(walk);
        else if(value&&typeof value==='object')walk(value);
      }
    }
    walk(ast);
  }
  assert.equal(safeWrites,42);
  assert.equal(read('static/vendor/purify.min.js'),read('node_modules/dompurify/dist/purify.min.js'),'vendored sanitizer matches locked package');
  const template=read('templates/app.html');
  assert.ok(template.indexOf("'vendor/purify.min.js'")<template.indexOf("'safe_dom.js'"));
  for(const name of modules)assert.ok(template.indexOf("'safe_dom.js'")<template.indexOf(`'${name}.js'`));

  const {dom,window,root,scope,document}=setup();
  for(const payload of [attack,'<a href="java&#x09;script:alert(1)">link</a>',
    '<math><mtext><table><mglyph><style><!--</style><img title="--><img src=x onerror=alert(1)>">',
    '<form><button formaction="javascript:alert(1)" onclick="alert(1)">Submit</button></form>',
    '<iframe srcdoc="<script>alert(1)</script>"></iframe><object data="javascript:alert(1)"></object>']) {
    root.replaceChildren(window.LexiDOM.fragment(payload));assertSafe(root);
  }
  root.replaceChildren(window.LexiDOM.fragment('<label><input type="checkbox" checked required data-word="a" aria-label="Choose"></label><p lang="en" data-no-i18n>English stays English.</p><svg viewBox="0 0 24 24"><path d="M1 1h2"/></svg><audio controls src="/static/a.mp3"></audio><a target="_blank" rel="noopener noreferrer" href="https://example.org">Source</a>'));
  assert.ok(root.querySelector('input').checked);assert.ok(root.querySelector('input').required);
  assert.equal(root.querySelector('input').dataset.word,'a');
  assert.ok(root.querySelector('[lang=en][data-no-i18n]'));assert.ok(root.querySelector('svg path'));
  assert.ok(root.querySelector('audio').controls);assert.equal(root.querySelector('a').target,'_blank');assertSafe(root);
  const unsupported={window:{DOMPurify:{isSupported:false,sanitize(){throw Error('must not be called');}}}};
  vm.runInNewContext(read('static/safe_dom.js'),unsupported);
  assert.throws(()=>unsupported.window.LexiDOM.fragment(attack),/Không thể/);
  delete unsupported.window.DOMPurify;
  assert.throws(()=>unsupported.window.LexiDOM.fragment(attack),/Không thể/);
  console.log('PASS pinned sanitizer, all 42 safe DOM writes, XSS vectors, safe attributes and fail-closed behavior');

  const lesson={slug:'test',title:attack,summary:attack,level:'A1',topic:'Travel',word_count:attack,question_count:3};
  scope.api=async url=>url==='/community/'?{}:{items:[lesson],topics:[attack],total:1};
  await scope.readingHome(1);assertSafe(root);assert.ok(root.querySelector('.reading-hero'));
  await scope.catalogPage(1);assertSafe(root);assert.equal(root.querySelector('.lesson-card h3').textContent,attack);
  const groups=[{title:attack,test_kind:'full_reading',exam_type:'ielts',question_count:attack,sections:[{title:attack,href:'javascript:alert(1)'}]}];
  scope.api=async()=>({items:groups});scope.fetch=async()=>({ok:true,json:async()=>[{title:attack,url:'javascript:alert(1)',publisher:attack}]});
  await scope.practiceGroupsPage(1);assertSafe(root);assert.equal(root.querySelector('ol a').getAttribute('href'),null);
  const kind=root.querySelector('[data-practice-kind]');kind.value='external';kind.dispatchEvent(new window.Event('change'));assertSafe(root);
  window.LEXIREAD_PREVIEW={};await scope.practiceGroupsPage(1);assertSafe(root);delete window.LEXIREAD_PREVIEW;
  scope.api=async()=>({items:[]});await scope.toeicPage(1);assert.ok(root.querySelector('.toeic-hero'));assertSafe(root);
  console.log('PASS home, catalogue, TOEIC and practice-group renders, including malicious metadata and links');

  const row={id:'x',title:attack,topic:attack,description:attack,level:'pre-A1',word_count:6};
  scope.api=async()=>({items:[row]});await window.LexiTopics.topics(root,()=>true);assertSafe(root);
  assert.equal(root.querySelector('.topic-course h2').textContent,attack);
  const search=root.querySelector('[data-topic-search]');search.value='missing';search.dispatchEvent(new window.Event('input'));
  assert.equal(root.querySelectorAll('.topic-course').length,0);
  scope.api=async()=>({id:'x',level:attack,title:attack,description:attack,source_urls:['javascript:alert(1)'],
    words:[{word:attack,meaning_vi:attack,example:attack,part_of_speech:'noun'}],questions:[{id:'q1',prompt:attack,options:['one','two','three','four']}]});
  await window.LexiAcademy.detail(root,'vocabulary','x',1);assertSafe(root);
  assert.equal(root.querySelector('.academy-heading h1').textContent,attack);
  assert.ok(root.querySelector('[data-quiz]').hidden);assert.equal(root.querySelectorAll('input[type=radio]').length,4);
  root.querySelector('[data-collection-practice]').click();assert.equal(root.querySelector('[data-quiz]').hidden,false);
  console.log('PASS topic filters, collection metadata, escaped lesson content and working quiz controls');

  window.LexiDecks.page(root);assertSafe(root);assert.ok(root.querySelector('input[type=file]'));
  const deck=window.LexiDecks.sample(attack);deck.vocabulary[0].word=attack;deck.vocabulary[0].meaning_vi=attack;
  root.querySelector('#deck-paste').value=JSON.stringify(deck);
  scope.api=async(_url,options)=>options.data.preview?{name:deck.deck.name,new:attack,existing:0,duplicates:0,items:deck.vocabulary}:{created:1,existing:0};
  root.querySelector('[data-deck-action=preview]').click();await tick();await tick();assertSafe(root);
  assert.equal(root.querySelector('[data-deck-preview] h2').textContent,attack);
  assert.equal(root.querySelectorAll('[data-deck-index]:checked').length,2);
  root.querySelector('[data-deck-index="1"]').checked=false;
  let saved;
  scope.api=async(_url,options)=>{saved=options.data.deck;return {created:1,existing:0};};
  root.querySelector('[data-deck-action=save]').click();await tick();await tick();assertSafe(root);
  assert.equal(saved.vocabulary.length,1);assert.equal(saved.vocabulary[0].word,attack);
  assert.ok(root.querySelector('.deck-success'));
  dom.window.close();
  console.log('PASS imported hostile text stays literal, preview selection and saving still work');
}
run().catch(error=>{console.error(error);process.exitCode=1;});
