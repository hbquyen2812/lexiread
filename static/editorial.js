'use strict';
// Progressive enhancement: the real JSON field remains the source on submit.
document.addEventListener('DOMContentLoaded',()=>{
  for(const raw of document.querySelectorAll('textarea.editorial-questions')){
    let values;try{values=JSON.parse(raw.value||'[]');if(!Array.isArray(values))continue;}catch{continue;}
    const host=document.createElement('div');host.className='editorial-question-list';raw.after(host);
    const cards=[];
    const types={main_idea:'Ý chính',detail:'Chi tiết',tfng:'TRUE / FALSE / NOT GIVEN',ynng:'YES / NO / NOT GIVEN',vocabulary:'Từ vựng',inference:'Suy luận',matching_heading:'Ghép tiêu đề',matching_information:'Ghép thông tin',gap_fill:'Điền từ',short_answer:'Trả lời ngắn'};
    function add(value={}){
      const card=document.createElement('section');card.className='editorial-question';host.append(card);
      const inputs={};
      function field(key,label,type='text',initial=''){
        const wrap=document.createElement('label');wrap.append(document.createTextNode(label));
        const input=document.createElement(type==='textarea'?'textarea':type==='select'?'select':'input');
        if(type==='select'){for(const [k,v] of Object.entries(types)){const option=document.createElement('option');option.value=k;option.textContent=v;input.append(option);}}
        else if(type!=='textarea')input.type=type;
        input.value=initial;wrap.append(input);card.append(wrap);inputs[key]=input;return input;
      }
      field('id','Mã câu hỏi','text',value.id||'q-'+(globalThis.crypto?.randomUUID?.()||Date.now().toString(36)));
      field('kind','Dạng câu hỏi','select',value.kind||'detail');
      field('prompt','Câu hỏi','textarea',value.prompt||'');
      field('options','Các lựa chọn (mỗi lựa chọn một dòng; để trống nếu điền từ)','textarea',(value.options||[]).join('\n'));
      field('answer','Đáp án: chỉ số 0, 1, 2… cho trắc nghiệm; chữ cho điền từ','text',value.answer??0);
      field('paragraph_index','Đoạn chứa bằng chứng (đoạn đầu là 0)','number',value.paragraph_index??0);
      field('evidence','Trích dẫn nguyên văn','textarea',value.evidence||'');
      field('explanation_vi','Giải thích tiếng Việt','textarea',value.explanation_vi||'');
      field('accepted_answers','Điền từ: đáp án chấp nhận, mỗi dòng một đáp án','textarea',(value.accepted_answers||[]).join('\n'));
      field('max_words','Điền từ: số từ tối đa','number',value.max_words||3);
      const remove=document.createElement('button');remove.type='button';remove.textContent='Bỏ câu này';remove.addEventListener('click',()=>{card.remove();});card.append(remove);
      cards.push({card,inputs});
    }
    values.forEach(add);raw.hidden=true;
    const button=document.createElement('button');button.type='button';button.textContent='+ Thêm câu hỏi';host.after(button);button.addEventListener('click',()=>add());
    raw.form.addEventListener('submit',()=>{
      raw.value=JSON.stringify(cards.filter(c=>c.card.isConnected).map(({inputs:f})=>{
        const text=['gap_fill','short_answer'].includes(f.kind.value);
        const q={id:f.id.value,kind:f.kind.value,prompt:f.prompt.value,options:text?[]:f.options.value.split('\n').filter(v=>v.trim()),answer:text?f.answer.value:Number(f.answer.value),paragraph_index:Number(f.paragraph_index.value),evidence:f.evidence.value,explanation_vi:f.explanation_vi.value};
        if(text){q.accepted_answers=f.accepted_answers.value.split('\n').filter(v=>v.trim());q.max_words=Number(f.max_words.value);}return q;
      }));
    });
  }
});
