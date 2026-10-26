"""Content integrity and public-guide trust boundary; no network/database needed."""
import copy
import json
import unittest

from learning.services.strategy_guides import (
    GUIDES_PATH, strategy_guide, strategy_guides, validate_strategy_guides,
)


class StrategyGuidesTests(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads(GUIDES_PATH.read_text(encoding='utf-8'))

    def test_complete_original_inventory(self):
        guides = validate_strategy_guides(self.raw)
        self.assertEqual(len(guides), 18)
        self.assertEqual(len(strategy_guides('ielts')), 12)
        self.assertEqual(len(strategy_guides('toeic')), 6)
        kinds = {kind for guide in guides for kind in guide['question_types']}
        self.assertTrue({'tfng', 'ynng', 'matching_heading', 'matching_information',
                         'matching_features', 'matching_sentence_endings', 'multiple_choice',
                         'sentence_completion', 'summary_completion', 'note_completion',
                         'table_completion', 'flowchart_completion', 'diagram_completion',
                         'short_answer', 'time_management', 'part5_grammar', 'part5_vocabulary',
                         'part6_cohesion', 'part6_sentence_insertion', 'part7_single',
                         'part7_multiple'}.issubset(kinds))
        self.assertEqual(len({g['worked_example']['passage'] for g in guides}), len(guides))
        self.assertTrue(all(len(g['worked_example']['explanation_vi']) >= 80 for g in guides))
        self.assertIsNone(strategy_guide('missing-guide'))
        with self.assertRaises(ValueError):
            strategy_guides('unknown')

    def test_user_mutation_cannot_change_shared_guides(self):
        guide = strategy_guide('ielts-tfng')
        guide['steps'].clear()
        guide['worked_example']['answer'] = 'changed'
        self.assertGreater(len(strategy_guide('ielts-tfng')['steps']), 0)
        self.assertEqual(strategy_guide('ielts-tfng')['worked_example']['answer'], 'FALSE')

    def test_external_source_cannot_execute_or_leave_official_allowlist(self):
        for url in ['javascript:alert(1)', 'http://ielts.org/test',
                    'https://ielts.org@localhost/', 'https://ielts.org.example.com/',
                    'https://127.0.0.1/', 'https://ielts.org:444/', 'https://ielts.org/\nattack']:
            with self.subTest(url=url):
                raw = copy.deepcopy(self.raw)
                raw['guides'][0]['sources'][0]['url'] = url
                with self.assertRaises(ValueError):
                    validate_strategy_guides(raw)

    def test_broken_example_answer_or_duplicate_choices_cannot_publish(self):
        for field, value in [('answer', 'NONE'), ('options', ['TRUE', 'TRUE'])]:
            with self.subTest(field=field):
                raw = copy.deepcopy(self.raw)
                raw['guides'][0]['worked_example'][field] = value
                with self.assertRaises(ValueError):
                    validate_strategy_guides(raw)

    def test_text_example_accepts_reviewed_variants_but_rejects_invalid_lists(self):
        self.assertEqual(strategy_guide('ielts-short-answers')['worked_example']['accepted_answers'],
                         ['the courtyard', 'courtyard'])
        for accepted in [[], ['not the answer'], 'the courtyard', ['the courtyard', 'the courtyard']]:
            with self.subTest(accepted=accepted):
                raw = copy.deepcopy(self.raw)
                example = next(g['worked_example'] for g in raw['guides'] if g['id'] == 'ielts-short-answers')
                example['accepted_answers'] = accepted
                with self.assertRaises(ValueError):
                    validate_strategy_guides(raw)

    def test_missing_explanation_steps_sources_and_wrong_track_are_rejected(self):
        for field, value in [('steps', []), ('sources', []), ('duration_minutes', True),
                             ('duration_minutes', -1), ('checked_at', 'yesterday'),
                             ('practice_query', {'track': 'toeic'}), ('worked_example', {}),
                             ('id', self.raw['guides'][1]['id'])]:
            with self.subTest(field=field):
                raw = copy.deepcopy(self.raw)
                raw['guides'][0][field] = value
                with self.assertRaises(ValueError):
                    validate_strategy_guides(raw)


if __name__ == '__main__':
    unittest.main()
