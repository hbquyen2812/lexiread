const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');

async function lookupLifecycle(){
  const listeners={},requests=[],editors=[];
  let result,button;const modal={open:false};
  const scope={URL,window:{},document:{
    addEventListener(name,handler){listeners[name]=handler;},
    querySelectorAll(){return [];},querySelector(){return button;},
    getElementById(id){return id==='modal'?modal:result;}
  },openModal(title,content,footer){
    if(result)result.isConnected=false;
    result={isConnected:true,innerHTML:content,querySelectorAll(){return [];}};
    button={disabled:footer.includes(' disabled'),dataset:{dictionarySave:'new'}};modal.open=true;
  },api(){return new Promise((resolve,reject)=>requests.push({resolve,reject}));},
  toast(){},blankEntry:()=>({meaning_vi:''}),editor:entry=>editors.push(entry)};
  vm.runInNewContext(fs.readFileSync('static/dictionary.js','utf8'),scope);
  const clickSave=()=>listeners.click({target:{closest:selector=>selector==='[data-dictionary-save]'?button:null}});
  const first=scope.window.LexiDictionary.open({word:'routine',reading_id:'reading-1',context:'My morning routine.'});
  assert.equal(button.disabled,true);clickSave();assert.equal(editors.length,0);
  requests[0].resolve({word:'routine',local_entries:[{word:'routine',meaning_vi:'thói quen'}],dictionary:{status:'ok',entries:[]}});
  await first;assert.equal(button.disabled,false);clickSave();
  assert.equal(editors[0].meaning_vi,'thói quen');assert.equal(editors[0].reading_id,'reading-1');assert.equal(editors[0].context,'My morning routine.');

  const older=scope.window.LexiDictionary.open({word:'book'}),oldButton=button;
  const newer=scope.window.LexiDictionary.open({word:'travel'});
  requests[1].resolve({word:'book',local_entries:[{meaning_vi:'sách'}],dictionary:{entries:[]}});await older;
  assert.equal(button.disabled,true);assert.equal(oldButton.disabled,true);clickSave();assert.equal(editors.length,1);
  requests[2].resolve({word:'travel',local_entries:[{meaning_vi:'du lịch'}],dictionary:{entries:[]}});await newer;
  clickSave();assert.equal(editors[1].word,'travel');assert.equal(editors[1].meaning_vi,'du lịch');

  const failed=scope.window.LexiDictionary.open({word:'unavailable'});
  requests[3].reject(new Error('Tạm thời không tra được.'));await failed;
  assert.equal(button.disabled,false);assert.match(button.textContent,/Nhập nghĩa thủ công/);clickSave();
  assert.equal(editors[2].word,'unavailable');assert.equal(editors[2].meaning_vi,'');
  modal.open=false;clickSave();assert.equal(editors.length,3);
  console.log('PASS pending dictionary save, meaning/context retention, overlapping lookup and explicit error fallback');
}

function selectionLifecycle(){
  const nodes={'#modal':{open:false},'#selection-bar':{hidden:true},'#selected-word':{},'[data-action=selected-dictionary]':{},'[data-action=selected-word]':{}};
  const paragraph={dataset:{index:'0'}},outside={nodeType:1,closest:()=>null};
  const inside={nodeType:1,closest:()=>paragraph};
  let selection;
  const scope={state:{reading:{id:'r1',title:'Reading',paragraphs:['A small routine.']},selection:null},
    window:{getSelection:()=>selection,LexiDictionary:{canLookup:()=>true}},$:key=>nodes[key]};
  const source=fs.readFileSync('static/app.js','utf8');
  vm.runInNewContext(source.slice(source.indexOf('function clearSelection()'),source.indexOf('function cloudConsent(')),scope);
  const select=()=>{selection={isCollapsed:false,anchorNode:inside,focusNode:inside,toString:()=> 'routine'};scope.captureSelection();};
  for(const invalid of [null,{isCollapsed:true},{isCollapsed:false,anchorNode:outside,focusNode:outside},
    {isCollapsed:false,anchorNode:inside,focusNode:outside},
    {isCollapsed:false,anchorNode:inside,focusNode:inside,toString:()=> 'x'.repeat(4001)}]){
    select();assert.equal(scope.state.selection.word,'routine');assert.equal(nodes['#selection-bar'].hidden,false);
    selection=invalid;scope.captureSelection();assert.equal(scope.state.selection,null);assert.equal(nodes['#selection-bar'].hidden,true);
  }
  select();nodes['#modal'].open=true;selection={isCollapsed:true};scope.captureSelection();assert.equal(scope.state.selection.word,'routine');
  nodes['#modal'].open=false;scope.state.reading=null;scope.captureSelection();assert.equal(scope.state.selection,null);
  console.log('PASS valid contextual selection, clearing outside/collapsed/oversize ranges and preserving modal context');
}
lookupLifecycle().then(selectionLifecycle).catch(error=>{console.error(error);process.exitCode=1;});
