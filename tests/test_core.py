"""Network/database-free tests. Run: python -m unittest discover -s tests -v"""
import copy,json,random,unittest
from datetime import date,datetime,timezone,timedelta
from pathlib import Path
from learning.services.core import (normalise,fingerprint,clean_text,paragraphs,parse_json,validate_entry,
    validate_progress,schedule,calculate_review_streak,word_in_text,mask_word,InputError)
from learning.services.analysis import validate_analysis,prompt_for_reading
from learning.services.exercises import build_question,MODES
ROOT=Path(__file__).resolve().parents[1]
WORDS=json.loads((ROOT/'data/seed_vocab.json').read_text(encoding='utf-8'))
TEXT=(ROOT/'data/set_in_metal.txt').read_text(encoding='utf-8')
ANALYSIS=json.loads((ROOT/'data/demo_analysis.json').read_text(encoding='utf-8'))
class TextTests(unittest.TestCase):
    def test_normalisation(self): self.assertEqual(normalise('  ＢＯＬＤ\n test '),'bold test')
    def test_sense_fingerprint(self):
        self.assertEqual(fingerprint(' BOLD','Táo bạo'),fingerprint('bold',' táo bạo '))
        self.assertNotEqual(fingerprint('novel','mới lạ'),fingerprint('novel','tiểu thuyết'))
    def test_null_removal(self): self.assertEqual(clean_text('a\x00b',10),'ab')
    def test_size_required(self):
        for value,limit,required in [('1234',3,False),('',10,True),(None,10,False)]:
            with self.assertRaises(InputError):clean_text(value,limit,required)
    def test_paragraphs(self): self.assertEqual(paragraphs('One.\r\n\r\nTwo.'),['One.','Two.'])
    def test_json(self):self.assertEqual(parse_json('```json\n{"a": 1}\n```'),{'a':1})
    def test_bad_json(self):
        with self.assertRaises(InputError):parse_json('{no}')
    def test_boundary(self):
        self.assertFalse(word_in_text('apt','adapt'))
        self.assertTrue(word_in_text('bold','A BOLD choice.'))
        self.assertEqual(mask_word('bold','A bold, bold choice.'),'A ______, ______ choice.')
    def test_entry_normalisation(self):
        w=validate_entry({'word':'tally','meaning_vi':'khớp','synonyms':'match|agree|match'})
        self.assertEqual(w['synonyms'],['match','agree']);self.assertFalse(w['verified'])
    def test_bad_entry(self):
        for entry in [{},{'word':'a','meaning_vi':''},{'word':'a','meaning_vi':'b','tags':[1]}]:
            with self.assertRaises(InputError):validate_entry(entry)
    def test_seed_data(self):
        self.assertEqual(len(WORDS),116)
        fps=[]
        for raw in WORDS:
            v=validate_entry(raw);fps.append(fingerprint(v['word'],v['meaning_vi']))
        self.assertEqual(len(fps),len(set(fps)))
    def test_corrections_present(self):
        terms={w['word'] for w in WORDS}
        for w in ['reinstate','monumental','apprenticeship','depict','undertaking','on the spur of the moment','pull out','step down']:
            self.assertIn(w,terms)
class SchedulerTests(unittest.TestCase):
    def setUp(self):self.now=datetime(2026,10,18,tzinfo=timezone.utc)
    def test_again(self):
        s=schedule({},'again',self.now);self.assertEqual(s['due_at']-self.now,timedelta(minutes=10));self.assertEqual(s['lapses'],1)
    def test_good_sequence(self):
        s=schedule({},'good',self.now);self.assertEqual(s['interval_days'],1)
        s=schedule(s,'good',self.now);self.assertEqual(s['interval_days'],3)
        s=schedule(s,'good',self.now);self.assertEqual(s['interval_days'],7.5)
    def test_easy_and_bounds(self):
        self.assertEqual(schedule({},'easy',self.now)['interval_days'],4)
        s={'interval_days':350,'ease':3,'repetitions':20}
        self.assertLessEqual(schedule(s,'easy',self.now)['interval_days'],365)
    def test_invalid_rating(self):
        with self.assertRaises(InputError):schedule({},'bad',self.now)
    def test_timezone(self):
        self.assertIsNotNone(validate_progress({'due_at':'2026-10-18T00:00:00Z'})['due_at'].tzinfo)
        with self.assertRaises(InputError):validate_progress({'due_at':'2026-10-18'})
    def test_invalid_progress(self):
        for d in [{'ease':float('nan')},{'interval_days':float('inf')},{'lapses':-1},{'repetitions':1.5},{'ease':True}]:
            with self.assertRaises(InputError):validate_progress(d)
    def test_review_streak_uses_today_or_yesterday(self):
        today=date(2026,10,22)
        self.assertEqual(calculate_review_streak([today,today-timedelta(days=1),today-timedelta(days=2)],today),3)
        self.assertEqual(calculate_review_streak([today-timedelta(days=1),today-timedelta(days=2)],today),2)
        self.assertEqual(calculate_review_streak([today-timedelta(days=2)],today),0)
