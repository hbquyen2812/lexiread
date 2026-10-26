from django.urls import path
from . import views as v
from . import foundation_views as f
urlpatterns=[
 path('api/learn/overview/',f.overview),path('api/learn/plan/',f.plan),
 path('api/learn/dictionary/',f.dictionary),path('api/learn/sources/',f.sources),
 path('api/learn/vocabulary/<slug:unit_id>/save/',f.save_collection),
 path('api/learn/<slug:kind>/<slug:unit_id>/submit/',f.submit),
 path('api/learn/<slug:kind>/<slug:unit_id>/',f.unit_detail),
 path('guides/',v.guides,name='guides'),
 path('api/catalog/',v.catalog),path('api/catalog/<slug:slug>/open/',v.open_lesson),
 path('api/toeic/',v.toeic_catalog),path('api/toeic/<slug:slug>/',v.toeic_detail),
 path('api/toeic/<slug:slug>/submit/',v.toeic_submit),
 path('api/readings/<uuid:pk>/progress/',v.reading_progress),
 path('api/readings/<uuid:pk>/quiz/',v.reading_quiz),
 path('api/readings/<uuid:pk>/questions/',v.reading_questions),
 path('',v.index,name='home'),path('health/',v.health),path('api/bootstrap/',v.bootstrap),
 path('api/activity/visit/',v.activity_visit),path('api/analytics/',v.analytics),
 path('api/community/',v.community),
 path('api/readings/',v.readings),path('api/readings/<uuid:pk>/',v.reading_detail),
 path('api/readings/<uuid:pk>/analyse/',v.analyse_reading),path('api/vocabulary/',v.vocabulary),
 path('api/vocabulary/sources/',v.vocabulary_sources),
 path('api/vocabulary/deck/',v.personal_deck),
 path('api/vocabulary/<uuid:pk>/',v.vocabulary_detail),path('api/vocabulary/<uuid:pk>/review/',v.review),
 path('api/exercises/next/',v.next_exercise),path('api/exercises/<uuid:pk>/answer/',v.answer_exercise),
 path('api/prompts/',v.prompts),path('api/ai/lookup/',v.lookup),path('api/ai/words/',v.enrich_words),
 path('api/backup/',v.backup),path('api/export.csv',v.export_csv),path('api/restore/',v.restore),
]
