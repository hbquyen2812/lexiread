"""Exercises use saved senses; no AI call is required for practice."""
import random
from .core import normalise,word_in_text,mask_word,InputError
MODES={'meaning','reverse','synonym','paraphrase','cloze','typing'}

def lexical_family(v):
    return {normalise(v['word'])}|{normalise(s) for s in v.get('synonyms',[])}|{normalise(s) for s in v.get('paraphrases',[])}

def build_question(entries,mode,rng=None,exclude=None):
    rng=rng or random.SystemRandom()
    if mode not in MODES: raise InputError('Dạng bài không hợp lệ.')
    candidates=[v for v in entries if str(v["id"]) not in set(exclude or [])]; rng.shuffle(candidates)
    for v in candidates:
        context=v.get('example') or v.get('context','')
        if mode=='cloze' and (not context or not word_in_text(v['word'],context)): continue
        if mode=='synonym' and not v.get('synonyms'): continue
        if mode=='paraphrase' and not v.get('paraphrases'): continue
        if mode=='meaning': answer=v['meaning_vi']; prompt=v['word']; caption='Chọn nghĩa tiếng Việt theo ngữ cảnh của thẻ.'
        elif mode in {'reverse','typing'}: answer=v['word'];prompt=v['meaning_vi'];caption='Nhớ từ/cụm tiếng Anh đã lưu cho nghĩa này.'
        elif mode=='cloze': answer=v['word'];prompt=mask_word(v['word'],context);caption='Chọn từ gốc điền vào chỗ trống.'
        elif mode=='synonym': answer=v['synonyms'][0];prompt=v['word'];caption='Chọn từ/cụm gần nghĩa đã lưu cho ngữ cảnh này.'
        else: answer=v['paraphrases'][0];prompt=v['word'];caption='Chọn cách diễn đạt gần nghĩa đã lưu (không phải đề IELTS chính thức).'
        family=lexical_family(v)
        options=[]; seen={normalise(answer)}
        others=[x for x in entries if x['id']!=v['id']]
        rng.shuffle(others)
        for o in others:
            # Exclude overlapping synonym families and identical meanings. This reduces
            # ambiguity, but is not a semantic proof that every distractor is exclusive.
            if normalise(o['word'])==normalise(v['word']) or normalise(o['meaning_vi'])==normalise(v['meaning_vi']) or family & lexical_family(o): continue
            if mode=='meaning': choice=o['meaning_vi']
            elif mode=='synonym': choice=(o.get('synonyms') or [o['word']])[0]
            elif mode=='paraphrase': choice=(o.get('paraphrases') or [o['word']])[0]
            else: choice=o['word']
            if normalise(choice) not in seen:
                options.append(choice);seen.add(normalise(choice))
            if len(options)==3:break
        if mode!='typing' and len(options)<3: continue
        if mode!='typing': options.append(answer);rng.shuffle(options)
        # Never expose the answer through an English example in reverse/typing mode.
        hint=context if mode in {'meaning','synonym','paraphrase'} else ''
        return v,{'mode':mode,'prompt':prompt,'caption':caption,'context':hint,'pos':v.get('pos',''),
                  'options':options if mode!='typing' else []},answer
    raise InputError('Chưa đủ thẻ phù hợp. Cần ít nhất 4 nghĩa khác nhau; dạng synonym/paraphrase cần dữ liệu tương ứng, điền từ cần câu chứa đúng từ gốc.')
