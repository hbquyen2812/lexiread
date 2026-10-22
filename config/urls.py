from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LogoutView
from learning.views import EmailLoginView
urlpatterns = [path('admin/',admin.site.urls), path('login/',EmailLoginView.as_view(),name='login'),
               path('logout/',LogoutView.as_view(),name='logout'), path('',include('learning.urls'))]
