from django.contrib import admin
from papers import models

# Register your models here.


class PaperTranslationInline(admin.StackedInline):
    model = models.PaperTranslation
    fields = [
        "language_code",
        "title",
        "content",
    ]

    extra = 1


@admin.register(models.Paper)
class PaperAdmin(admin.ModelAdmin):
    fields = [
        "amendmend_deadline",
        "state",
        "authors",
    ]

    autocomplete_fields = ["authors"]

    inlines = [PaperTranslationInline]


@admin.register(models.Author)
class AuthorsAdmin(admin.ModelAdmin):
    fields = ["name"]
    search_fields = ["name"]


@admin.register(models.Amendmend)
class AmendmendedAdmin(admin.ModelAdmin):
    fields = ["author", "paper", "state", "content"]
    list_display = ["paper", "state", "author"]
