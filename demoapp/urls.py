from django.urls import path

from demoapp.views import HomePageView


app_name = "demoapp"


urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
]
