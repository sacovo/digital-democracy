"""
Database models for app papers
"""
from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.utils.html import mark_safe
from django.utils.translation import gettext as _

from papers import utils
from papers.utils import index_of_first_change, index_of_last_change

# Create your models here.

PAPER_STATES = (
    (
        "draft",
        mark_safe(
            u'<u title="ⓘ This paper is a private draft and not ready for amendments.">Draft</u>'
        ),
    ),
    (
        "public",
        mark_safe(
            u'<u title="ⓘ This paper is public and ready for amendments.">Published</u>'
        ),
    ),
    (
        "final",
        mark_safe(
            u'<u title="ⓘ This paper is final no more changes can be made.">Finalized</u>'
        ),
    ),
)

AMENDMENT_STATES = (
    ("draft", mark_safe(u'<u title="ⓘ This amendment is a draft.">Draft</u>')),
    ("public", mark_safe(u'<u title="ⓘ This amendment is public.">Published</u>')),
    (
        "retracted",
        mark_safe(u'<u title="ⓘ This amendment is retracted.">Retracted</u>'),
    ),
    ("approved", mark_safe(u'<u title="ⓘ This amendment is a approved.">Approved</u>')),
)


class Tag(models.Model):
    """
    Tagging for amendments
    """

    name = models.CharField(max_length=35)
    created_at = models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return self.name


