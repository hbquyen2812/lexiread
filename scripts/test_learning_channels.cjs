const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const scope={URL,window:{},document:{addEventListener(){}}};
vm.runInNewContext(fs.readFileSync('static/learning_channels.js','utf8'),scope);
const ui=scope.window.LexiChannels,items=JSON.parse(fs.readFileSync('data/learning_channels.json','utf8')).channels;
const query=(options={})=>ui.filter(items,{level:'',skill:'',q:'',...options});
assert.equal(query().length,8);
for(const level of ['A1','A2','B1','B2','C1','C2'])assert.ok(query({level}).length);
assert.equal(query({level:'A1',skill:'ielts'}).length,0);
assert.ok(query({level:'B1',skill:'work'}).every(x=>x.id==='oxford-online-english'));
assert.ok(query({q:'phat am'}).some(x=>x.id==='rachels-english'));
assert.ok(query({q:'TOEIC'}).some(x=>x.id==='oxford-online-english'));
assert.equal(query({q:'not-a-channel-123'}).length,0);
const hostile={...items[0],name:'<img src=x onerror=alert(1)>',description_vi:'<script>bad()</script>',mark:'<img>',channel_url:'javascript:alert(1)',start_url:'https://www.youtube.com.evil.test/',source_url:'https://user@www.youtube.com/'};
const card=ui.card(hostile);
assert.doesNotMatch(card,/<img|<script|href="javascript:|youtube\.com\.evil|user@/);
assert.match(card,/&lt;img/);
for(const item of items){const html=ui.card(item);assert.match(html,/rel="noopener noreferrer"/);assert.doesNotMatch(html,/<iframe|<img|<script/);}
assert.match(ui.tabs('youtube'),/href="#guides\/youtube" aria-current="page"/);
console.log('PASS channel level/goal/search combinations, empty results, accessible navigation and safe outbound rendering');
