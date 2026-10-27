const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),acorn=require('acorn');
const {environment}=require('./dom_test_env.cjs');
const read=file=>fs.readFileSync(file,'utf8');
const dom=environment(),{window}=dom,{document}=window;
const scope={window,document,state:{boot:{user:'Learner <img src=x onerror=alert(1)>',ai_enabled:false}},
  $:selector=>document.querySelector(selector),esc:value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))};
vm.createContext(scope);vm.runInContext(read('static/visuals.js'),scope);
const app=read('static/app.js');
for(const node of acorn.parse(app,{ecmaVersion:'latest'}).body){
  if(node.type==='FunctionDeclaration'&&node.id.name==='settingsPage')vm.runInContext(app.slice(node.start,node.end),scope);
  if(node.type==='ExpressionStatement'&&node.expression.callee?.object?.name==='document'&&node.expression.callee.property?.name==='addEventListener'&&node.expression.arguments[0]?.value==='change')vm.runInContext(app.slice(node.start,node.end),scope);
}
scope.settingsPage();
assert.equal(document.querySelector('h2[data-no-i18n]').textContent,scope.state.boot.user);
assert.equal(document.querySelectorAll('[onerror],script').length,0);
assert.ok(document.querySelector('[data-action=import-library]').disabled);
assert.equal(document.querySelector('details.settings-restore').open,false);
assert.equal(document.querySelector('details.settings-privacy').open,false);
const input=document.querySelector('#import-file');
Object.defineProperty(input,'files',{configurable:true,value:[new window.File(['{}'],'my-backup.json')]});
input.dispatchEvent(new window.Event('change',{bubbles:true}));
assert.equal(document.querySelector('#restore-filename').textContent,'my-backup.json');
assert.equal(document.querySelector('[data-action=import-library]').disabled,false);
Object.defineProperty(input,'files',{configurable:true,value:[]});input.dispatchEvent(new window.Event('change',{bubbles:true}));
assert.ok(document.querySelector('[data-action=import-library]').disabled);
for(const value of ['book','coffee','deadline','abstract concept','../../secret','<img src=x onerror=alert(1)>']){
  const box=document.createElement('div');box.replaceChildren(window.LexiDOM.fragment(window.LexiVisuals.word(value)));
  const image=box.querySelector('img');assert.ok(image);assert.equal(image.alt,'');
  assert.match(image.getAttribute('src'),/^\/static\/illustrations\/words\/[a-z]+\.svg$/);
  assert.ok(fs.existsSync('.'+image.getAttribute('src')));
}
const methods={window:{}};vm.runInNewContext(read('static/learning_methods.js'),{...methods,document:{addEventListener(){}}});
assert.doesNotMatch(methods.window.LexiMethods.community({active_learners:1,practice_attempts:2,word_reviews:3}),/Cách tính số liệu|<details>/);
dom.window.close();
console.log('PASS compact settings, safe local illustrations, restored-file selection and concise activity statistics');
