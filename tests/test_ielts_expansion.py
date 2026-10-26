"""Editorial integrity checks for the ten original extended reading lessons."""
import json
from pathlib import Path
import re
import unittest

from learning.services.catalog import validate_lesson, grade_lesson
from learning.services.core import paragraphs, normalise

ROOT = Path(__file__).resolve().parents[1]
SLUGS = (
    'ielts-repair-and-reuse', 'ielts-night-trains-return', 'ielts-community-noise-maps',
    'ielts-museum-touch', 'ielts-rooftop-water', 'ielts-wildlife-crossings',
    'ielts-citizen-weather', 'ielts-library-of-things', 'ielts-digital-margins',
    'ielts-food-label-design',
)


def lessons():
    return [json.loads((ROOT / f'data/lessons/{slug}.json').read_text(encoding='utf-8'))
            for slug in SLUGS]


class IeltsExpansionTests(unittest.TestCase):
    def test_complete_original_lesson_contracts(self):
        for lesson in lessons():
            with self.subTest(slug=lesson['slug']):
                validate_lesson(lesson)
                self.assertEqual(lesson['track'], 'ielts')
                self.assertIn('Không phải đề IELTS chính thức', lesson['provenance'])
                self.assertIn('giả định', lesson['provenance'])
                self.assertTrue(400 <= len(lesson['text'].split()) <= 650)
                self.assertEqual(len(lesson['questions']), 10)
                self.assertEqual(len(lesson['analysis']['vocabulary']), 7)
                self.assertEqual(lesson['translation_status'], 'complete')
                self.assertEqual(len(paragraphs(lesson['text'])), 6)
                self.assertEqual(len(lesson['analysis']['translations']), 6)
                for index, item in enumerate(lesson['analysis']['translations']):
                    self.assertEqual(item['index'], index)
                    self.assertTrue(item['vi'].startswith(chr(65 + index) + '. '))
                    self.assertGreater(len(item['vi'].split()), 60)

    def test_extractive_answers_are_in_the_passage_and_limits_match_instructions(self):
        for lesson in lessons():
            paras = paragraphs(lesson['text'])
            for question in lesson['questions']:
                if question['kind'] not in ('gap_fill', 'short_answer'):
                    continue
                with self.subTest(slug=lesson['slug'], question=question['id']):
                    instruction = re.search(r'(ONE|TWO|THREE) WORDS?', question['prompt'])
                    self.assertIsNotNone(instruction)
                    self.assertEqual(question['max_words'], {'ONE': 1, 'TWO': 2, 'THREE': 3}[instruction[1]])
                    for answer in question['accepted_answers']:
                        self.assertIn(normalise(answer), normalise(paras[question['paragraph_index']]))
                        self.assertLessEqual(len(answer.split()), question['max_words'])
                    self.assertIn(normalise(question['answer']), normalise(question['evidence']))

    def test_question_styles_and_answer_positions_are_varied(self):
        all_kinds = set()
        for lesson in lessons():
            all_kinds.update(q['kind'] for q in lesson['questions'])
            mcq = [q['answer'] for q in lesson['questions']
                   if q['kind'] in ('detail', 'inference', 'matching_heading')]
            self.assertGreaterEqual(len(set(mcq)), 2)
            # Correct answers must remain consumable by the same scoring path as existing lessons.
            result = grade_lesson(validate_lesson(lesson), {q['id']: q['answer'] for q in lesson['questions']})
            self.assertEqual((result['score'], result['total']), (10, 10))
        self.assertTrue({'tfng', 'ynng', 'matching_heading', 'matching_information',
                         'gap_fill', 'short_answer', 'inference', 'detail'} <= all_kinds)
        ynng_answers = {q['answer'] for lesson in lessons() for q in lesson['questions'] if q['kind'] == 'ynng'}
        self.assertEqual(ynng_answers, {0, 1, 2})

    def test_vocabulary_has_short_examples_and_usable_patterns(self):
        for lesson in lessons():
            for entry in lesson['analysis']['vocabulary']:
                with self.subTest(slug=lesson['slug'], word=entry['word']):
                    self.assertNotEqual(entry['pos'], 'word / phrase')
                    for field in ('meaning_vi', 'usage_pattern', 'example', 'example_vi', 'note'):
                        self.assertTrue(entry[field].strip())
                    self.assertTrue(entry['synonyms'])
                    self.assertTrue(entry['paraphrases'])
                    self.assertLessEqual(len(entry['example'].split()), 20)
                    self.assertIn(entry['word'], entry['context'])
                    self.assertIn(lesson['level'], entry['tags'])


if __name__ == '__main__':
    unittest.main()
