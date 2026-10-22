"""Pure-function tests. Run without Django or PostgreSQL: unittest discover -s tests."""
import copy
import json
import unittest
from pathlib import Path
from learning.services.core import InputError, paragraphs, MAX_AI_CHARS
from learning.services.catalog import validate_lesson, public_lesson, grade_lesson, clean_reading_progress
from learning.services.qa import validate_answer, question_context, source_hash, prompt_for_question
ROOT=Path(__file__).resolve().parents[1]

def load():return json.loads((ROOT/'data/lessons/a-quiet-start.json').read_text(encoding='utf-8'))

class FixedLessonTests(unittest.TestCase):
    def setUp(self):self.raw=load();self.lesson=validate_lesson(self.raw)
    def test_catalog_inventory(self):
        all_lessons=[validate_lesson(json.loads(f.read_text(encoding='utf-8'))) for f in (ROOT/'data/lessons').glob('*.json')]
        self.assertEqual(len(all_lessons),12)
        self.assertEqual(len({x['slug'] for x in all_lessons}),12)
        self.assertEqual(len({x['topic'] for x in all_lessons}),12)
        for level in ['A2','B1','B2']:self.assertEqual(sum(x['level']==level for x in all_lessons),4)
        self.assertEqual(sum(len(x['analysis']['vocabulary']) for x in all_lessons),72)
        self.assertEqual(sum(len(x['questions']) for x in all_lessons),48)
        self.assertEqual(sum(len(x['analysis']['grammar']) for x in all_lessons),24)
        self.assertEqual(sum(len(x['faqs']) for x in all_lessons),24)
        for x in all_lessons:
            self.assertTrue(190<=len(x['text'].split())<=250)
            self.assertEqual(len(paragraphs(x['text'])),4)
    def test_analysis_is_curated_not_learner_verified(self):
        self.assertEqual(self.lesson['analysis']['origin'],'curated')
        self.assertTrue(all(not v['verified'] and v['origin']=='curated' for v in self.lesson['analysis']['vocabulary']))
    def test_validation_preserves_original(self):
        old=copy.deepcopy(self.raw);validate_lesson(self.raw);self.assertEqual(old,self.raw)
    def test_rejects_bad_slug(self):
        for slug in ['../x','abc def','CAPITAL','', 'x/y']:
            with self.subTest(slug=slug),self.assertRaises(InputError):validate_lesson({**self.raw,'slug':slug})
    def test_rejects_bad_level(self):
        with self.assertRaises(InputError):validate_lesson({**self.raw,'level':'Band 9'})
    def test_rejects_bad_revision(self):
        for rev in [True,0,1.2,'1']:
            with self.subTest(revision=rev),self.assertRaises(InputError):validate_lesson({**self.raw,'revision':rev})
    def test_malformed_nested_content_is_input_error(self):
        for key,value in [('analysis',None),('questions',[None]),('faqs',[None])]:
            with self.subTest(key=key),self.assertRaises(InputError):validate_lesson({**self.raw,key:value})
        self.raw['analysis']['vocabulary']=[None]
        with self.assertRaises(InputError):validate_lesson(self.raw)
    def test_questions_require_valid_key(self):
        for answer in [-1,4,False,'0']:
            c=copy.deepcopy(self.raw);c['questions'][0]['answer']=answer
            with self.subTest(answer=answer),self.assertRaises(InputError):validate_lesson(c)
    def test_rejects_duplicate_question_ids(self):
        self.raw['questions'][1]['id']=self.raw['questions'][0]['id']
        with self.assertRaises(InputError):validate_lesson(self.raw)
    def test_rejects_duplicate_options(self):
        self.raw['questions'][0]['options'][1]=self.raw['questions'][0]['options'][0].upper()
        with self.assertRaises(InputError):validate_lesson(self.raw)
    def test_tfng_labels_are_fixed(self):
        q=next(x for x in self.raw['questions'] if x['kind']=='tfng');q['options']=['YES','NO','NOT GIVEN']
        with self.assertRaises(InputError):validate_lesson(self.raw)
    def test_rejects_fabricated_evidence(self):
        self.raw['questions'][0]['evidence']='There is a spaceship in this story.'
        with self.assertRaises(InputError):validate_lesson(self.raw)
    def test_rejects_wrong_evidence_paragraph(self):
        q=self.raw['questions'][0];q['paragraph_index']=(q['paragraph_index']+1)%4
        with self.assertRaises(InputError):validate_lesson(self.raw)
    def test_missing_translation_rejected(self):
        self.raw['analysis']['translations'].pop()
        with self.assertRaises(InputError):validate_lesson(self.raw)
    def test_public_response_has_no_answer_key(self):
        public=public_lesson(self.lesson)
        self.assertNotIn('text',public)
        for q in public['questions']:self.assertEqual(set(q),{'id','kind','prompt','options'})
    def test_public_response_is_copy(self):
        public=public_lesson(self.lesson);public['questions'][0]['options'][0]='CHANGED';public['faqs'][0]['evidence']='CHANGED'
        self.assertNotEqual(self.lesson['questions'][0]['options'][0],'CHANGED')
        self.assertNotEqual(self.lesson['faqs'][0]['evidence'],'CHANGED')
    def test_perfect_grade(self):
        result=grade_lesson(self.lesson,{q['id']:q['answer'] for q in self.lesson['questions']})
        self.assertEqual((result['score'],result['total']),(4,4));self.assertTrue(all(q['evidence'] for q in result['results']))
    def test_all_wrong_grade(self):
        result=grade_lesson(self.lesson,{q['id']:(q['answer']+1)%len(q['options']) for q in self.lesson['questions']})
        self.assertEqual(result['score'],0)
    def test_grade_rejects_incomplete_extra_and_bad_index(self):
        answers={q['id']:q['answer'] for q in self.lesson['questions']}
        for invalid in [{},None,{**answers,'alien':0},{**answers,'q1':True}]:
            with self.subTest(answers=invalid),self.assertRaises(InputError):grade_lesson(self.lesson,invalid)
    def test_only_allowed_progress_is_copied(self):
        out=clean_reading_progress({'paragraph':1,'completed':True,'favorite':True,'quiz_best':999,'owner':12},self.lesson['text'])
        self.assertEqual(out,{'paragraph':1,'completed':True,'favorite':True})
    def test_progress_rejects_wrong_values(self):
        for raw in [{'paragraph':-1},{'paragraph':4},{'paragraph':False},{'completed':'yes'},{'favorite':1},None]:
            with self.subTest(raw=raw),self.assertRaises(InputError):clean_reading_progress(raw,self.lesson['text'])

