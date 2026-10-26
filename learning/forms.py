from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Tên đăng nhập hoặc email", max_length=254,
        widget=forms.TextInput(
            attrs={"autocomplete": "username", "autofocus": True, "placeholder": "Tên đăng nhập hoặc email"}
        ),
    )
    error_messages = {
        "invalid_login": "Tên đăng nhập/email hoặc mật khẩu không đúng.",
        "inactive": "Tài khoản này đang bị khóa.",
    }

    def clean(self):
        identifier = self.cleaned_data.get("username", "").strip()
        if identifier:
            query = {"email__iexact": identifier} if "@" in identifier else {"username__iexact": identifier}
            matches = list(
                get_user_model().objects.filter(**query).values_list("username", flat=True)[:2]
            )
            if len(matches) != 1:
                raise ValidationError(self.error_messages["invalid_login"], code="invalid_login")
            self.cleaned_data["username"] = matches[0]
        return super().clean()


class UniqueEmailMixin:
    def clean_email(self):
        user_model = get_user_model()
        email = user_model.objects.normalize_email(self.cleaned_data.get("email", "")).strip().lower()
        if not email:
            raise ValidationError("Mỗi tài khoản cần một email.")
        matches = user_model.objects.filter(email__iexact=email)
        if self.instance.pk:
            matches = matches.exclude(pk=self.instance.pk)
        if matches.exists():
            raise ValidationError("Email này đã thuộc một tài khoản khác.")
        return email


class EmailUserCreationForm(UniqueEmailMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")


class EmailUserChangeForm(UniqueEmailMixin, UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = get_user_model()
        fields = "__all__"
