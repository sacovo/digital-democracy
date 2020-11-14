from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext as _

# Create your models here.

STATES = (
    ("draft", _("Draft")),
    ("public", _("Published")),
    ("final", _("Finalized")),
)


class Author(models.Model):
    name = models.CharField(max_length=255)


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
    content = RichTextField(config_name="basic", verbose_name=_("content"))

    def __str__(self):
        return self.title

    def content_safe(self):
        return mark_safe(self.content)


class Amendmend(models.Model):
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
        self.paper.translation_set.get(language_code=self.language_code)


class Comment(models.Model):
    amendment = models.ForeignKey(
        Amendmend,
        models.CASCADE,
        verbose_name=_("amendment"),
        related_name="comments",
        null=True,
    )
    name = models.CharField(max_length=80)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Comment {} by {}".format(self.body, self.name)
