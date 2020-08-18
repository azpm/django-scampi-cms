# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-08-18 11:55
from __future__ import unicode_literals

from django.db import migrations, models
import libscampi.contrib.cms.newsengine.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('-creation_date',),
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
            },
        ),
        migrations.CreateModel(
            name='ArticleTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('headline', models.CharField(help_text='Article Title. No markup allowed.', max_length=255, verbose_name='Article Headline')),
                ('sub_headline', models.CharField(help_text='Will be truncated to 30 words when viewed as a spotlight. No markup allowed.', max_length=255, verbose_name='Article Tag line')),
                ('synopsis', models.TextField(blank=True, help_text="Usually left blank. Article Synopsis, markup(down) allowed: see <a href='http://daringfireball.net/projects/markdown/syntax' target='_blank'>Markdown Syntax</a> for help")),
                ('body', models.TextField(blank=True, help_text="Article body, markup(down) allowed: see <a href='http://daringfireball.net/projects/markdown/syntax' target='_blank'>Markdown Syntax</a> for help", validators=[libscampi.contrib.cms.newsengine.validators.validate_article])),
            ],
            options={
                'verbose_name': 'Article Translation',
                'verbose_name_plural': 'Article Translations',
            },
        ),
        migrations.CreateModel(
            name='Publish',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField(db_index=True, null=True)),
                ('end', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('published', models.BooleanField(db_index=True, default=False)),
                ('slug', models.SlugField(max_length=255, null=True, unique_for_date=models.DateTimeField(db_index=True, null=True))),
                ('sticky', models.BooleanField(db_index=True, default=False)),
                ('order_me', models.PositiveSmallIntegerField(db_index=True, default=0)),
                ('seen', models.BooleanField(db_index=True, default=False)),
            ],
            options={
                'ordering': ('-sticky', 'order_me', '-start'),
                'verbose_name': 'Published Story',
                'verbose_name_plural': 'Published Stories',
            },
        ),
        migrations.CreateModel(
            name='PublishCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyname', models.SlugField(max_length=100)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Publishing Word',
                'verbose_name_plural': 'Publishing Words',
            },
        ),
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alternate_byline', models.CharField(blank=True, help_text=b'You can specify a different byline than the one automatically created from choosing an author', max_length=250, null=True, verbose_name=b'Alternate Byline')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Creation Date')),
                ('modified', models.DateTimeField(auto_now=True)),
                ('important', models.BooleanField(default=False)),
                ('slug', models.SlugField(editable=False, max_length=250, null=True, unique=True)),
            ],
            options={
                'ordering': ('-creation_date',),
                'verbose_name': 'Story',
                'verbose_name_plural': 'Stories',
            },
        ),
        migrations.CreateModel(
            name='StoryCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('keyname', models.SlugField(max_length=100)),
                ('seen', models.PositiveIntegerField(default=0, editable=False)),
                ('shared', models.PositiveIntegerField(default=0, editable=False)),
                ('browsable', models.BooleanField(db_index=True, default=True, help_text='Visible in category filters list on archive pages.')),
                ('excluded', models.BooleanField(db_index=True, default=False, help_text='Hide from Story Archives.')),
                ('active', models.BooleanField(db_index=True, default=True, help_text='Active in backend.')),
                ('collection', models.BooleanField(db_index=True, default=False, help_text="Is a 'collection' Category", verbose_name='Collection')),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ('keyname',),
                'verbose_name': 'Story Category',
                'verbose_name_plural': 'Story Categories',
            },
        ),
    ]
