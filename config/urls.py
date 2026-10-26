from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LogoutView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordChangeDoneView
from learning.views import EmailLoginView
from learning.accounts.views import signup, RecoveryView, profile, AccountPasswordChangeView
urlpatterns = [path('admin/',admin.site.urls), path('login/',EmailLoginView.as_view(),name='login'),
               path('signup/',signup,name='signup'),
               path('account/',profile,name='account'),
               path('account/password/',AccountPasswordChangeView.as_view(),name='password_change'),
               path('account/password/done/',PasswordChangeDoneView.as_view(),name='password_change_done'),
               path('password-reset/',RecoveryView.as_view(),name='password_reset'),
               path('password-reset/sent/',PasswordResetDoneView.as_view(),name='password_reset_done'),
               path('reset/<uidb64>/<token>/',PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
               path('reset/complete/',PasswordResetCompleteView.as_view(),name='password_reset_complete'),
               path('logout/',LogoutView.as_view(),name='logout'), path('',include('learning.urls'))]
