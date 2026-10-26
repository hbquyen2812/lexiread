"""Functional invariants for the original October TOEIC content expansion."""
import json
from pathlib import Path
import re
import unittest

from learning.services.toeic import validate_toeic_set

DATA = Path(__file__).resolve().parents[1] / 'data' / 'toeic'


class ToeicExpansionContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sets = [validate_toeic_set(json.loads(path.read_text(encoding='utf-8')))
                    for path in sorted(DATA.glob('p[567]-*.json'))]

    def test_part_six_questions_match_the_displayed_numbered_blanks(self):
        for practice in (row for row in self.sets if row['parts'] == [6]):
            with self.subTest(slug=practice['slug']):
                documents = {doc['id']: doc for doc in practice['documents']}
                blanks = []
                for document in documents.values():
                    numbers = re.findall(r'___\((\d+)\)___', document['body'])
                    self.assertEqual(len(numbers), 4)
                    blanks.extend(int(number) for number in numbers)
                self.assertEqual(sorted(blanks), list(range(1, 17)))
                for number, question in enumerate(practice['questions'], 1):
                    self.assertTrue(question['prompt'].startswith(f'Blank {number}:'))
                    self.assertEqual(len(question['document_ids']), 1)
                    body = documents[question['document_ids'][0]]['body']
                    self.assertIn(f'___({number})___', body)
                    self.assertIn(question['evidence'], body)

    def test_part_seven_document_clusters_keep_all_context_visible(self):
        for practice in (row for row in self.sets if row['parts'] == [7]):
            with self.subTest(slug=practice['slug']):
                size = 3 if '-triple-' in practice['slug'] else 2 if '-double-' in practice['slug'] else 1
                for offset in (0, 5):
                    group = practice['questions'][offset:offset + 5]
                    ids = group[0]['document_ids']
                    self.assertEqual(len(ids), size)
                    self.assertTrue(all(question['document_ids'] == ids for question in group))
                    self.assertEqual(ids, [doc['id'] for doc in practice['documents'][offset // 5 * size:(offset // 5 + 1) * size]])
                    for question in group:
                        self.assertTrue(question['evidence'])
                        self.assertTrue(any(question['evidence'] in doc['body']
                                            for doc in practice['documents'] if doc['id'] in ids))

    def test_expansion_has_the_promised_part_and_document_coverage(self):
        self.assertEqual(len(self.sets), 12)
        counts = {part: sum(len(row['questions']) for row in self.sets if row['parts'] == [part])
                  for part in (5, 6, 7)}
        self.assertEqual(counts, {5: 60, 6: 48, 7: 60})
        self.assertEqual(sum(len(row['documents']) for row in self.sets), 36)
        self.assertEqual(sum(len(row['focus_vocabulary']) for row in self.sets), 72)


if __name__ == '__main__':
    unittest.main()
