/* Build-time extraction only. Never scan a learner's database or browser storage.
   Install acorn in a separate tooling directory and expose it through NODE_PATH. */
const fs=require('node:fs'),path=require('node:path'),acorn=require('acorn');
const root=path.resolve(__dirname,'..'),sources=new Map();
const vietnamese=/[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/i;
const normalize=s=>s.replace(/\s+/g,' ').trim();
function add(text,file){
  text=normalize(text);if(!vietnamese.test(text)||text.length>2200)return;
  if(!sources.has(text))sources.set(text,new Set());sources.get(text).add(file);
}
function extract(value,file){
  if(!vietnamese.test(value))return;
  if(/<[a-z][^>]*>/i.test(value)){
    for(const m of value.matchAll(/(?:placeholder|aria-label|title|alt)="([^"]*)"/g))add(m[1],file);
    for(const text of value.replace(/<[^>]*>/g,'\n').split('\n'))add(text,file);
  }else add(value,file);
}
function walkAST(node,file){
  if(!node||typeof node!=='object')return;
  // The generated AI prompt is an editable document, not interface copy.
  if(file==='static/personal_decks.js'&&node.type==='FunctionDeclaration'&&node.id?.name==='prompt')return;
  if(node.type==='Literal'&&typeof node.value==='string')extract(node.value,file);
  if(node.type==='TemplateLiteral')extract(node.quasis.map((q,i)=>q.value.cooked+(i<node.expressions.length?`{${i}}`:'')).join(''),file);
  for(const [key,value] of Object.entries(node))if(key!=='quasis'&&value&&typeof value==='object'){
    if(Array.isArray(value))value.forEach(n=>walkAST(n,file));else walkAST(value,file);
  }
}
for(const name of fs.readdirSync(path.join(root,'static')).filter(n=>n.endsWith('.js')&&!n.startsWith('i18n'))){
  const file='static/'+name;walkAST(acorn.parse(fs.readFileSync(path.join(root,file),'utf8'),{ecmaVersion:'latest'}),file);
}
function templates(dir){for(const entry of fs.readdirSync(path.join(root,dir),{withFileTypes:true})){
  const file=dir+'/'+entry.name;
  if(entry.isDirectory())templates(file);
  else if(entry.name.endsWith('.html'))extract(fs.readFileSync(path.join(root,file),'utf8').replace(/{%[\s\S]*?%}/g,'').replace(/{{[\s\S]*?}}/g,'{0}'),file);
}}
templates('templates');
function walkJSON(value,file){
  if(typeof value==='string')add(value,file);
  else if(Array.isArray(value))value.forEach(v=>walkJSON(v,file));
  else if(value&&typeof value==='object')Object.values(value).forEach(v=>walkJSON(v,file));
}
const files=['grammar_lessons.json','grammar_reference.json','strategy_guides.json','study_sources.json','learning_channels.json','vocabulary_collections.json'];
for(const file of files)walkJSON(JSON.parse(fs.readFileSync(path.join(root,'data',file),'utf8')),'data/'+file);
for(const dir of ['lessons','toeic'])for(const file of fs.readdirSync(path.join(root,'data',dir)).filter(n=>n.endsWith('.json')))walkJSON(JSON.parse(fs.readFileSync(path.join(root,'data',dir,file),'utf8')),`data/${dir}/${file}`);
// The versioned runtime pack replaces the optional v1 export.
const pack='data/content_packs/v3/lessons.json.gz';
const packText=require('node:zlib').gunzipSync(fs.readFileSync(path.join(root,pack))).toString('utf8');
walkJSON(JSON.parse(packText),pack);
const output=process.argv[2]||path.join(root,'data/private/localization-build/sources.json');
fs.mkdirSync(path.dirname(output),{recursive:true});
fs.writeFileSync(output,JSON.stringify([...sources].map(([text,files])=>({text,files:[...files]})),null,2)+'\n');
console.log(`${sources.size} authored strings extracted to ${output}`);
