# Generated by Django 2.2 on 2019-04-28 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ags_site', '0017_auto_20190428_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopproduct',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание товара'),
        ),
    ]
