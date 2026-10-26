"""Chromium DOM tests with an in-memory Storage double.
Container browser policy blocks localhost/file navigation, so this tests serialization and
restoration in fresh DOMs, not actual localStorage across real browser restarts.
"""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
BASE='about:blank'
LEGACY=Path(os.getenv('LEXIREAD_V1_PREVIEW', str(ROOT/'tests/fixtures/v1_preview.html')))
def content_with_storage(storage=None, legacy=False):
    text=(LEGACY if legacy else ROOT/'preview.html').read_text(encoding='utf-8')
    init=json.dumps(storage or {},ensure_ascii=False).replace('<','\\u003c')
    shim='<script>window.__testStorage='+init+';Object.defineProperty(window,"localStorage",{value:{getItem:k=>window.__testStorage[k]??null,setItem:(k,v)=>window.__testStorage[k]=String(v),removeItem:k=>delete window.__testStorage[k]}});</script>'
    return text.replace('<head>','<head>'+shim,1)
checks=[]
def ok(name):checks.append(name);print('PASS',name,flush=True)
def api(page,path,method='GET',data=None):
    return page.evaluate('async ([path,method,data])=>await window.LEXIREAD_PREVIEW.api(path,{method,data})',[path,method,data])
def navigate(page,route,selector):
    page.evaluate('(r)=>location.hash=r',route);page.wait_for_selector(selector);page.wait_for_timeout(110)
