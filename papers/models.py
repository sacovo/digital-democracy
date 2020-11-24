"""
Database models for app papers
"""
from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext as _

from papers import utils

# Create your models here.

STATES = (("draft", _("Draft")), ("public", _("Published")), ("final", _("Finalized")))


class Author(models.Model):
    """
    Represents an author of a paper or an amendment, used as a proxy to auth.User
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, models.CASCADE, blank=True, null=True
    )

    @property
    def name(self):
        """
        The name of the user
        """
        return str(self.user)


class Paper(models.Model):
    """
    Collects the information about a paper.
    """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    edited_at = models.DateTimeField(auto_now=True, verbose_name=_("edited at"))
    amendmend_deadline = models.DateTimeField(verbose_name=_("deadline"))

    working_title = models.CharField(max_length=255)

    state = models.CharField(choices=STATES, max_length=20, verbose_name=_("state"))

    authors = models.ManyToManyField(Author, blank=True)

    def __str__(self):
        return self.working_title

    def missing_translations(self):
        """
        Iterator over all language tuples where there is no translation for this paper
        """
        for language in settings.LANGUAGES:
            if not bool(self.translation_set.filter(language_code=language[0])):
                yield language


class PaperTranslation(models.Model):
    """
    The content of a paper in a specific language.
    """

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

    def amendmend_list(self):
        """
        List of all amendments for this paper in the language of this translation.
        """
        return self.paper.amendmend_set.filter(language_code=self.language_code)


class Amendmend(models.Model):
    """
    Represents a proposed change to a paper
    """

    paper = models.ForeignKey(Paper, models.CASCADE, verbose_name=_("paper"))
    language_code = models.CharField(
        max_length=7, verbose_name=_("language code"), choices=settings.LANGUAGES
    )

    content = models.TextField()
    author = models.ForeignKey(Author, models.CASCADE, verbose_name=_("author"))
    created_at = models.DateTimeField(auto_now_add=True)

    state = models.CharField(max_length=7, verbose_name=_("state"), choices=STATES)
    reason = RichTextField(config_name="basic", verbose_name=_("reason"))

    def translation(self):
        """
        Returns the translation this amendment belongs to
        """
        return self.paper.translation_set.get(language_code=self.language_code)

    def extract_content(self):
        """
        Returns only the part of the paper that is changed through this amendment
        """

        return utils.extract_content(self.content)


class Comment(models.Model):
    """
    A comment to an amendment
    """

    amendment = models.ForeignKey(
        Amendmend,
        models.CASCADE,
        verbose_name=_("amendment"),
        related_name="comments",
        null=True,
    )
    author = models.ForeignKey(
        Author, models.CASCADE, verbose_name=_("author"), blank=True, null=True
    )
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL)

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
