from django import forms
from core.forms import BaseForm
from demoapp.models import LongRunningModel


class LongRunningModelForm(BaseForm, forms.ModelForm):
    class Meta:
        model = LongRunningModel
        fields = "__all__"
