import copy
import unittest
from learning.services.core import InputError
from learning.services.toeic import grade_toeic,public_toeic_set,toeic_sets,validate_toeic_set

class ToeicContentTests(unittest.TestCase):
    def test_two_modes_and_inventory(self):
        sets=toeic_sets()
        self.assertEqual({item['mode'] for item in sets},{'parts-5-6','part-7'})
        self.assertEqual(len(sets),14)
        self.assertEqual(sum(item['question_count'] for item in sets),192)
        self.assertEqual(sum(len(item['focus_vocabulary']) for item in sets),88)

    def test_public_payload_hides_keys_and_explanations(self):
        for practice in toeic_sets():
            public=public_toeic_set(practice['slug'])
            for question in public['questions']:
                self.assertNotIn('answer',question)
                self.assertNotIn('explanation_vi',question)
                self.assertNotIn('evidence',question)

    def test_perfect_grade_and_part_breakdown(self):
        for practice in toeic_sets():
            answers={q['id']:q['answer'] for q in practice['questions']}
            result=grade_toeic(practice,answers)
            self.assertEqual(result['score'],result['total'])
            self.assertEqual(result['percentage'],100)
            self.assertEqual(sum(row['total'] for row in result['by_part'].values()),result['total'])

    def test_incomplete_or_extra_answers_rejected(self):
        practice=toeic_sets()[0]
        with self.assertRaises(InputError):grade_toeic(practice,{})
        answers={q['id']:q['answer'] for q in practice['questions']};answers['extra']=0
        with self.assertRaises(InputError):grade_toeic(practice,answers)

    def test_evidence_must_exist_in_document(self):
        raw=copy.deepcopy(toeic_sets()[0]);raw['questions'][0]['evidence']='fabricated evidence'
        with self.assertRaises(InputError):validate_toeic_set(raw)
