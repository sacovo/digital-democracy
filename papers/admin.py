"""
Admin views
"""
from django.contrib import admin

from papers import models

# Register your models here.


class PaperTranslationInline(admin.StackedInline):
    """
    Inline admin for translations
    """

    model = models.PaperTranslation
    fields = [
        "language_code",
        "title",
        "content",
    ]

    extra = 1


@admin.register(models.Paper)
class PaperAdmin(admin.ModelAdmin):
    """
    Admin for papers
    """

    fields = [
        "amendmend_deadline",
        "state",
        "authors",
    ]

    autocomplete_fields = ["authors"]

    inlines = [PaperTranslationInline]


@admin.register(models.Author)
class AuthorsAdmin(admin.ModelAdmin):
    """
    Admin for authors
    """

    fields = ["user"]
    search_fields = ["user__username"]


@admin.register(models.Amendmend)
class AmendmendedAdmin(admin.ModelAdmin):
    """
    Admin for amendments
    """

    fields = ["author", "paper", "state", "content"]
    list_display = ["paper", "state", "author"]


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin for comments
    """

    list_display = ["name", "body", "amendment", "created_on"]
    list_filter = ["created_on"]
    search_fields = ["name", "body"]
