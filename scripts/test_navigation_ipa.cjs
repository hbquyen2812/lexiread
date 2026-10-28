const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {environment}=require('./dom_test_env.cjs');
const read=p=>fs.readFileSync(p,'utf8');
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));

async function main(){
  const dom=environment(),{window}=dom,{document}=window;
  document.body.insertAdjacentHTML('afterbegin','<aside class="sidebar"><button class="mobile-menu-toggle"></button><nav><a href="#guides">Guides</a></nav></aside><button data-sidebar-toggle></button>');
  let resize;const media={matches:true,addEventListener:(type,fn)=>resize=fn};
  window.matchMedia=()=>media;window.LexiI18n={language:'vi'};
  window.localStorage.setItem('lexiread.sidebar.collapsed','true');
  vm.runInNewContext(read('static/navigation.js'),{window,document,localStorage:window.localStorage});
  const aside=document.querySelector('aside'),toggle=document.querySelector('[data-sidebar-toggle]');
  assert.ok(aside.inert);assert.equal(aside.getAttribute('aria-hidden'),'true');
  toggle.click();assert.equal(aside.inert,false);assert.equal(toggle.getAttribute('aria-expanded'),'true');
  toggle.click();assert.equal(window.localStorage.getItem('lexiread.sidebar.collapsed'),'true');
  media.matches=false;resize();assert.equal(aside.inert,false);assert.equal(aside.getAttribute('aria-hidden'),null);
  window.LexiNavigation.toggle();assert.equal(document.querySelector('.mobile-menu-toggle').getAttribute('aria-expanded'),'true');
  document.dispatchEvent(new window.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
  assert.equal(aside.classList.contains('menu-open'),false);
  assert.equal(document.activeElement,document.querySelector('.mobile-menu-toggle'));
  media.matches=true;resize();assert.ok(aside.inert,'mobile state does not override desktop preference');
  window.LexiI18n.language='en';document.dispatchEvent(new window.Event('lexiread:language'));
  assert.equal(toggle.getAttribute('aria-label'),'Open menu');
  console.log('PASS persisted desktop drawer, inert hidden links, responsive state, Escape and translated labels');

  const calls=[];let resolve;
  const api=(path,options)=>{calls.push({path,options});return new Promise(r=>resolve=r);};
  const add=word=>{const span=document.createElement('span');span.className='pronunciation';const button=document.createElement('button');button.dataset.pronounceKind='word';button.dataset.pronounce=word;span.append(button);document.querySelector('main').append(span);return span;};
  add('run');add('RUN');add('ran');
  vm.runInNewContext(read('static/word_ipa.js'),{window,document,api,MutationObserver:window.MutationObserver,setTimeout,clearTimeout});
  await wait(90);assert.equal(calls.length,1);assert.deepEqual(JSON.parse(JSON.stringify(calls[0].options.data.words)),['run','ran']);
  // Render another copy while the same batch is still in flight.
  const fresh=add('run');await wait(90);assert.equal(calls.length,1);
  resolve({items:{run:['/rʌn/','<img src=x onerror=alert(1)>'],ran:[]}});await wait(90);
  assert.equal(fresh.querySelector('.word-ipa').textContent,'/rʌn/ · <img src=x onerror=alert(1)>');
  assert.equal(fresh.querySelector('img'),null,'dictionary content remains plain text');
  assert.equal(document.querySelector('.ipa-lookup').dataset.dictionaryWord,'ran','never display lemma IPA for an inflection');
  document.dispatchEvent(new window.Event('lexiread:language'));
  assert.equal(document.querySelector('.ipa-lookup').textContent,'Look up IPA');
  await wait(120);assert.equal(calls.length,1,'IPA mutations never create a request loop');
  add('run');await wait(100);assert.equal(calls.length,1,'reuse per-page cache');
  console.log('PASS deduplicated IPA batches, stale-view updates, exact headwords, XSS escaping and cache reuse');
  dom.window.close();
}
main().catch(error=>{console.error(error);process.exitCode=1;});
