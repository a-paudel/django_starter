from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView as _DjangoLoginView, LogoutView as _DjangoLogoutView

from users.forms import LoginForm

# Create your views here.


class LoginView(_DjangoLoginView):
    template_name = "users/pages/login.html"
    form_class = LoginForm


class LogoutView(_DjangoLogoutView):
    pass
