# Generated by Django 2.2 on 2019-04-09 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ags_site', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='walkingdate',
            name='month',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]