class GroundingTests(unittest.TestCase):
    def test_demo_valid(self):
        result=validate_analysis(ANALYSIS,TEXT)
        self.assertEqual(len(result['translations']),9);self.assertEqual(len(result['vocabulary']),10)
        self.assertEqual(result['warnings'],[])
    def test_missing_translation(self):
        d=copy.deepcopy(ANALYSIS);d['translations'].pop()
        with self.assertRaises(InputError):validate_analysis(d,TEXT)
    def test_duplicate_index(self):
        d=copy.deepcopy(ANALYSIS);d['translations'][1]['index']=0
        with self.assertRaises(InputError):validate_analysis(d,TEXT)
    def test_untrusted_quote_removed(self):
        d=copy.deepcopy(ANALYSIS);d['vocabulary'][0]['context']='This quotation does not exist.'
        result=validate_analysis(d,TEXT);self.assertEqual(len(result['vocabulary']),9)
        self.assertEqual(len(result['warnings']),1)
    def test_wrong_paragraph_removed(self):
        d=copy.deepcopy(ANALYSIS);d['vocabulary'][0]['paragraph_index']=999
        self.assertEqual(len(validate_analysis(d,TEXT)['vocabulary']),9)
    def test_grammar_not_fabricated(self):
        d=copy.deepcopy(ANALYSIS);d['grammar'][0]['evidence']='This is invented.'
        self.assertEqual(len(validate_analysis(d,TEXT)['grammar']),3)
    def test_schema_extra(self):
        d=copy.deepcopy(ANALYSIS);d['fake']=123
        with self.assertRaises(InputError):validate_analysis(d,TEXT)
    def test_prompt_limit(self):
        with self.assertRaises(InputError):prompt_for_reading('a'*16001)
class ExerciseTests(unittest.TestCase):
    def setUp(self):self.pool=[dict(w,id=str(i)) for i,w in enumerate(WORDS)]
    def test_all_modes(self):
        for mode in sorted(MODES):
            for seed in range(12):
                with self.subTest(mode=mode,seed=seed):
                    v,q,answer=build_question(self.pool,mode,random.Random(seed))
                    self.assertNotIn('correct_answer',q)
                    if mode=='typing':self.assertEqual(q['options'],[])
                    else:self.assertEqual(len(q['options']),4);self.assertEqual(len(set(q['options'])),4);self.assertIn(answer,q['options'])
                    if mode in {'typing','reverse'}:self.assertEqual(q['context'],'')
                    if mode=='cloze':self.assertIn('______',q['prompt']);self.assertFalse(word_in_text(answer,q['prompt']))
    def test_exclusion_keeps_distractors(self):
        pool=self.pool[:4];target=pool[0]['id']
        v,q,a=build_question(pool,'meaning',random.Random(1),exclude=[p['id'] for p in pool[1:]])
        self.assertEqual(v['id'],target);self.assertEqual(len(q['options']),4)
    def test_not_enough(self):
        with self.assertRaises(InputError):build_question(self.pool[:1],'meaning')
    def test_invalid_mode(self):
        with self.assertRaises(InputError):build_question(self.pool,'unknown')
    def test_all_excluded(self):
        with self.assertRaises(InputError):build_question(self.pool,'typing',exclude=[v['id'] for v in self.pool])
if __name__=='__main__':unittest.main()