try:
 with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
    context=browser.new_context(viewport={'width':1440,'height':1050})
    page=context.new_page();errors=[];external=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r: external.append(r.url) if not r.url.startswith(BASE) else None)
    page.on('dialog',lambda d:d.accept())
    page.set_content(content_with_storage(),wait_until='domcontentloaded');page.wait_for_selector('.lesson-card')
    assert page.locator('.stat-value').all_inner_texts()==['24','0','116','116'];ok('Reading-first home with accurate library and review counts')
    assert page.locator('#analytics-nav').is_hidden();ok('Traffic dashboard stays admin-only')
    assert page.locator('.panel').filter(has_text='KẾ HOẠCH ÔN HÔM NAY').count()==1;ok('Home shows the daily spaced-review plan')
    page.screenshot(path=str(ROOT/'docs/v2_home.png'),full_page=True)
    navigate(page,'catalog','.catalog-filters');assert page.locator('.lesson-card').count()==24;ok('24 general lessons listed')
    page.locator('#catalog-level').select_option('A2');page.locator('[data-action="catalog-filter"]').click();page.wait_for_timeout(200)
    assert page.locator('.lesson-card').count()==6;ok('Level filter A2 -> 6 lessons')
    page.locator('#catalog-topic').select_option('Ẩm thực');page.locator('[data-action="catalog-filter"]').click();page.wait_for_timeout(200)
    assert page.locator('.lesson-card').count()==1;ok('Combined level and topic filters')
    page.locator('#catalog-level').select_option('');page.locator('#catalog-topic').select_option('');page.locator('[data-action="catalog-filter"]').click();page.wait_for_timeout(200)
    page.screenshot(path=str(ROOT/'docs/v2_catalog.png'),full_page=True)
    navigate(page,'toeic','.toeic-mode-grid');assert page.locator('.toeic-mode').count()==2;ok('TOEIC Reading offers exactly two practice paths')
    page.locator('a[href="#toeic-set/parts-5-6-workplace-basics"]').click();page.wait_for_selector('.toeic-questions');page.wait_for_timeout(150)
    assert page.locator('.reading-question').count()==12 and all('answer' not in q for q in api(page,'/toeic/parts-5-6-workplace-basics/')['questions']);ok('TOEIC practice renders 12 questions without leaking keys')
    page.locator('input[data-toeic-question]').evaluate_all("els=>els.filter((_,i)=>i%4===0).forEach(el=>{el.checked=true;el.dispatchEvent(new Event('change',{bubbles:true}))})")
    page.locator('[data-action="submit-toeic"]').click();page.wait_for_timeout(200)
    assert page.locator('.toeic-score').count()==1 and api(page,'/toeic/')['items'][1]['attempt_count']==1;ok('TOEIC result and personal attempt persist')
    navigate(page,'catalog','.catalog-filters')
    page.locator('a[href="#lesson/a-quiet-start"]').click();page.wait_for_selector('.reader-en');page.wait_for_timeout(180)
    rid=page.url.split('#reading/')[1];r=api(page,f'/readings/{rid}/')
    assert len(r['paragraphs'])==4 and r['lesson']['slug']=='a-quiet-start';ok('Opening curated content creates user reading snapshot')
    assert 'lesson_snapshot' not in r and all('answer' not in q and 'evidence' not in q for q in r['lesson']['questions']);ok('Reader API omits quiz keys before submission')
    assert api(page,'/readings/')['items'][0]['title']=='Set in Metal' and len(api(page,'/readings/')['items'])==1;ok('Curated lessons do not appear in private import list')
    api(page,f'/readings/{api(page,"/readings/")["items"][0]["id"]}/progress/','POST',{'favorite':True})
    filtered=api(page,'/readings/?q=metal&status=in_progress&favorite=yes&sort=title&page=1&limit=1')
    assert filtered['total']==1 and filtered['items'][0]['favorite'];ok('Saved readings support search, favorite, status and pagination')
    same=api(page,'/catalog/a-quiet-start/open/','POST',{});assert same['id']==rid;ok('Reopening lesson does not duplicate a personal reading')
    page.locator('#translation-toggle').uncheck();assert page.locator('.reader-vi').count()==0
    page.locator('#translation-toggle').check();assert page.locator('.reader-vi').count()==4;ok('Translation show/hide')
    page.locator('[data-action="bookmark-paragraph"][data-index="2"]').click();page.wait_for_timeout(200)
    assert api(page,f'/readings/{rid}/')['progress']['paragraph']==2;ok('Paragraph bookmark persisted')
    page.locator('[data-action="complete-reading"]').click();page.wait_for_timeout(200)
    assert api(page,f'/readings/{rid}/')['progress']['completed'];ok('Mark a reading complete')
    api(page,f'/readings/{rid}/progress/','POST',{'favorite':True})
    favorite_catalog=api(page,'/catalog/?favorite=yes')['items']
    assert len(favorite_catalog)==1 and favorite_catalog[0]['reading_id']==rid;ok('Favorite curated lesson can be found again in catalog')
    page.locator('.reader-en').first.evaluate('''el=>{
      const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let n;
      while(n=walker.nextNode()){const i=n.textContent.indexOf('routine');if(i>=0){const range=document.createRange();range.setStart(n,i);range.setEnd(n,i+7);const sel=window.getSelection();sel.removeAllRanges();sel.addRange(range);break;}}
      document.dispatchEvent(new MouseEvent('mouseup',{bubbles:true}));
    }''')
    page.wait_for_selector('#selection-bar:not([hidden])');page.locator('[data-action="selected-word"]').click()
    assert page.locator('#word-word').input_value()=='routine' and 'thói quen' in page.locator('#word-meaning').input_value();ok('Selected curated term prefills contextual meaning')
    page.locator('[data-action="save-word"]').click();page.wait_for_timeout(200)
    assert api(page,'/bootstrap/')['stats']['total']==117;ok('One-click vocabulary save into common personal store')
    page.locator('[data-action="reader-tab"][data-tab="words"]').click();assert page.locator('.candidate').count()==6;ok('Six preset vocabulary candidates')
    page.locator('[data-action="reader-tab"][data-tab="grammar"]').click();assert page.locator('.grammar-card').count()==2;ok('Two preset grammar notes')
    page.locator('[data-action="reader-tab"][data-tab="quiz"]').click();assert page.locator('.reading-question').count()==4
    page.locator('[data-action="submit-reading-quiz"]').click();page.wait_for_timeout(160);assert not page.locator('.reading-score').count();ok('Incomplete comprehension quiz rejected')
    raw=json.loads((ROOT/'data/lessons/a-quiet-start.json').read_text())
    for q in raw['questions']:page.locator(f'input[data-lesson-question="{q["id"]}"][value="{q["answer"]}"]').check()
    page.locator('[data-action="submit-reading-quiz"]').click();page.wait_for_selector('.reading-score')
    assert '4 / 4' in page.locator('.reading-score').inner_text() and page.locator('.feedback').count()==4;ok('Fixed comprehension quiz scored with four source explanations')
    token=page.evaluate('state.homework.token');ans={q['id']:q['answer'] for q in raw['questions']}
    again=api(page,f'/readings/{rid}/quiz/','POST',{'token':token,'answers':ans});assert again['duplicate'] and again['progress']['quiz_attempts']==1;ok('Comprehension submission is idempotent')
    page.screenshot(path=str(ROOT/'docs/v2_quiz.png'),full_page=True)
    page.locator('[data-action="reader-tab"][data-tab="help"]').click();assert page.locator('.faq-item').count()==2
    page.locator('.faq-item summary').first.click();assert 'morning' in page.locator('.faq-item').first.inner_text();ok('Static explanations work without AI')
    page.locator('#reading-question-input').fill('Routine nghĩa là gì trong bài?');page.locator('[data-action="ask-reading-prompt"]').click();page.wait_for_selector('#prompt-text')
    prompt=page.locator('#prompt-text').input_value();assert 'Routine nghĩa' in prompt and 'paragraphs' in prompt and 'cannot_answer' in prompt;ok('Reading-scoped manual Q&A prompt includes source and schema')
    answer={'answer_vi':'Routine ở đây là trình tự hoặc thói quen buổi sáng của Mai.','cannot_answer':False,'limitation_vi':'Đây là lời giải tham khảo.','evidence':[{'paragraph_index':0,'quote':'she decided to change her morning routine.'}],'language_notes':[{'point':'morning routine','explanation_vi':'thói quen buổi sáng'}]}
    page.locator('#result-json').fill(json.dumps(answer,ensure_ascii=False));page.locator('[data-action="apply-prompt"]').click();page.wait_for_selector('.qa-answer')
    assert 'Routine nghĩa' in page.locator('.qa-answer').inner_text();ok('Manual Q&A JSON -> stored answer and exact evidence')
    bad={**answer,'evidence':[{'paragraph_index':0,'quote':'This sentence was invented.'}]}
    response=page.evaluate('async ([rid,result])=>{try{await window.LEXIREAD_PREVIEW.api(`/readings/${rid}/questions/`,{method:"POST",data:{question:"Test",result}});return "accepted";}catch(e){return e.message;}}',[rid,bad])
    assert 'khớp' in response and len(api(page,f'/readings/{rid}/questions/')['items'])==1;ok('Invented Q&A quotation rejected without a write')
    response=page.evaluate('async (rid)=>{try{await window.LEXIREAD_PREVIEW.api(`/readings/${rid}/`,{method:"PATCH",data:{title:"Overwrite",text:"changed"}});return false;}catch(e){return true;}}',rid)
    assert response;ok('Curated reading cannot be overwritten through personal editor API')
    saved_storage=page.evaluate('window.__testStorage');page.close();page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept());page.set_content(content_with_storage(saved_storage),wait_until='domcontentloaded');page.wait_for_selector('.lesson-card');navigate(page,'reading/'+rid,'.reader-en');page.wait_for_timeout(180)
    rr=api(page,f'/readings/{rid}/');assert rr['progress']['paragraph']==2 and rr['progress']['completed'] and rr['progress']['quiz_best']==4;ok('Serialized bookmark, completion and score restore in a fresh DOM (Storage double)')
    page.locator('[data-action="reader-tab"][data-tab="help"]').click();assert page.locator('.qa-answer').count()==1;ok('Serialized Q&A history restores in a fresh DOM')
    page.screenshot(path=str(ROOT/'docs/v2_help.png'),full_page=True)
    navigate(page,'readings','.reading-card');assert page.locator('#reading-search').count()==1
    page.locator('#reading-favorite').select_option('yes');page.locator('[data-action="filter-readings"]').click();page.wait_for_timeout(150)
    assert page.locator('.reading-card').count()==1 and 'Yêu thích' in page.locator('.reading-card').inner_text();ok('Saved-reading filters render in the UI')
    page.locator('[data-action="new-reading"]').click()
    page.locator('#reading-title').fill('My private practice');page.locator('#reading-text').fill('A student reads a story every evening.\n\nShe saves a few words in her notebook.')
    page.locator('[data-action="save-reading"]').click();page.wait_for_selector('.reader-en');page.wait_for_timeout(170)
    private_id=page.url.split('#reading/')[1];assert private_id!=rid
    assert not page.locator('[data-action="reader-tab"][data-tab="quiz"]').count();ok('Imported reading has no fabricated fixed comprehension test')
    assert len(api(page,'/readings/')['items'])==2 and len(api(page,'/catalog/')['items'])==12;ok('Private imports remain out of the shared catalog')
    page.locator('[data-action="ask-paragraph"][data-index="0"]').click();assert 'A student' in page.locator('.selected-context').inner_text();ok('Ask about a chosen paragraph')
    routine=api(page,'/vocabulary/?q=routine')['items'][0]
    linked=api(page,'/vocabulary/','POST',{'reading_id':private_id,'word':routine['word'],'meaning_vi':routine['meaning_vi'],'context':'A student reads a story every evening.','source_label':'My private practice'})
    assert linked['created']==0 and private_id in {x['id'] for x in api(page,'/vocabulary/sources/')['items']}
    assert routine['id'] in {x['id'] for x in api(page,f'/vocabulary/?reading={private_id}')['items']};ok('One sense keeps occurrences from multiple readings')
    backup=api(page,'/backup/');assert backup['version']==4 and backup['counts']['vocabulary']==117 and backup['counts']['toeic_attempts']==1
    saved=next(x for x in backup['readings'] if x['id']==rid)
    saved_routine=next(x for x in backup['vocabulary'] if x['id']==routine['id'])
    assert len(saved['lesson_attempts'])==1 and len(saved['qa_history'])==1 and saved['lesson_snapshot']['questions'] and len(saved_routine['occurrences'])>=2 and len(backup['toeic_attempts'])==1;ok('V4 backup includes readings, vocabulary occurrences and TOEIC attempts')
    merged=api(page,'/restore/','POST',{'data':backup});assert merged['created']==0 and merged['readings_created']==0;ok('Backup merge keeps existing progress')
    private_backup=next(x for x in backup['readings'] if x['id']==private_id)
    duplicate_backup={'format':'lexiread-backup','version':3,'readings':[{**private_backup,'id':'00000000-0000-4000-8000-000000000099'}],'vocabulary':[],'reviews':[]}
    first_duplicate=api(page,'/restore/','POST',{'data':duplicate_backup});second_duplicate=api(page,'/restore/','POST',{'data':duplicate_backup})
    assert first_duplicate['readings_created']==1 and second_duplicate['readings_created']==0;ok('Backup preserves distinct readings with identical title and text')
    # Practice sessions retained after the reading-first changes.
    navigate(page,'vocabulary','#vocab-reading');assert page.locator('#vocab-reading option').count()>=3;ok('Vocabulary can be filtered by source reading')
    navigate(page,'reading/'+rid,'.reader-en');page.locator('[data-action="study-reading"]').click();page.wait_for_selector('#study-reading')
    assert page.locator('#study-reading').input_value()==rid;ok('Study-this-reading uses the stable reading id')
    page.locator('#study-reading').select_option('')
    navigate(page,'study','#study-mode');page.locator('#study-scope').select_option('all');page.locator('[data-action="start-study"]').click();page.wait_for_selector('.flashcard');page.locator('.flashcard').click();assert page.locator('.ratings button').count()==4;ok('Existing flashcard flow retained')
    first_card_id=page.evaluate('state.study.cards[0].id');page.locator('.ratings button').first.click();page.wait_for_timeout(180)
    assert page.evaluate('state.study.retryCount===1 && state.study.cards.some((x,i)=>i>=3&&x._retry===true)');ok('Forgotten flashcard is queued once for same-session relearning')
    assert first_card_id not in [x['id'] for x in api(page,'/vocabulary/?scope=new&limit=500')['items']]
    assert first_card_id in [x['id'] for x in api(page,'/vocabulary/?scope=learning&limit=500')['items']];ok('Forgotten card remains learning, not new')
    api(page,f'/vocabulary/{first_card_id}/review/','POST',{'token':'00000000-0000-4000-8000-000000000091','rating':'again'})
    api(page,f'/vocabulary/{first_card_id}/review/','POST',{'token':'00000000-0000-4000-8000-000000000092','rating':'again'})
    assert first_card_id in [x['id'] for x in api(page,'/vocabulary/?scope=weak&limit=500')['items']] and api(page,'/bootstrap/')['stats']['weak']>=1;ok('Frequently forgotten cards are grouped as weak words')
    for mode in ['meaning','reverse','synonym','paraphrase','cloze','typing']:
        page.locator('#study-mode').select_option(mode);page.locator('[data-action="start-study"]').click();page.wait_for_selector('.question-card')
        if mode=='typing':page.locator('#typing-answer').fill('test');page.locator('#typing-form button').click()
        else:page.locator('.option').first.click()
        page.wait_for_selector('.feedback');ok('Existing vocabulary exercise: '+mode)
    navigate(page,'catalog','.catalog-filters');page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(100)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2');ok('390px catalog reflow')
    page.locator('a[href="#lesson/a-quiet-start"]').click();page.wait_for_selector('.reader-en');page.wait_for_timeout(180)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2');ok('390px reader reflow')
    page.locator('#toasts').evaluate('e=>e.innerHTML=""');page.screenshot(path=str(ROOT/'docs/v2_mobile.png'),full_page=True)
    # Optional regression fixture: serialize v1 into fresh v2 DOM, not a real browser reload.
    if LEGACY.exists():
        legacy=context.browser.new_context();lp=legacy.new_page();lp.set_content(content_with_storage(legacy=True),wait_until='domcontentloaded');lp.wait_for_selector('.stat-value')
        word=api(lp,'/vocabulary/','POST',{'word':'my-legacy-word','meaning_vi':'từ cá nhân đã học'})['items'][0]
        api(lp,f'/vocabulary/{word["id"]}/review/','POST',{'token':'00000000-0000-4000-8000-000000000001','rating':'good'})
        legacy_storage=lp.evaluate('window.__testStorage');lp.close();lp=legacy.new_page();lp.set_content(content_with_storage(legacy_storage),wait_until='domcontentloaded');lp.wait_for_selector('.lesson-card')
        restored=api(lp,'/vocabulary/?q=my-legacy-word')['items'][0]
        assert restored['repetitions']==1 and restored['word']=='my-legacy-word' and api(lp,'/bootstrap/')['stats']['total']==117;ok('V1 serialized data loads in V2 without resetting the personal card or review schedule')
        legacy.close()
    assert not errors,errors;ok('No uncaught JavaScript exceptions')
    assert not external,external;ok('No external requests during the offline workflow')
    (ROOT/'docs/v2_browser_test_results.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'errors':errors,'environment':'Real Chromium DOM; set_content with a Storage test double because container browser policy blocks URL navigation. Serialization restored into fresh pages; not a test of actual localStorage persistence, Django/PostgreSQL or live AI.'},ensure_ascii=False,indent=2))
    browser.close()
finally:pass
print(len(checks),'checks passed',flush=True)
