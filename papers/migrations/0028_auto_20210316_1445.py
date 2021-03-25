# Generated by Django 3.1.1 on 2021-03-16 14:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("papers", "0027_merge_20210309_1611"),
    ]

    operations = [
        migrations.AlterField(
            model_name="amendment",
            name="state",
            field=models.CharField(
                choices=[
                    ("draft", '<u title="ⓘ This amendment is a draft.">Draft</u>'),
                    ("public", '<u title="ⓘ This amendment is public.">Published</u>'),
                    (
                        "retracted",
                        '<u title="ⓘ This amendment is retracted.">Retracted</u>',
                    ),
                    (
                        "approved",
                        '<u title="ⓘ This amendment is a approved.">Approved</u>',
                    ),
                ],
                max_length=12,
                verbose_name="Status",
            ),
        ),
        migrations.AlterField(
            model_name="paper",
            name="state",
            field=models.CharField(
                choices=[
                    (
                        "draft",
                        '<u title="ⓘ This paper is a private draft and not ready for amendments.">Draft</u>',
                    ),
                    (
                        "public",
                        '<u title="ⓘ This paper is public and ready for amendments.">Published</u>',
                    ),
                    (
                        "final",
                        '<u title="ⓘ This paper is final no more changes can be made.">Finalized</u>',
                    ),
                ],
                max_length=20,
                verbose_name="Status",
            ),
        ),
        migrations.CreateModel(
            name="PaperComment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("body", models.TextField(verbose_name="Inhalt")),
                (
                    "created_on",
                    models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am"),
                ),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="papers.author",
                        verbose_name="Autor*in",
                    ),
                ),
                (
                    "likes",
                    models.ManyToManyField(
                        to=settings.AUTH_USER_MODEL, verbose_name="Likes"
                    ),
                ),
                (
                    "paper",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="papers.paper",
                        verbose_name="Papier",
                    ),
                ),
            ],
            options={"verbose_name": "Kommentar", "verbose_name_plural": "Kommentare"},
        ),
    ]
