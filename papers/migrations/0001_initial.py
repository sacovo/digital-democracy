# Generated by Django 3.1.1 on 2020-10-05 11:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Author",
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
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Paper",
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
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "edited_at",
                    models.DateTimeField(auto_now=True, verbose_name="edited at"),
                ),
                ("amendmend_deadline", models.DateTimeField(verbose_name="deadline")),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("public", "Published"),
                            ("final", "Finalized"),
                        ],
                        max_length=20,
                        verbose_name="state",
                    ),
                ),
                ("authors", models.ManyToManyField(to="papers.Author")),
            ],
        ),
        migrations.CreateModel(
            name="PaperTranslation",
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
                (
                    "language_code",
                    models.CharField(max_length=2, verbose_name="language code"),
                ),
                ("title", models.CharField(max_length=180, verbose_name="title")),
                ("content", models.TextField(blank=True, verbose_name="content")),
                (
                    "paper",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="papers.paper",
                        verbose_name="paper",
                    ),
                ),
            ],
        ),
    ]
