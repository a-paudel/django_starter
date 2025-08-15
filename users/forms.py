from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from core.forms import BaseForm
from users.models import User


class LoginForm(BaseForm, AuthenticationForm):
    pass


class RegisterForm(BaseForm, UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
