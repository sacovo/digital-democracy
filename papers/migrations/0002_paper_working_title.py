# Generated by Django 3.1.1 on 2020-10-05 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("papers", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="paper",
            name="working_title",
            field=models.CharField(default="draft", max_length=255),
            preserve_default=False,
        )
    ]
