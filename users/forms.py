from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from core.forms import BaseForm


class LoginForm(BaseForm, AuthenticationForm):
    pass


class RegisterForm(BaseForm, UserCreationForm):
    pass
