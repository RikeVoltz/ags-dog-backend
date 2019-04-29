# Generated by Django 2.2 on 2019-04-10 16:38

import ags_site.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ags_site', '0002_walkingdate_month'),
    ]

    operations = [
        migrations.AddField(
            model_name='walker',
            name='can_change_dates',
            field=models.BooleanField(default=True, verbose_name='Может изменить даты выгула'),
        ),
        migrations.AlterField(
            model_name='walker',
            name='photo',
            field=models.ImageField(upload_to=ags_site.models.user_directory_path, verbose_name='Аватар'),
        ),
        migrations.AlterField(
            model_name='walkingdate',
            name='dog_owner_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='walkingdate',
            name='street',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
