from datetime import UTC, datetime
from typing import Any
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from demoapp.forms import LongRunningModelForm
from demoapp.models import LongRunningModel
from demoapp.tasks import task_create_long_running_model


# Create your views here.
class HomePageView(TemplateView):
    template_name = "demoapp/pages/homepage.html"


class LongRunningView(FormView):
    form_class = LongRunningModelForm
    template_name = "demoapp/pages/long_running.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data["object_list"] = LongRunningModel.objects.all()
        return data

    def get_success_url(self) -> str:
        return reverse("demoapp:long_running")

    def form_valid(self, form: LongRunningModelForm) -> HttpResponse:
        model = task_create_long_running_model(form.cleaned_data["data"], datetime.now(UTC))
        return redirect(self.get_success_url())
