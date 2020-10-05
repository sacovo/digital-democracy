from django import forms
from django.conf import settings
from ckeditor.widgets import CKEditorWidget


class PaperCreateForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=CKEditorWidget)
    language_code = forms.ChoiceField(choices=settings.LANGUAGES)
