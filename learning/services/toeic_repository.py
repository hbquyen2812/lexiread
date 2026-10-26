"""Live content always comes from PostgreSQL; file edits are not a publishing API."""
import copy
from learning.models import ToeicPractice
from .core import InputError


def toeic_sets():
    return tuple(copy.deepcopy(obj.content) for obj in ToeicPractice.objects.filter(published=True))


def get_toeic_set(slug):
    obj=ToeicPractice.objects.filter(pk=slug,published=True).first()
    if not obj: raise InputError('Không tìm thấy bộ luyện TOEIC đang xuất bản.')
    return copy.deepcopy(obj.content)


def public_toeic_set(slug):
    practice=get_toeic_set(slug)
    practice.pop('editorial',None)
    practice['questions']=[{key:copy.deepcopy(q[key]) for key in ('id','part','prompt','options','document_ids')} for q in practice['questions']]
    return practice
