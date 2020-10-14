from django import forms
from django.conf import settings
from ckeditor.widgets import CKEditorWidget


from papers import models

class PaperCreateForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=CKEditorWidget)
    language_code = forms.ChoiceField(choices=settings.LANGUAGES)
    state = forms.ChoiceField(choices=models.STATES)


class AmendmendForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=CKEditorWidget(config_name="track-changes"))


    def __init__(self, *args, **kwargs):
        self.translation = kwargs.pop('translation')
        super().__init__(*args, **kwargs)
        self.fields['content'].initial = self.translation.content
        self.fields['title'].initial = self.translation.title
