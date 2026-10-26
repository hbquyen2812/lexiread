import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from learning.forms import EmailUserCreationForm, UniqueEmailMixin


def clean_public_username(username, user_id=None):
    username = username.strip().lower()
    if not re.fullmatch(r'[a-z0-9][a-z0-9_.-]{2,29}', username):
        raise forms.ValidationError('Dùng 3–30 ký tự: chữ không dấu, số, dấu chấm, gạch dưới hoặc gạch ngang.')
    matches = get_user_model().objects.filter(username__iexact=username)
    if user_id:
        matches = matches.exclude(pk=user_id)
    if matches.exists():
        raise forms.ValidationError('Tên đăng nhập đã được sử dụng.')
    return username


class SignupForm(EmailUserCreationForm):
    email = forms.EmailField(label='Email khôi phục', max_length=254,
                             widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

    def clean_username(self):
        return clean_public_username(self.cleaned_data['username'])


class ProfileForm(UniqueEmailMixin, forms.ModelForm):
    current_password = forms.CharField(label='Mật khẩu hiện tại (khi đổi username hoặc email)',
        required=False, widget=forms.PasswordInput(attrs={'autocomplete':'current-password'}))

    class Meta:
        model = get_user_model()
        fields = ('first_name','last_name','username','email')
        labels = {'first_name':'Tên','last_name':'Họ','username':'Tên đăng nhập','email':'Email khôi phục'}

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.original_username=self.instance.username
        self.original_email=self.instance.email
        self.fields['email'].required=True
        self.fields['email'].widget.attrs['autocomplete']='email'
        self.fields['username'].widget.attrs['autocomplete']='username'

    def clean_username(self):
        value=self.cleaned_data['username']
        if value==self.original_username: return value  # Keep valid legacy usernames.
        return clean_public_username(value,self.instance.pk)

    def clean(self):
        cleaned=super().clean()
        if (cleaned.get('username',self.original_username)!=self.original_username or
                cleaned.get('email',self.original_email).lower()!=self.original_email.lower()):
            if not self.instance.check_password(cleaned.get('current_password','')):
                self.add_error('current_password','Nhập đúng mật khẩu hiện tại để thay đổi thông tin đăng nhập.')
        return cleaned


class RecoveryForm(PasswordResetForm):
    """Legacy duplicate emails are ambiguous: never reset multiple accounts."""
    def get_users(self, email):
        users = list(get_user_model().objects.filter(email__iexact=email.strip())[:2])
        return [users[0]] if len(users) == 1 and users[0].is_active and users[0].has_usable_password() else []
