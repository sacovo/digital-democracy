"""
Forms
"""
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.conf import settings

from papers import models


class PaperCreateForm(forms.Form):
    """
    Form to create a new paper
    """

    title = forms.CharField()
    language_code = forms.ChoiceField(
        label=" ", widget=forms.RadioSelect, choices=settings.LANGUAGES
    )
    content = forms.CharField(widget=CKEditorWidget)
    state = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={"class": "radioSelection"}),
        choices=models.STATES,
    )


class AmendmendForm(forms.Form):
    """
    Form to create or update an amendment
    """

    content = forms.CharField(widget=CKEditorWidget(config_name="track-changes"))
    reason = forms.CharField(widget=CKEditorWidget(config_name="basic"))

    def __init__(self, *args, **kwargs):
        self.translation = kwargs.pop("translation", None)
        self.amendmend = kwargs.pop("amendmend", None)
        super().__init__(*args, **kwargs)

        if self.translation:
            self.fields["content"].initial = self.translation.content

        elif self.amendmend:
            self.fields["content"].initial = self.amendmend.content
            self.fields["reason"].initial = self.amendmend.reason


class TranslationForm(forms.ModelForm):
    """
    Form to create or update a translation
    """

    class Meta:
        model = models.PaperTranslation
        fields = ["title", "content"]


class CommentForm(forms.Form):
    """
    Form for comments
    """

    comment = forms.CharField(widget=CKEditorWidget(config_name="basic"))
