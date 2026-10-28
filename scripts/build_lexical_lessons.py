"""Build original short lessons from reviewed source rows; no network or AI calls."""
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from learning.services.foundation_content import validate_unit, validate_questions

DATA = ROOT / 'data/lexical'
RELATIONS = {
    'verb-noun': ('Verb + noun', 'Chọn động từ đi cùng danh từ. Học cả cụm để dùng tự nhiên hơn.', 'A2', 'B1'),
    'adjective-noun': ('Adjective + noun', 'Tính từ giúp nói rõ đặc điểm của danh từ. Chú ý những cách kết hợp quen dùng.', 'A2', 'B2'),
    'adverb-adjective': ('Adverb + adjective', 'Trạng từ đứng trước tính từ để nhấn mạnh hoặc làm rõ mức độ.', 'B1', 'B2'),
    'verb-preposition': ('Verb + preposition', 'Học động từ cùng giới từ và phần theo sau. Một động từ có thể đổi nghĩa khi đổi giới từ.', 'A2', 'B2'),
    'adjective-preposition': ('Adjective + preposition', 'Ghi nhớ tính từ cùng giới từ. Sau giới từ thường là danh từ, đại từ hoặc động từ thêm -ing.', 'A2', 'B1'),
    'noun-preposition': ('Noun + preposition', 'Danh từ cũng thường đi với một giới từ nhất định. Hãy học cả cụm trong câu.', 'B1', 'B2'),
    'verb-adverb': ('Verb + adverb', 'Trạng từ cho biết hành động diễn ra như thế nào. Học cả cụm cùng một câu ngắn.', 'A2', 'B1'),
    'noun-noun': ('Noun + noun', 'Danh từ đứng trước bổ nghĩa cho danh từ đứng sau: coffee shop là quán cà phê.', 'A2', 'B1'),
}


def rows(filename, width):
    for line in (DATA / filename).read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        parts = line.split('|')
        assert len(parts) == width, line
        yield parts


def question(identifier, example, answer, distractors, meaning, explanation):
    pattern = r'\b' + re.escape(answer) + r'\b'
    assert re.search(pattern, example, re.I), (example, answer)
    prompt = re.sub(pattern, '____', example, count=1, flags=re.I)
    options = list(distractors)
    slot = int(hashlib.sha256(identifier.encode()).hexdigest()[:8], 16) % 4
    options.insert(slot, answer)
    return dict(id=identifier, prompt=prompt, hint_vi=meaning, options=options, answer=slot,
                prompt_lang='en', explanation_vi=explanation)


def build():
    lessons = []
    groups = defaultdict(list)
    for relation, phrase, meaning, example, translation, answer, distractors in rows('collocations.psv', 7):
        groups[relation].append((phrase, meaning, example, translation, answer, distractors))
    for relation, entries in groups.items():
        title, tip, first_level, second_level = RELATIONS[relation]
        assert len(entries) >= 6 and len(entries) % 6 == 0
        for offset in range(0, len(entries), 6):
            number = offset // 6 + 1
            unit = dict(id=f'patterns-{relation}-{number}', title=f'{title} · {number}',
                        topic='Collocations', level=first_level if not offset else second_level if offset == 6 else 'B2',
                        track='lexical_patterns', pattern_kind='collocations', relation=relation,
                        description=tip, tip=tip, minutes=8, tags=['Collocations', title], words=[], questions=[],
                        source_urls=['https://dictionary.cambridge.org/grammar/british-grammar/collocation'])
            for i, (phrase, meaning, example, translation, answer, distractors) in enumerate(entries[offset:offset+6]):
                unit['words'].append(dict(word=phrase, meaning_vi=meaning, example=example,
                    example_translation=translation, usage_pattern=title, part_of_speech='phrase'))
                unit['questions'].append(question(f'q{i+1}', example, answer, distractors.split(','), meaning,
                    f'Chọn “{answer}” để tạo cụm “{phrase}” ({meaning}). {translation}'))
            lessons.append(unit)
    families = defaultdict(list)
    for family, level, word, pos, meaning, example, translation, cue in rows('families.psv', 8):
        families[(family, level)].append(dict(word=word, part_of_speech=pos, meaning_vi=meaning,
            example=example, example_translation=translation, usage_pattern=cue, family=family))
    # Two families per lesson; each lesson has a single level and at most eight forms.
    by_level = defaultdict(list)
    for (family, level), forms in families.items():
        assert len(forms) == 4
        by_level[level].append((family, forms))
    for level, bundles in by_level.items():
        for offset in range(0, len(bundles), 2):
            selected = bundles[offset:offset+2]
            first = selected[0][0]
            unit = dict(id=f'patterns-family-{first}', title=' / '.join(f for f, _ in selected),
                topic='Word families', level=level, track='lexical_patterns', pattern_kind='families',
                relation='word-family', description='Nhận ra từ loại và chọn đúng dạng từ trong câu.',
                tip='Xem vị trí trống cần từ loại nào, rồi xét nghĩa của cả câu. Các từ cùng họ có thể khác nghĩa; không phải họ nào cũng có đủ bốn từ loại.',
                minutes=10, tags=['Word families'], words=[], questions=[],
                source_urls=['https://en-word.net/', 'https://dictionary.cambridge.org/grammar/british-grammar/word-formation'])
            for family, forms in selected:
                for w in forms:
                    unit['words'].append(w)
                    unit['questions'].append(question(f'q{len(unit["questions"])+1}', w['example'], w['word'],
                        [r['word'] for r in forms if r['word'] != w['word']], w['meaning_vi'],
                        f'{w["usage_pattern"]} {w["word"]}: {w["meaning_vi"]}. {w["example_translation"]}'))
            lessons.append(unit)
    for unit in lessons:
        validate_unit(unit, 'vocabulary')
        validate_questions(unit['questions'])
    assert len({u['id'] for u in lessons}) == len(lessons)
    return dict(version=1, author='Lexivela', content_type='original teaching examples and exercises',
                collections=lessons)


if __name__ == '__main__':
    data = build()
    (DATA / 'lessons.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'{len(data["collections"])} lessons; {sum(len(u["words"]) for u in data["collections"])} entries/questions.')
