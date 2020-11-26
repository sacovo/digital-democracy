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
    fields = ["language_code", "title", "content"]

    extra = 1


@admin.register(models.Paper)
class PaperAdmin(admin.ModelAdmin):
    """
    Admin for papers
    """

    fields = ["amendment_deadline", "state", "authors"]

    autocomplete_fields = ["authors"]

    inlines = [PaperTranslationInline]

    search_fields = ["working_title"]


@admin.register(models.Author)
class AuthorsAdmin(admin.ModelAdmin):
    """
    Admin for authors
    """

    fields = ["user"]
    search_fields = ["user__username"]


@admin.register(models.Amendment)
class AmendmentedAdmin(admin.ModelAdmin):
    """
    Admin for amendments
    """

    fields = ["author", "paper", "state", "content", "tags"]
    list_display = ["paper", "state", "author"]
    filter_horizontal = ["tags"]
    ordering = ["tags"]
    list_filter = ["paper", "tags", "language_code"]
    search_fields = ["content"]


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin for comments
    """

    list_display = ["name", "body", "amendment", "created_on"]
    list_filter = ["created_on"]
    search_fields = ["name", "body"]


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin for tag
    """

    list_display = ["name", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name"]
