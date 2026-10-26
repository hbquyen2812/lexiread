"""Deterministic marking helpers. Python 3.10+, standard library only."""
import re
import unicodedata

def normalize_answer(value):
    # Keep punctuation/spelling significant; only normalize Unicode, case, whitespace.
    return ' '.join(unicodedata.normalize('NFKC',str(value)).casefold().split())

def word_count(value):
    # Whitespace-separated words; hyphenated compounds count as one word.
    return len(str(value).split())

def grade(question, response):
    """response is option key or text. Never use fuzzy matching for exam answers."""
    if response is None:
        return False
    values = response if isinstance(response,list) else [response]
    if len(values) != len(question['answer']):
        return False
    if question.get('max_words') is not None:
        if any(word_count(v)>question['max_words'] for v in values):
            return False
    if question['type'] in ('gap_fill','short_answer'):
        accepted=question.get('accepted_answers') or question['answer']
        return len(values)==1 and normalize_answer(values[0]) in {normalize_answer(x) for x in accepted}
    return {normalize_answer(x) for x in values} == {normalize_answer(x) for x in question['answer']}
