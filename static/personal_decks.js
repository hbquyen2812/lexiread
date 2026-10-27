'use strict';
/* A portable file workflow. Copying a prompt never calls an external AI service. */
(() => {
  const FORMAT='lexiread-vocabulary',LIMIT=500,MAX_BYTES=2*1024*1024;
  const fields={word:160,pos:40,meaning_vi:2000,usage_pattern:300,example:2000,example_vi:2000,context:4000,note:4000};
  const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const key=v=>[v.word,v.meaning_vi].map(x=>x.normalize('NFKC').trim().toLowerCase().replace(/\s+/g,' ')).join('\u001f');
  const sample=(name='Bộ từ mẫu')=>({format:FORMAT,version:1,deck:{name},vocabulary:[
    {word:'confirm',pos:'verb',meaning_vi:'xác nhận',usage_pattern:'confirm + a booking / an appointment',example:'Please confirm your appointment by Friday.',example_vi:'Bạn vui lòng xác nhận lịch hẹn trước thứ Sáu nhé.',synonyms:['verify'],paraphrases:['say that something is certain'],context:'',note:'Verify thường nhấn mạnh việc kiểm tra tính chính xác.'},
    {word:'reschedule',pos:'verb',meaning_vi:'đổi lịch',usage_pattern:'reschedule a meeting for + time',example:'We rescheduled the meeting for Monday.',example_vi:'Chúng tôi đã chuyển cuộc họp sang thứ Hai.',synonyms:['rearrange'],paraphrases:['move an event to another time'],context:'',note:''}
  ]});
  function normalize(payload){
    if(!payload||payload.format!==FORMAT||payload.version!==1||!payload.deck||typeof payload.deck.name!=='string')throw new Error('File chưa đúng mẫu bộ từ LexiRead. Bạn tải mẫu ở bước 1 để đối chiếu nhé.');
    const name=payload.deck.name.normalize('NFC').trim();if(!name||name.length>100)throw new Error('Tên bộ từ cần từ 1 đến 100 ký tự.');
    if(!Array.isArray(payload.vocabulary)||!payload.vocabulary.length||payload.vocabulary.length>LIMIT)throw new Error('Mỗi bộ cần từ 1 đến 500 từ hoặc cụm từ.');
    const items=[],seen=new Set();let duplicates=0;
    payload.vocabulary.forEach((raw,index)=>{
      if(!raw||typeof raw!=='object'||Array.isArray(raw))throw new Error(`Từ số ${index+1} chưa đúng cấu trúc.`);
      const v={};for(const [field,max] of Object.entries(fields)){const value=raw[field]??'';if(typeof value!=='string'||value.length>max)throw new Error(`Từ số ${index+1}: mục ${field} cần là văn bản, tối đa ${max} ký tự.`);v[field]=value.normalize('NFC').replaceAll('\u0000','').trim();}
      if(!v.word||!v.meaning_vi)throw new Error(`Từ số ${index+1} thiếu từ tiếng Anh hoặc nghĩa tiếng Việt.`);
      if(v.word.split(/\s+/).length>16)throw new Error(`Từ số ${index+1} quá dài. Mỗi cụm chỉ nên có tối đa 16 từ.`);
      for(const field of ['synonyms','paraphrases']){let list=raw[field]??[];if(typeof list==='string')list=list.split('|').map(x=>x.trim()).filter(Boolean);if(!Array.isArray(list)||list.length>20||list.some(x=>typeof x!=='string'||x.length>300))throw new Error(`Từ số ${index+1}: kiểm tra danh sách ${field}.`);v[field]=[...new Set(list.map(x=>x.trim()).filter(Boolean))];}
      v.tags=[name];v.source_label=name;v.origin='import';v.verified=false;
      const fp=key(v);if(seen.has(fp)){duplicates++;return;}seen.add(fp);items.push(v);
    });return {name,items,duplicates};
  }
  const pack=(name,items)=>({format:FORMAT,version:1,deck:{name},vocabulary:items.map(v=>Object.fromEntries([...Object.keys(fields),'synonyms','paraphrases'].map(k=>[k,v[k]??(['synonyms','paraphrases'].includes(k)?[]:'')])))});
  function prompt(name,topic,level,count){
    return `Hãy tạo một bộ ${count} từ hoặc cụm từ tiếng Anh về chủ đề ${topic}, phù hợp trình độ ${level}, để tôi nhập vào LexiRead và ôn bằng flashcard.
Tên bộ: ${name}.
Chọn từ thông dụng, hữu ích, không lặp. Mỗi mục chỉ tập trung vào một nghĩa. Giải nghĩa và dịch ví dụ sang tiếng Việt tự nhiên, dễ đọc, tránh dịch từng chữ. Giữ đúng nghĩa và sắc thái.
Với mỗi từ: ghi từ loại, nghĩa tiếng Việt, một cấu trúc hay dùng, một ví dụ tiếng Anh ngắn phù hợp trình độ và bản dịch. Có thể thêm 1–3 từ gần nghĩa và 1–2 cách diễn đạt tương đương; nếu không phù hợp thì để danh sách rỗng. Chỉ ghi lưu ý khi thật sự cần; không bịa từ gần nghĩa. Tự viết ví dụ, không sao chép bài đọc dài. Để context rỗng nếu tôi chưa cung cấp câu gốc.
Xuất một file UTF-8 tên lexiread-vocabulary.json theo đúng cấu trúc bên dưới. Thay hai từ mẫu bằng ${count} mục mới. Không thêm trường, không đưa lịch ôn hoặc thông tin tài khoản. Nếu không tạo được file tải xuống, chỉ trả một khối JSON để tôi sao chép và lưu thành file .json.
${JSON.stringify(sample(name),null,2)}`;
  }
  let current=null;
  function page(root){
    current={root,preview:null};root.innerHTML=`<a class="link-btn" href="#vocabulary">← Kho từ của tôi</a><div class="hub-heading"><h1>Tạo bộ từ của bạn</h1><p>Nhờ AI soạn từ theo chủ đề bạn thích, rồi mang về đây để ôn mỗi ngày.</p></div><div class="deck-workflow"><section class="deck-step"><span class="eyebrow">BƯỚC 1 · NHỜ AI SOẠN TỪ</span><h2>Bạn muốn học về điều gì?</h2><div class="form-grid"><label>Tên bộ từ<input id="deck-name" maxlength="100" placeholder="Ví dụ: TOEIC · Email công việc"></label><label>Chủ đề<input id="deck-topic" maxlength="200" placeholder="Ví dụ: viết email và sắp xếp cuộc họp"></label><label>Trình độ<select id="deck-level">${['A1','A2','B1','B2','C1'].map(x=>`<option ${x==='B1'?'selected':''}>${x}</option>`).join('')}</select></label><label>Số từ muốn tạo<select id="deck-count">${[20,40,60,100].map(n=>`<option>${n}</option>`).join('')}</select></label></div><div class="button-row"><button class="btn primary" type="button" data-deck-action="prompt">Sao chép prompt cho AI</button><button class="btn" type="button" data-deck-action="sample">Tải file mẫu</button></div><p class="fineprint">Dán prompt vào ChatGPT, Gemini hoặc AI bạn đang dùng. Khi có kết quả, tải file JSON về. </p><details id="deck-prompt-details" hidden><summary>Xem hoặc sao chép prompt</summary><textarea id="deck-prompt" rows="10" readonly aria-label="Prompt tạo bộ từ"></textarea></details><p data-deck-prompt-status role="status"></p></section><section class="deck-step"><span class="eyebrow">BƯỚC 2 · MANG BỘ TỪ VỀ ĐÂY</span><h2>Chọn file AI vừa tạo</h2><label>File bộ từ<input id="deck-file" type="file" accept=".json,application/json"></label><p class="fineprint">File JSON, tối đa 2 MB và 500 mục. Chưa có file? Bạn có thể dán kết quả bên dưới.</p><details><summary>Dán nội dung JSON</summary><textarea id="deck-paste" rows="8" placeholder="Dán khối JSON AI đã tạo…" aria-label="Nội dung bộ từ"></textarea></details><p><button class="link-btn" type="button" data-action="bulk-open">Nhập nhanh danh sách từ có sẵn</button></p><div class="button-row"><button class="btn primary" type="button" data-deck-action="preview">Xem trước bộ từ</button></div><p data-deck-error role="alert"></p></section></div><section class="deck-preview" data-deck-preview hidden></section>`;
  }
  function renderPreview(result){
    const root=current.root.querySelector('[data-deck-preview]');root.hidden=false;
    root.innerHTML=`<span class="eyebrow">BƯỚC 3 · CHỌN TỪ MUỐN GIỮ</span><h2 data-no-i18n>${escape(result.name)}</h2><p>${result.new} từ mới · ${result.existing} từ đã có${result.duplicates?' · '+result.duplicates+' mục trùng trong file đã gộp':''}.</p><p class="fineprint">Đọc lại nghĩa và ví dụ trước khi lưu. Từ đã có sẽ được thêm vào bộ này, giữ nguyên nội dung và lịch ôn của bạn.</p><label class="check-label"><input type="checkbox" data-deck-all checked> Chọn tất cả</label><div class="deck-word-list">${result.items.map((v,i)=>`<article class="deck-word"><label class="check-label"><input type="checkbox" data-deck-index="${i}" checked aria-label="Chọn ${escape(v.word)}"><strong lang="en">${escape(v.word)}</strong><span class="chip">${v.exists?'Đã có':'Mới'}</span></label><p data-no-i18n>${escape(v.meaning_vi)}</p>${v.example?`<p lang="en">${escape(v.example)}</p><p class="muted" data-no-i18n>${escape(v.example_vi)}</p>`:''}<details><summary>Cách dùng và ghi chú</summary><p lang="en">${escape(v.usage_pattern)}</p><p ${v.note?'data-no-i18n':''}>${escape(v.note)||'Chưa có ghi chú thêm.'}</p></details></article>`).join('')}</div><div class="button-row"><button class="btn primary" type="button" data-deck-action="save">Lưu bộ từ vào kho của tôi</button></div><p data-deck-save-status role="status"></p>`;
    root.scrollIntoView({behavior:'smooth',block:'start'});
  }
  async function action(button){
    if(!current||!current.root.isConnected)return;
    const flow=current,epoch=state.routeEpoch,revision=flow.revision||0;
    const active=()=>current===flow&&state.routeEpoch===epoch&&(flow.revision||0)===revision;
    const root=flow.root,get=id=>root.querySelector('#'+id),message=root.querySelector('[data-deck-error]');if(!message)return;message.textContent='';
    const name=get('deck-name').value.trim();
    if(button.dataset.deckAction==='sample'){download('lexiread-vocabulary-mau.json',sample(name||'Bộ từ mẫu'));return;}
    if(button.dataset.deckAction==='prompt'){
      const topic=get('deck-topic').value.trim();if(!name||!topic)throw new Error('Bạn điền tên bộ từ và chủ đề trước nhé.');
      const text=prompt(name,topic,get('deck-level').value,Number(get('deck-count').value));get('deck-prompt').value=text;get('deck-prompt-details').hidden=false;
      try{await navigator.clipboard.writeText(text);if(active())root.querySelector('[data-deck-prompt-status]').textContent='Đã sao chép. Bạn dán vào AI để bắt đầu nhé.';}catch{if(active()){get('deck-prompt-details').open=true;get('deck-prompt').focus();get('deck-prompt').select();root.querySelector('[data-deck-prompt-status]').textContent='Bạn sao chép prompt trong ô phía trên nhé.';}}return;
    }
    if(button.dataset.deckAction==='preview'){
      await busy(button,async()=>{
        const file=get('deck-file').files[0];if(file&&(file.size>MAX_BYTES||!file.name.toLowerCase().endsWith('.json')))throw new Error('Bạn chọn file .json không quá 2 MB nhé.');
        let text=file?await file.text():get('deck-paste').value;if(!active())return;if(new Blob([text]).size>MAX_BYTES)throw new Error('Nội dung quá lớn. Mỗi lần nhập tối đa 2 MB.');
        text=text.replace(/^\uFEFF/,'').trim().replace(/^```(?:json)?\s*/i,'').replace(/\s*```$/,'');
        let data;try{data=JSON.parse(text);}catch{throw new Error('Chưa đọc được file. Hãy dùng đúng khối JSON hoặc file mẫu ở bước 1.');}
        if(name&&data&&typeof data==='object')data.deck={name};
        normalize(data);
        const result=await api('/vocabulary/deck/',{method:'POST',data:{preview:true,deck:data}});
        if(!active())return;flow.preview=result;get('deck-name').value=result.name;renderPreview(result);
      },'Đang kiểm tra…');return;
    }
    if(button.dataset.deckAction==='save'){
      if(!current.preview)throw new Error('Bạn xem trước bộ từ trước nhé.');
      const items=[...root.querySelectorAll('[data-deck-index]:checked')].map(x=>current.preview.items[Number(x.dataset.deckIndex)]);
      if(!items.length)throw new Error('Bạn chọn ít nhất một từ để lưu nhé.');
      await busy(button,async()=>{
        const result=await api('/vocabulary/deck/',{method:'POST',data:{preview:false,deck:pack(flow.preview.name,items)}});await refreshBoot();if(!active())return;
        root.querySelector('[data-deck-preview]').innerHTML=`<section class="deck-success"><h2>Đã có bộ từ của bạn!</h2><p>${result.created} từ mới đã được lưu. ${result.existing?result.existing+' từ đã có được thêm vào bộ, giữ nguyên lịch ôn.':''}</p><div class="button-row"><button class="btn primary" type="button" data-deck-action="study">Ôn bộ từ này</button><button class="btn" type="button" data-deck-action="open">Xem trong kho từ</button><button class="btn" type="button" data-deck-action="export">Tải bộ từ</button></div></section>`;
      },'Đang lưu…');return;
    }
    const deckName=current.preview?.name;if(!deckName)return;
    if(button.dataset.deckAction==='open'){state.filters={q:'',tag:deckName,reading:'',scope:'all',sort:'newest',page:1};location.hash='vocabulary';}
    if(button.dataset.deckAction==='study'){state.study=null;state.studySettings={...state.studySettings,tag:deckName,reading:'',scope:'all'};location.hash='study';}
    if(button.dataset.deckAction==='export')await busy(button,async()=>download('lexiread-vocabulary.json',await api('/vocabulary/deck/?name='+encodeURIComponent(deckName))));
  }
  document.addEventListener('click',e=>{const button=e.target.closest('[data-deck-action]');if(button)action(button).catch(error=>{const output=current?.root.querySelector('[data-deck-error]');if(output){output.textContent=error.message;output.scrollIntoView({behavior:'smooth',block:'center'});}else toast(error.message,true);});});
  function invalidate(){if(current){current.revision=(current.revision||0)+1;current.preview=null;const preview=current.root.querySelector('[data-deck-preview]');if(preview)preview.hidden=true;}}
  document.addEventListener('change',e=>{if(e.target.matches('[data-deck-all]'))current.root.querySelectorAll('[data-deck-index]').forEach(x=>x.checked=e.target.checked);if(e.target.id==='deck-file')invalidate();});
  document.addEventListener('input',e=>{if(['deck-paste','deck-name'].includes(e.target.id))invalidate();});
  window.LexiDecks={page,normalize,pack,sample,prompt,key};
})();
