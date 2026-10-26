import logging
from urllib.parse import urlparse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordChangeView
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from learning.views import login_key
from .forms import SignupForm, RecoveryForm, ProfileForm
from .limits import consume, lock_identities

logger = logging.getLogger(__name__)


@sensitive_post_parameters('password1', 'password2')
@never_cache
def signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    form = SignupForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                allowed = consume('signup', login_key(request))
                lock_identities()
                if allowed and form.is_valid():
                    user = form.save()
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    return redirect('/')
        except IntegrityError:
            form.add_error(None, 'Thông tin tài khoản đã được sử dụng. Hãy thử tên khác hoặc khôi phục bằng email.')
            allowed = True
        if not allowed:
            return render(request, 'registration/signup.html', {'form': form, 'limited': True}, status=429)
    return render(request, 'registration/signup.html', {'form': form})


@login_required
@sensitive_post_parameters('current_password')
@never_cache
def profile(request):
    form=ProfileForm(instance=request.user)
    if request.method=='POST':
        try:
            with transaction.atomic():
                allowed=consume('profile',login_key(request))
                if allowed:
                    lock_identities()
                    current=get_user_model().objects.select_for_update().get(pk=request.user.pk)
                    form=ProfileForm(request.POST,instance=current)
                    if form.is_valid():
                        updated=form.save(commit=False)
                        updated.save(update_fields=['first_name','last_name','username','email'])
                        messages.success(request,'Đã lưu thông tin tài khoản.')
                        return redirect('account')
                else:
                    return render(request,'registration/profile.html',{'form':form,'limited':True},status=429)
        except IntegrityError:
            form.add_error(None,'Thông tin đăng nhập đã được sử dụng. Hãy kiểm tra và thử lại.')
    return render(request,'registration/profile.html',{'form':form})


class AccountPasswordChangeView(PasswordChangeView):
    template_name='registration/password_change_form.html'
    success_url=reverse_lazy('password_change_done')

    def post(self,request,*args,**kwargs):
        with transaction.atomic():
            allowed=consume('password-change',login_key(request))
        if not allowed:
            return render(request,self.template_name,{'limited':True,'form':self.get_form()},status=429)
        return super().post(request,*args,**kwargs)


@method_decorator(never_cache, name='dispatch')
class RecoveryView(PasswordResetView):
    form_class = RecoveryForm
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.txt'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

    def get_context_data(self, **kwargs):
        return super().get_context_data(recovery_enabled=settings.EMAIL_RECOVERY_ENABLED, **kwargs)

    def form_valid(self, form):
        if not settings.EMAIL_RECOVERY_ENABLED:
            form.add_error(None, 'Tính năng gửi email khôi phục chưa được mở. Vui lòng liên hệ quản trị viên.')
            return self.form_invalid(form)
        with transaction.atomic():
            allowed = consume('recovery', login_key(self.request), form.cleaned_data['email'])
        if allowed:
            try:
                canonical=urlparse(settings.PUBLIC_SITE_URL) if settings.PUBLIC_SITE_URL else None
                form.save(use_https=canonical.scheme=='https' if canonical else self.request.is_secure(),
                    domain_override=canonical.netloc if canonical else None,
                    from_email=self.from_email,request=self.request,token_generator=self.token_generator,
                    email_template_name=self.email_template_name,subject_template_name=self.subject_template_name,
                    html_email_template_name=self.html_email_template_name,extra_email_context=self.extra_email_context)
            except Exception:
                # Same public outcome for delivery failure, unknown and ambiguous emails.
                logger.warning('Password recovery delivery failed; check the mail service configuration.')
        return redirect(self.success_url)
