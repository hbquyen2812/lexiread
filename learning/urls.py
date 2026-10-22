from django.urls import path
from . import views as v
urlpatterns=[
 path('api/catalog/',v.catalog),path('api/catalog/<slug:slug>/open/',v.open_lesson),
 path('api/readings/<uuid:pk>/progress/',v.reading_progress),
 path('api/readings/<uuid:pk>/quiz/',v.reading_quiz),
 path('api/readings/<uuid:pk>/questions/',v.reading_questions),
 path('',v.index,name='home'),path('health/',v.health),path('api/bootstrap/',v.bootstrap),
 path('api/readings/',v.readings),path('api/readings/<uuid:pk>/',v.reading_detail),
 path('api/readings/<uuid:pk>/analyse/',v.analyse_reading),path('api/vocabulary/',v.vocabulary),
 path('api/vocabulary/<uuid:pk>/',v.vocabulary_detail),path('api/vocabulary/<uuid:pk>/review/',v.review),
 path('api/exercises/next/',v.next_exercise),path('api/exercises/<uuid:pk>/answer/',v.answer_exercise),
 path('api/prompts/',v.prompts),path('api/ai/lookup/',v.lookup),path('api/ai/words/',v.enrich_words),
 path('api/backup/',v.backup),path('api/export.csv',v.export_csv),path('api/restore/',v.restore),
]
