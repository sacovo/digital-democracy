from django import forms
from django.conf import settings
from ckeditor.widgets import CKEditorWidget
from django.template.defaultfilters import mark_safe


from papers import models


class PaperCreateForm(forms.Form):
    title = forms.CharField()
    language_code = forms.ChoiceField(
        label=" ", widget=forms.RadioSelect, choices=settings.LANGUAGES
    )
    content = forms.CharField(widget=CKEditorWidget)
    state = forms.ChoiceField(widget=forms.RadioSelect, choices=models.STATES)


class AmendmendForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=CKEditorWidget(config_name="track-changes"))

    def __init__(self, *args, **kwargs):
        self.translation = kwargs.pop("translation")
        super().__init__(*args, **kwargs)
        self.fields["content"].initial = self.translation.content
        self.fields["title"].initial = self.translation.title
