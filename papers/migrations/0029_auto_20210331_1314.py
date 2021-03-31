# Generated by Django 3.1.1 on 2021-03-31 13:14

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('papers', '0028_auto_20210316_1445'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='amendment',
            options={'ordering': ['start_index'], 'verbose_name': 'amendment', 'verbose_name_plural': 'amendments'},
        ),
        migrations.AlterModelOptions(
            name='author',
            options={'verbose_name': 'author', 'verbose_name_plural': 'authors'},
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'verbose_name': 'comment', 'verbose_name_plural': 'comments'},
        ),
        migrations.AlterModelOptions(
            name='paper',
            options={'verbose_name': 'paper', 'verbose_name_plural': 'papers'},
        ),
        migrations.AlterModelOptions(
            name='papercomment',
            options={'verbose_name': 'comment', 'verbose_name_plural': 'comments'},
        ),
        migrations.AlterModelOptions(
            name='papertranslation',
            options={'verbose_name': 'paper translation', 'verbose_name_plural': 'paper translations'},
        ),
        migrations.AddField(
            model_name='papertranslation',
            name='needs_update',
            field=models.BooleanField(default=False, help_text='Do the other translations need an update after this edit?'),
        ),
        migrations.AlterField(
            model_name='amendment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='papers.author', verbose_name='author'),
        ),
        migrations.AlterField(
            model_name='amendment',
            name='content',
            field=models.TextField(verbose_name='content'),
        ),
        migrations.AlterField(
            model_name='amendment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='amendment',
            name='end_index',
            field=models.IntegerField(default=0, verbose_name='last index'),
        ),
        migrations.AlterField(
            model_name='amendment',
            name='language_code',
            field=models.CharField(choices=[('de', 'German'), ('fr', 'French'), ('it', 'Italian')], max_length=7, verbose_name='language code'),
        ),
        migrations.AlterField(
            model_name='amendment',
            name='paper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='papers.paper', verbose_name='paper'),
        ),
        migrations.AlterField(
            model_name='amendment',
            name='reason',
            field=ckeditor.fields.RichTextField(verbose_name='reason'),
        ),
        migrations.AlterField(
            model_name='amendment',
            name='start_index',
            field=models.IntegerField(default=0, verbose_name='start index'),
        ),
        migrations.AlterField(
            model_name='amendment',
            name='state',
            field=models.CharField(choices=[('draft', '<u title="ⓘ This amendment is a draft.">Draft</u>'), ('public', '<u title="ⓘ This amendment is public.">Published</u>'), ('retracted', '<u title="ⓘ This amendment is retracted.">Retracted</u>'), ('accepted', '<u title="ⓘ This amendment is accepted.">Accepted</u>'), ('rejected', '<u title="ⓘ This amendment is rejected.">Rejected</u>')], max_length=12, verbose_name='state'),
        ),
        migrations.AlterField(
            model_name='amendment',
            name='translations',
            field=models.ManyToManyField(related_name='_amendment_translations_+', to='papers.Amendment', verbose_name='translations'),
        ),
        migrations.AlterField(
            model_name='author',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Benutzer'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='amendment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='papers.amendment', verbose_name='amendment'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='papers.author', verbose_name='author'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='body',
            field=models.TextField(verbose_name='body'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='likes',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='likes'),
        ),
        migrations.AlterField(
            model_name='paper',
            name='amendment_deadline',
            field=models.DateTimeField(verbose_name='deadline'),
        ),
        migrations.AlterField(
            model_name='paper',
            name='authors',
            field=models.ManyToManyField(blank=True, to='papers.Author', verbose_name='authors'),
        ),
        migrations.AlterField(
            model_name='paper',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='paper',
            name='edited_at',
            field=models.DateTimeField(auto_now=True, verbose_name='edited at'),
        ),
        migrations.AlterField(
            model_name='paper',
            name='state',
            field=models.CharField(choices=[('draft', '<u title="ⓘ This paper is a private draft and not ready for amendments.">Draft</u>'), ('public', '<u title="ⓘ This paper is public and ready for amendments.">Published</u>'), ('final', '<u title="ⓘ This paper is final no more changes can be made.">Finalized</u>')], max_length=20, verbose_name='state'),
        ),
        migrations.AlterField(
            model_name='paper',
            name='working_title',
            field=models.CharField(max_length=255, verbose_name='working title'),
        ),
        migrations.AlterField(
            model_name='papercomment',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='papers.author', verbose_name='author'),
        ),
        migrations.AlterField(
            model_name='papercomment',
            name='body',
            field=models.TextField(verbose_name='body'),
        ),
        migrations.AlterField(
            model_name='papercomment',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='papercomment',
            name='likes',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='likes'),
        ),
        migrations.AlterField(
            model_name='papercomment',
            name='paper',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='papers.paper', verbose_name='paper'),
        ),
        migrations.AlterField(
            model_name='papertranslation',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='content'),
        ),
        migrations.AlterField(
            model_name='papertranslation',
            name='language_code',
            field=models.CharField(choices=[('de', 'German'), ('fr', 'French'), ('it', 'Italian')], max_length=7, verbose_name='language code'),
        ),
        migrations.AlterField(
            model_name='papertranslation',
            name='paper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translation_set', to='papers.paper', verbose_name='paper'),
        ),
        migrations.AlterField(
            model_name='papertranslation',
            name='title',
            field=models.CharField(max_length=180, verbose_name='title'),
        ),
    ]
