# Generated by Django 2.2 on 2019-04-17 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ags_site', '0004_walker_walking_map'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30, verbose_name='Название товара')),
                ('thumbnail', models.ImageField(max_length=30, upload_to='', verbose_name='Название товара')),
                ('Video', models.CharField(max_length=30, verbose_name='Название товара')),
            ],
        ),
    ]
