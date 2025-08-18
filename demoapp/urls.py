from django.urls import path

from demoapp.views import HomePageView, LongRunningView


app_name = "demoapp"


urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("long-running/", LongRunningView.as_view(), name="long_running"),
]
