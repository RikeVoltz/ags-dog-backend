# Generated by Django 2.2 on 2019-04-28 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ags_site', '0014_auto_20190428_1302'),
    ]

    operations = [
        migrations.AddField(
            model_name='walker',
            name='history',
            field=models.TextField(blank=True, null=True, verbose_name='Текст на странице специалистов'),
        ),
    ]
