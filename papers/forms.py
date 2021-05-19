"""
Forms
"""
import bleach
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _

from papers import models, utils


class PaperCreateForm(forms.Form):
    """
    Form to create a new paper
    """

    title = forms.CharField(label=_("Title"))
    language_code = forms.ChoiceField(
        label=" ", widget=forms.RadioSelect, choices=settings.LANGUAGES
    )
    content = forms.CharField(widget=CKEditorWidget, label=_("Content"))
    deadline = forms.DateTimeField(initial=timezone.now(), label=_("Deadline"))

    def clean_content(self):
        """
        Clean content
        """
        return bleach.clean(
            self.cleaned_data["content"],
            tags=settings.BLEACH_ALLOWED_TAGS,
            attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
        )


class PaperUpdateForm(forms.ModelForm):
    state = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={"class": "radioSelection"}),
        choices=models.PAPER_STATES,
        label=_("state"),
        help_text="ⓘ Hover over the states for more information.",
    )

    class Meta:
        model = models.Paper
        fields = ["amendment_deadline", "state", "authors"]


class AmendmentForm(forms.Form):
    """
    Form to create or update an amendment
    """

    title = forms.CharField(label=_("title"))
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
            self.fields["title"].initial = self.amendment.title
            self.fields["content"].initial = utils.add_lite_classes(
                self.amendment.content
            )
            self.fields["reason"].initial = self.amendment.reason

    def create_amendment(self, translation, author):
        """
        Creates a new amendment from the form data and to the given translation and user.
        This has to be called after `is_valid` has been called and succeded.
        """
        content = self.cleaned_data["content"]
        reason = self.cleaned_data["reason"]
        title = self.cleaned_data["title"]

        return models.Amendment.objects.create(
            paper=translation.paper,
            language_code=translation.language_code,
            author=author,
            title=title,
            content=content,
            state="draft",
            reason=reason,
        )

    def clean(self):
        # prevent the creation of new amendments if the server time is past the paper's deadline
        deadline = None
        if self.translation:
            deadline = self.translation.paper.amendment_deadline
        if self.amendment:
            deadline = self.amendment.paper.amendment_deadline
        if deadline and timezone.now() > deadline:
            raise ValidationError(
                _("Cannot create new amendments past a paper's deadline.")
            )

    def clean_content(self):
        """
        Cleans the given content from malicious html tags.
        """
        return bleach.clean(
            self.cleaned_data["content"],
            tags=settings.BLEACH_ALLOWED_TAGS,
            attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
        )

    def clean_reason(self):
        """
        Cleans the given reason from any malicious tags.
        """
        return bleach.clean(
            self.cleaned_data["reason"],
            tags=settings.BLEACH_ALLOWED_TAGS,
            attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
        )


class TranslationForm(forms.ModelForm):
    """
    Form to create or update a translation
    """

    class Meta:
        model = models.PaperTranslation
        fields = ["title", "content", "needs_update"]

    def clean_content(self):
        """
        Clean content
        """
        return bleach.clean(
            self.cleaned_data["content"],
            tags=settings.BLEACH_ALLOWED_TAGS,
            attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
        )


class CommentForm(forms.Form):
    """
    Form for comments and private notes
    """

    comment = forms.CharField(
        widget=CKEditorWidget(config_name="basic"), label=_("Comment")
    )

    def clean_comment(self):
        """
        Clean comments from script tasks
        """
        return bleach.clean(
            self.cleaned_data["comment"],
            tags=settings.BLEACH_ALLOWED_TAGS,
            attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
        )


class UserUploadForm(forms.Form):
    """
    Form for uploading a bunch of users in bulk
    """

    csv_file = forms.FileField()


class RecommendationForm(forms.ModelForm):
    class Meta:
        model = models.Recommendation
        fields = ["recommendation", "reason"]

    def clean_reason(self):
        """
        Clean comments from script tasks
        """
        return bleach.clean(
            self.cleaned_data["reason"],
            tags=settings.BLEACH_ALLOWED_TAGS,
            attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
        )


class AmendmentChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, amendment):
        return amendment.title


class AmendmentSelect(forms.Form):
    merge = AmendmentChoiceField(
        queryset=models.Amendment.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label=_("Amendments to merge into final paper"),
        help_text=_(
            "Select all amendments that you wish to merge into the final paper. "
            "Accepted amendments have already been selected."
        ),
    )

    def __init__(self, *args, **kwargs):
        translation = kwargs.pop("translation")
        super().__init__(*args, **kwargs)
        self.fields["merge"].queryset = models.Amendment.objects.filter(
            paper_id=translation.paper_id, language_code=translation.language_code
        )
        self.fields["merge"].initial = models.Amendment.objects.filter(
            paper_id=translation.paper_id,
            language_code=translation.language_code,
            state="accepted",
        )


class FinalizePaperForm(forms.Form):
    title = forms.CharField(label=_("title"))
    content = forms.CharField(
        widget=CKEditorWidget(config_name="track-changes"), label=_("content")
    )
