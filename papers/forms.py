from ckeditor.widgets import CKEditorWidget
from django import forms
from django.conf import settings
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
    content = forms.CharField(widget=CKEditorWidget(config_name="track-changes"))
    reason = forms.CharField(widget=CKEditorWidget(config_name="basic"))
    author = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.translation = kwargs.pop("translation", None)
        self.amendmend = kwargs.pop("amendmend", None)
        super().__init__(*args, **kwargs)
        if self.translation:
            self.fields["content"].initial = self.translation.content
        elif self.amendmend:
            self.fields["content"].initial = self.amendmend.content
            self.fields["reason"].initial = self.amendmend.reason
            self.fields["author"].initial = self.amendmend.author.name


class CommentForm(forms.Form):
    name = forms.CharField()
    comment = forms.CharField()
