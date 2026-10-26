import copy
import json
import unittest
from learning.services.foundation_content import units, questions_for, grade, quiz_snapshot, validate_unit, ROOT, LEVELS
from learning.services.core import InputError
from learning.services.grammar_reference import reference, lesson_guide


class FoundationContentTests(unittest.TestCase):
    def test_reference_integrity_and_copy_isolation(self):
        data=reference()
        lessons={r['id'] for r in units('grammar')}
        self.assertLessEqual(set(data['lesson_guides']),lessons)
        self.assertLessEqual({r['lesson_id'] for r in data['tenses'] if r['lesson_id']},lessons)
        verbs={r['base']:r for r in data['verbs']}
        for base,past,participle in [('go','went','gone'),('lie','lay','lain'),('lay','laid','laid'),('write','wrote','written')]:
            self.assertIn(past,verbs[base]['past'])
            self.assertIn(participle,verbs[base]['participle'])
        self.assertIn('/red/',verbs['read']['note'])
        self.assertIn('gotten',verbs['get']['participle'])
        guide=lesson_guide('b1-present-perfect')
        self.assertEqual(guide['tenses'][0]['id'],'present-perfect')
        guide['tenses'][0]['forms']['affirmative']='changed'
        self.assertNotEqual(lesson_guide('b1-present-perfect')['tenses'][0]['forms']['affirmative'],'changed')
        self.assertIsNone(lesson_guide('not-a-lesson'))

    def test_complete_graded_curriculum(self):
        for kind,total in [('grammar',216),('vocabulary',360)]:
            rows=units(kind)
            expected={'A1':8,'A2':8,'B1':5,'B2':5,'C1':5,'C2':5} if kind=='grammar' else dict.fromkeys(LEVELS,5)
            self.assertEqual(len(rows),sum(expected.values()))
            self.assertEqual({l:sum(r['level']==l for r in rows) for l in LEVELS},expected)
            self.assertEqual(sum(len(questions_for(r,kind)) for r in rows),total)
            for row in rows:
                snapshot=quiz_snapshot(row,kind)
                answers={q['id']:q['answer'] for q in snapshot['questions']}
                self.assertEqual(grade(snapshot,answers)['percent'],100)
                self.assertEqual(grade(snapshot,{k:(v+1)%4 for k,v in answers.items()})['percent'],0)

    def test_beginner_lessons_teach_before_testing(self):
        lessons=[r for r in units('grammar') if r['level'] in ('A1','A2')]
        self.assertEqual(len(lessons),16)
        self.assertEqual(lessons[0]['id'],'a1-sentence-basics')
        for lesson in lessons:
            self.assertGreaterEqual(len(lesson['explanation']),3)
            teaching=lesson['teaching']
            self.assertEqual(len(teaching['steps']),3)
            self.assertEqual(len(teaching['takeaways']),2)
            self.assertTrue(teaching['quick_check']['answer'])
            self.assertEqual(len(lesson['questions']),6)

    def test_reject_incomplete_teaching_content(self):
        original=units('grammar')[0]
        for field in ('objective','context','example','translation_vi','steps','takeaways','quick_check'):
            broken=copy.deepcopy(original)
            broken['teaching'].pop(field)
            with self.subTest(field=field),self.assertRaises(InputError):
                validate_unit(broken,'grammar')

    def test_sources_report_matches_actual_catalogue(self):
        data=json.loads((ROOT/'study_sources.json').read_text(encoding='utf-8'))
        self.assertEqual(len(data['items']),40)
        self.assertEqual(len({r['id'] for r in data['items']}),40)
        self.assertTrue(all(r['url'].startswith('https://') for r in data['items']))
