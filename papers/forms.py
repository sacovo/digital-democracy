"""
Forms
"""
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.conf import settings
from django.utils.translation import gettext as _

from papers import models


class PaperCreateForm(forms.Form):
    """
    Form to create a new paper
    """

    title = forms.CharField(label=_("title"))
    language_code = forms.ChoiceField(
        label=" ", widget=forms.RadioSelect, choices=settings.LANGUAGES
    )
    content = forms.CharField(widget=CKEditorWidget, label=_("content"))
    state = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={"class": "radioSelection"}),
        choices=models.STATES,
        label=_("state"),
    )


class AmendmentForm(forms.Form):
    """
    Form to create or update an amendment
    """

    content = forms.CharField(
        widget=CKEditorWidget(config_name="track-changes"), label=_("content")
    )
    reason = forms.CharField(
        widget=CKEditorWidget(config_name="basic"), label=_("reason")
    )

    def __init__(self, *args, **kwargs):
        self.translation = kwargs.pop("translation", None)
        self.amendment = kwargs.pop("amendment", None)
        super().__init__(*args, **kwargs)

        if self.translation:
            self.fields["content"].initial = self.translation.content

        elif self.amendment:
            self.fields["content"].initial = self.amendment.content
            self.fields["reason"].initial = self.amendment.reason

    def create_amendment(self, translation, author):
        """
        Creates a new amendment from the form data and to the given translation and user.
        This has to be called after `is_valid` has been called and succeded.
        """
        content = self.cleaned_data["content"]
        reason = self.cleaned_data["reason"]

        return models.Amendment.objects.create(
            paper=translation.paper,
            language_code=translation.language_code,
            author=author,
            content=content,
            state="draft",
            reason=reason,
        )


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

    comment = forms.CharField(
        widget=CKEditorWidget(config_name="basic"), label=_("comment")
    )
