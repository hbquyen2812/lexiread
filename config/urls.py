from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LogoutView
from learning.views import PrivateLoginView
urlpatterns = [path('admin/',admin.site.urls), path('login/',PrivateLoginView.as_view(),name='login'),
               path('logout/',LogoutView.as_view(),name='logout'), path('',include('learning.urls'))]
