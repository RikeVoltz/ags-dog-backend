# Generated by Django 2.2 on 2019-04-28 10:02

import ags_site.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ags_site', '0013_auto_20190428_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='walker',
            name='extra_photo_1',
            field=models.ImageField(blank=True, null=True, upload_to=ags_site.models.user_directory_path, verbose_name='Дополнительное фото 1'),
        ),
        migrations.AddField(
            model_name='walker',
            name='extra_photo_2',
            field=models.ImageField(blank=True, null=True, upload_to=ags_site.models.user_directory_path, verbose_name='Дополнительное фото 2'),
        ),
        migrations.AddField(
            model_name='walker',
            name='extra_photo_3',
            field=models.ImageField(blank=True, null=True, upload_to=ags_site.models.user_directory_path, verbose_name='Дополнительное фото 3'),
        ),
    ]
