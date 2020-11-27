# Generated by Django 3.1.1 on 2020-11-25 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("papers", "0014_widget")]

    operations = [
        migrations.CreateModel(
            name="Tag",
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
                ("word", models.CharField(max_length=35)),
                ("created_at", models.DateTimeField()),
            ],
        ),
        migrations.DeleteModel(name="Widget"),
        migrations.AddField(
            model_name="amendmend",
            name="tags",
            field=models.ManyToManyField(related_name="photos", to="papers.Tag"),
        ),
    ]
