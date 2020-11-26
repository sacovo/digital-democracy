# Generated by Django 3.1.1 on 2020-11-24 13:32

import ckeditor.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("papers", "0011_auto_20201123_1310"),
    ]

    operations = [
        migrations.AddField(
            model_name="amendmend",
            name="translations",
            field=models.ManyToManyField(
                related_name="_amendmend_translations_+",
                to="papers.Amendmend",
                verbose_name="translations",
            ),
        ),
        migrations.AlterField(
            model_name="amendmend",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="papers.author",
                verbose_name="Autor*in",
            ),
        ),
        migrations.AlterField(
            model_name="amendmend",
            name="content",
            field=models.TextField(verbose_name="Inhalt"),
        ),
        migrations.AlterField(
            model_name="amendmend",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am"),
        ),
        migrations.AlterField(
            model_name="amendmend",
            name="language_code",
            field=models.CharField(
                choices=[("de", "German"), ("fr", "French"), ("it", "Italian")],
                max_length=7,
                verbose_name="Sprachcode",
            ),
        ),
        migrations.AlterField(
            model_name="amendmend",
            name="paper",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="papers.paper",
                verbose_name="Papier",
            ),
        ),
        migrations.AlterField(
            model_name="amendmend",
            name="reason",
            field=ckeditor.fields.RichTextField(verbose_name="Begründung"),
        ),
        migrations.AlterField(
            model_name="amendmend",
            name="state",
            field=models.CharField(
                choices=[
                    ("draft", "Entwurf"),
                    ("public", "Veröffentlicht"),
                    ("final", "Finalisiert"),
                ],
                max_length=7,
                verbose_name="Status",
            ),
        ),
        migrations.AlterField(
            model_name="author",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Benutzer",
            ),
        ),
        migrations.AlterField(
            model_name="comment",
            name="amendment",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to="papers.amendmend",
                verbose_name="Antrag",
            ),
        ),
        migrations.AlterField(
            model_name="comment",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="papers.author",
                verbose_name="Autor*in",
            ),
        ),
        migrations.AlterField(
            model_name="comment",
            name="body",
            field=models.TextField(verbose_name="Inhalt"),
        ),
        migrations.AlterField(
            model_name="comment",
            name="created_on",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am"),
        ),
        migrations.AlterField(
            model_name="comment",
            name="likes",
            field=models.ManyToManyField(
                to=settings.AUTH_USER_MODEL, verbose_name="Likes"
            ),
        ),
        migrations.AlterField(
            model_name="paper",
            name="amendment_deadline",
            field=models.DateTimeField(verbose_name="Antragsfrist"),
        ),
        migrations.AlterField(
            model_name="paper",
            name="authors",
            field=models.ManyToManyField(
                blank=True, to="papers.Author", verbose_name="Autor*innen"
            ),
        ),
        migrations.AlterField(
            model_name="paper",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am"),
        ),
        migrations.AlterField(
            model_name="paper",
            name="edited_at",
            field=models.DateTimeField(auto_now=True, verbose_name="Bearbeitet am"),
        ),
        migrations.AlterField(
            model_name="paper",
            name="state",
            field=models.CharField(
                choices=[
                    ("draft", "Entwurf"),
                    ("public", "Veröffentlicht"),
                    ("final", "Finalisiert"),
                ],
                max_length=20,
                verbose_name="Status",
            ),
        ),
        migrations.AlterField(
            model_name="paper",
            name="working_title",
            field=models.CharField(max_length=255, verbose_name="Working title"),
        ),
        migrations.AlterField(
            model_name="papertranslation",
            name="content",
            field=ckeditor.fields.RichTextField(blank=True, verbose_name="Inhalt"),
        ),
        migrations.AlterField(
            model_name="papertranslation",
            name="language_code",
            field=models.CharField(
                choices=[("de", "German"), ("fr", "French"), ("it", "Italian")],
                max_length=7,
                verbose_name="Sprachcode",
            ),
        ),
        migrations.AlterField(
            model_name="papertranslation",
            name="paper",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="translation_set",
                to="papers.paper",
                verbose_name="Papier",
            ),
        ),
        migrations.AlterField(
            model_name="papertranslation",
            name="title",
            field=models.CharField(max_length=180, verbose_name="Titel"),
        ),
    ]