class Author(models.Model):
    """
    Represents an author of a paper or an amendment, used as a proxy to auth.User
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("user"),
    )

    def __str__(self):
        return self.name

    @property
    def name(self):
        """
        The name of the user
        """
        return str(self.user)

    class Meta:
        verbose_name = _("author")
        verbose_name_plural = _("authors")


class Paper(models.Model):
    """
    Collects the information about a paper.
    """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    edited_at = models.DateTimeField(auto_now=True, verbose_name=_("edited at"))
    amendment_deadline = models.DateTimeField(verbose_name=_("deadline"))

    working_title = models.CharField(max_length=255, verbose_name=_("working title"))

    state = models.CharField(
        choices=PAPER_STATES, max_length=20, verbose_name=_("state")
    )

    authors = models.ManyToManyField(Author, blank=True, verbose_name=_("authors"))

    def is_author(self, user):
        return self.authors.filter(user=user).exists()

    def __str__(self):
        return self.working_title

    def missing_translations(self):
        """
        Iterator over all language tuples where there is no translation for this paper
        """
        for language in settings.LANGUAGES:
            if not bool(self.translation_set.filter(language_code=language[0])):
                yield language

    def has_translation_for_language(self, language_code):
        """
        returns true if there is a translation for the given language
        """
        return bool(self.translation_set.filter(language_code=language_code))

    def translation_for(self, language_code):
        """
        Returns the according translation
        """
        return self.translation_set.get(language_code=language_code)

    def count_amendments(self):
        """
        Return the amount of public amendments to this paper
        """
        return len(self.amendment_set.filter(state="public"))

    def count_comments(self):
        """
        Return the amount of comments to this paper
        """
        return len(
            Comment.objects.filter(amendment__paper=self, amendment__state="public")
        )

    def latest_amendment(self):
        """
        Return the datetime of the latest amendment, fails if no amendments
        """
        return self.amendment_set.order_by("-created_at").first()

    def latest_comment(self):
        """
        Return the latest comment to this amendment
        """
        return (
            Comment.objects.filter(amendment__paper=self, amendment__state="public")
            .order_by("-created_on")
            .first()
        )

    def get_all_papers(self):
        """
        Return all papers for further use
        """
        return Paper.objects.all()

    class Meta:
        verbose_name = _("paper")
        verbose_name_plural = _("papers")


class PaperTranslation(models.Model):
    """
    The content of a paper in a specific language.
    """

    needs_update = models.BooleanField(
        default=False,
        help_text=_("Do the other translations need an update after this edit?"),
    )

    paper = models.ForeignKey(
        Paper, models.CASCADE, verbose_name=_("paper"), related_name="translation_set"
    )
    language_code = models.CharField(
        max_length=7, verbose_name=_("language code"), choices=settings.LANGUAGES
    )
    title = models.CharField(max_length=180, verbose_name=_("title"))
    content = RichTextField(
        config_name="default", verbose_name=_("content"), blank=True
    )

    def __str__(self):
        return self.title

    def content_safe(self):
        """
        Returns the content as safe string
        """
        return mark_safe(self.content)

    def amendment_list(self):
        """
        List of all amendments for this paper in the language of this translation.
        """
        return self.paper.amendment_set.filter(language_code=self.language_code)

    class Meta:
        verbose_name = _("paper translation")
        verbose_name_plural = _("paper translations")


class Amendment(models.Model):
    """
    Represents a proposed change to a paper
    """

    paper = models.ForeignKey(Paper, models.CASCADE, verbose_name=_("paper"))
    language_code = models.CharField(
        max_length=7, verbose_name=_("language code"), choices=settings.LANGUAGES
    )

    start_index = models.IntegerField(verbose_name=_("start index"), default=0)
    end_index = models.IntegerField(verbose_name=_("last index"), default=0)

    content = models.TextField(verbose_name=_("content"))
    author = models.ForeignKey(Author, models.CASCADE, verbose_name=_("author"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))

    state = models.CharField(
        max_length=12, verbose_name=_("state"), choices=AMENDMENT_STATES
    )
    reason = RichTextField(config_name="basic", verbose_name=_("reason"))
    supporters = models.ManyToManyField(settings.AUTH_USER_MODEL)
    tags = models.ManyToManyField(Tag, related_name="tag")

    translations = models.ManyToManyField("self", verbose_name=_("translations"))

    title = models.CharField(max_length=120, blank=True)

    def save(self, *args, **kwargs):  # pylint: disable=W0222
        """
        Save the amendment to the database, also updates the start_index to the index
        of the first change.
        """
        self.start_index = index_of_first_change(self.content)
        self.end_index = index_of_last_change(self.content)
        super().save(*args, **kwargs)

    def translation(self):
        """
        Returns the translation this amendment belongs to
        """
        return self.paper.translation_set.get(language_code=self.language_code)

    def extract_content(self):
        """
        Returns only the part of the paper that is changed through this amendment
        """
        if self.start_index == self.end_index:
            return _(
                "This amendment does not change the content of the paper, "
                "see the reason for more information."
            )

        return utils.extract_content(self.content)

    def add_translation(self, other):
        """
        Adds the given amendment to the translations of this amendment.
        If the amendment already has a translation in this language nothing happens.
        """
        if not self.has_translation_for_language(other.language_code):
            self.translations.add(other)

    def has_translation_for_language(self, language_code):
        """
        Return true if a translation for this language exists.
        """
        return self.language_code == language_code or bool(
            self.translations.filter(language_code=language_code)
        )

    def missing_translations(self):
        """
        Iterator over the language tuples that are missing.
        """
        for translation in self.paper.translation_set.all():
            if not self.has_translation_for_language(translation.language_code):
                yield translation.language_code

    def translation_list(self):
        """
        Iterator over the translations for this amendment
        """
        return self.translations.all()

    def num_supporters(self):
        """
        Number of people that support the amendment
        """
        return self.supporters.all().count()

    def get_absolute_url(self):
        """
        URL of the detail view
        """
        return reverse("amendment-detail", args=(self.pk,))

    @property
    def name(self):
        """
        The name of the author of this
        """
        return self.author.name

    class Meta:
        ordering = ["start_index"]
        verbose_name = _("amendment")
        verbose_name_plural = _("amendments")


class Comment(models.Model):
    """
    A comment to an amendment
    """

    amendment = models.ForeignKey(
        Amendment,
        models.CASCADE,
        verbose_name=_("amendment"),
        related_name="comments",
        null=True,
    )
    author = models.ForeignKey(
        Author, models.CASCADE, verbose_name=_("author"), blank=True, null=True
    )
    body = models.TextField(verbose_name=_("body"))
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("likes"))

    @property
    def name(self):
        """
        The name of the author of this comment
        """
        return self.author.name

    def __str__(self):
        return "Comment {} by {}".format(self.body, self.name)

    def num_likes(self):
        """
        Number of likes for this comment
        """
        return self.likes.all().count()

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")


class PaperComment(models.Model):
    """
    A comment to an amendment
    """

    paper = models.ForeignKey(
        Paper,
        models.CASCADE,
        verbose_name=_("paper"),
        related_name="comments",
        null=True,
    )
    author = models.ForeignKey(
        Author, models.CASCADE, verbose_name=_("author"), blank=True, null=True
    )
    body = models.TextField(verbose_name=_("body"))
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("likes"))

    @property
    def name(self):
        """
        The name of the author of this comment
        """
        return self.author.name

    def __str__(self):
        return "Comment {} by {}".format(self.body, self.name)

    def num_likes(self):
        """
        Number of likes for this comment
        """
        return self.likes.all().count()

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")


REJECT = "reject"
ACCEPT = "accept"
MODIFIED = "modified"

RECOMMENDATIONS = (
    (REJECT, _("reject")),
    (ACCEPT, _("accept")),
    (MODIFIED, _("modified")),
)


class Recommendation(models.Model):
    """
    A recommendation for an amendent, either: accept, reject or a modification
    """

    amendment = models.OneToOneField(
        Amendment, models.CASCADE, verbose_name=_("amendment")
    )

    recommendation = models.CharField(max_length=80, choices=RECOMMENDATIONS)
    reason = RichTextField(blank=True)
    alternative = models.ForeignKey(
        Amendment,
        models.SET_NULL,
        verbose_name=_("alternative"),
        null=True,
        blank=True,
        related_name="recommended_by",
    )

    def save(self, *args, **kwargs):
        if not kwargs.get("update_translations"):
            for translation in self.amendment.translations.all():
                rec, created = Recommendation.objects.update_or_create(
                    amendment=translation,
                    defaults={
                        "recommendation": self.recommendation,
                    },
                )

        return super().save(*args, **kwargs)
