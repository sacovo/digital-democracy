# Generated by Django 3.1.1 on 2020-11-25 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("papers", "0016_amendmend_end_index")]

    operations = [
        migrations.AlterField(
            model_name="amendmend",
            name="end_index",
            field=models.IntegerField(default=0, verbose_name="Endindex"),
        ),
        migrations.AlterField(
            model_name="amendmend",
            name="start_index",
            field=models.IntegerField(default=0, verbose_name="Startindex"),
        ),
        migrations.AlterField(
            model_name="amendmend",
            name="translations",
            field=models.ManyToManyField(
                related_name="_amendmend_translations_+",
                to="papers.Amendmend",
                verbose_name="Übersetzung aktualisieren",
            ),
        ),
    ]