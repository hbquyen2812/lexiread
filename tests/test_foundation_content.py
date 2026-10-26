import json
import unittest
from learning.services.foundation_content import units, questions_for, grade, quiz_snapshot, ROOT, LEVELS


class FoundationContentTests(unittest.TestCase):
    def test_complete_graded_curriculum(self):
        for kind,total in [('grammar',180),('vocabulary',360)]:
            rows=units(kind)
            self.assertEqual(len(rows),30)
            self.assertEqual({l:sum(r['level']==l for r in rows) for l in LEVELS},dict.fromkeys(LEVELS,5))
            self.assertEqual(sum(len(questions_for(r,kind)) for r in rows),total)
            for row in rows:
                snapshot=quiz_snapshot(row,kind)
                answers={q['id']:q['answer'] for q in snapshot['questions']}
                self.assertEqual(grade(snapshot,answers)['percent'],100)
                self.assertEqual(grade(snapshot,{k:(v+1)%4 for k,v in answers.items()})['percent'],0)

    def test_sources_report_matches_actual_catalogue(self):
        data=json.loads((ROOT/'study_sources.json').read_text(encoding='utf-8'))
        self.assertEqual(len(data['items']),40)
        self.assertEqual(len({r['id'] for r in data['items']}),40)
        self.assertTrue(all(r['url'].startswith('https://') for r in data['items']))
