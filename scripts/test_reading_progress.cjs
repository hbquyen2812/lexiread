/* Exercise the real reading renderer/action with combined filters and pagination. */
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const fields=new Map(Object.entries({
  '#main':{innerHTML:''}, '#catalog-search':{value:'  garden  '},
  '#catalog-topic':{value:'nature'}, '#catalog-favorite':{value:'yes'},
  '#catalog-kind':{value:'tfng'}, '#main .progress-tabs [aria-pressed=true]':{focus(){}}
}));
const requests=[];
const scope={window:{LexiLibrary:{cover:()=>'',levelPicker:()=>'',topicLabel:x=>x,savedLevel:()=>'',saveLevel:x=>x}},
  document:{addEventListener(){}},URLSearchParams,
  state:{routeEpoch:0,libraryTrack:'ielts',ieltsFilters:{level:'B1',status:'started',page:3}},
  $:selector=>fields.get(selector),esc:s=>String(s??'').replace(/[<>&"]/g,c=>({'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c])),
  heading:()=>'',empty:()=>'',api:async url=>{requests.push(new URL('http://local'+url));return {items:[],topics:['nature'],page:1};}};
vm.createContext(scope);vm.runInContext(fs.readFileSync('static/reading_platform.js','utf8'),scope);
(async()=>{
  await scope.platformAct({dataset:{action:'catalog-status',status:'completed'}});
  const first=requests.at(-1).searchParams;
  for(const [key,value] of Object.entries({track:'ielts',status:'completed',level:'B1',topic:'nature',favorite:'yes',q:'garden',kind:'tfng',page:'1'}))assert.equal(first.get(key),value);
  assert.match(fields.get('#main').innerHTML,/data-status="completed" aria-pressed="true"/);
  fields.get('#catalog-search').value='changed';
  await scope.platformAct({dataset:{action:'catalog-filter'}});
  assert.equal(requests.at(-1).searchParams.get('status'),'completed');
  assert.equal(requests.at(-1).searchParams.get('q'),'changed');
  await scope.platformAct({dataset:{action:'catalog-next'}});
  assert.equal(requests.at(-1).searchParams.get('page'),'2');
  assert.equal(requests.at(-1).searchParams.get('status'),'completed');
  const lesson={level:'A1',title:'<script>unsafe</script>',summary:'Short',slug:'sample',question_count:3,word_count:100};
  for(const [status,label,cta] of [['new','Chưa đọc','Bắt đầu'],['started','Đang đọc','Đọc tiếp'],['completed','Đã đọc','Đọc lại']]){
    const html=scope.lessonCard({...lesson,status,reading_id:status==='new'?null:'r1'});
    assert.match(html,new RegExp(label));assert.match(html,new RegExp(cta));assert.doesNotMatch(html,/<script>/);
  }
  console.log('PASS reading status filters preserve search, level, topic, favorite and IELTS type; pagination and distinct read labels');
})().catch(error=>{console.error(error);process.exitCode=1;});
