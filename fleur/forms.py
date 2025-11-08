from django import forms
from .models import HomeVideo

class HomeVideoForm(forms.ModelForm):
    class Meta:
        model = HomeVideo
        fields = ["file"]
        widgets = {
            "file": forms.FileInput(attrs={"accept": "video/*", "class": "form-control"})
        }