class GroundedHelpTests(unittest.TestCase):
    def setUp(self):
        self.text='She changed her routine.\n\nShe put her bag beside the door.'
        self.good={'answer_vi':'Cô ấy đổi thói quen.','cannot_answer':False,'limitation_vi':'Lời giải tham khảo.',
                   'evidence':[{'paragraph_index':0,'quote':'She changed her routine.'}],'language_notes':[]}
    def test_accepts_grounded_answer(self):self.assertEqual(validate_answer(self.good,self.text),self.good)
    def test_refusal_can_have_no_evidence(self):
        result=validate_answer({**self.good,'cannot_answer':True,'evidence':[]},self.text);self.assertTrue(result['cannot_answer'])
    def test_ordinary_answer_must_have_evidence(self):
        with self.assertRaises(InputError):validate_answer({**self.good,'evidence':[]},self.text)
    def test_quote_must_match(self):
        with self.assertRaises(InputError):validate_answer({**self.good,'evidence':[{'paragraph_index':0,'quote':'Invented'}]},self.text)
    def test_correct_quote_wrong_paragraph_rejected(self):
        self.good['evidence'][0]['paragraph_index']=1
        with self.assertRaises(InputError):validate_answer(self.good,self.text)
    def test_boolean_paragraph_index_rejected(self):
        self.good['evidence'][0]['paragraph_index']=False
        with self.assertRaises(InputError):validate_answer(self.good,self.text)
    def test_cross_paragraph_quote_rejected(self):
        self.good['evidence'][0]['quote']=self.text
        with self.assertRaises(InputError):validate_answer(self.good,self.text)
    def test_empty_answer_rejected(self):
        with self.assertRaises(InputError):validate_answer({**self.good,'answer_vi':'  '},self.text)
    def test_schema_rejects_extra_fields(self):
        with self.assertRaises(InputError):validate_answer({**self.good,'owner':1},self.text)
    def test_limits_number_of_evidence_items(self):
        with self.assertRaises(InputError):validate_answer({**self.good,'evidence':self.good['evidence']*7},self.text)
    def test_selection_matches_source(self):
        self.assertEqual(question_context(self.text,'Nghĩa?','her routine')[2],'her routine')
        with self.assertRaises(InputError):question_context(self.text,'Nghĩa?','some other book')
    def test_question_and_text_limits(self):
        for text,q in [(self.text,''),(self.text,'q'*1501),('x'*(MAX_AI_CHARS+1),'Why?')]:
            with self.subTest(length=len(text)),self.assertRaises(InputError):question_context(text,q)
    def test_source_hash_is_sensitive(self):
        self.assertEqual(source_hash(self.text),source_hash(self.text));self.assertNotEqual(source_hash(self.text),source_hash(self.text+' edited'))
    def test_prompt_contains_question_and_source_data(self):
        prompt=prompt_for_question(self.text,'Routine nghĩa gì?','routine')
        self.assertIn('Routine nghĩa gì?',prompt);self.assertIn('UNTRUSTED STUDY DATA',prompt);self.assertIn('paragraph_index',prompt)
    def test_matching_quote_not_semantic_guarantee(self):
        # Mechanical checks cannot determine whether the explanation really follows.
        value={**self.good,'answer_vi':'Một cách diễn giải cần người học kiểm tra lại.'}
        self.assertEqual(validate_answer(value,self.text)['answer_vi'],value['answer_vi'])

if __name__=='__main__':unittest.main()
