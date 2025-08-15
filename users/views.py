from django.views.generic import CreateView
from django.contrib.auth.views import LoginView as _DjangoLoginView, LogoutView as _DjangoLogoutView
from config import settings
from users.forms import LoginForm, RegisterForm

# Create your views here.


class LoginView(_DjangoLoginView):
    template_name = "users/pages/login.html"
    form_class = LoginForm


class LogoutView(_DjangoLogoutView):
    pass


class RegisterView(CreateView):
    template_name = "users/pages/register.html"
    form_class = RegisterForm
    success_url = settings.LOGIN_REDIRECT_URL
