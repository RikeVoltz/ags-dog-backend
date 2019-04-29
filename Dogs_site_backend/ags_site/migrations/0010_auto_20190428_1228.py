# Generated by Django 2.2 on 2019-04-28 09:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ags_site', '0009_auto_20190428_1223'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopProductCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30, verbose_name='Название товара')),
                ('thumbnail', models.ImageField(blank=True, default='ags_site/media/default.png', max_length=30, upload_to='', verbose_name='Обложка товара')),
            ],
        ),
        migrations.AlterField(
            model_name='shopproduct',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ags_site.ShopProductCategory', verbose_name='Категория товара'),
        ),
        migrations.AlterField(
            model_name='shopproduct',
            name='image_1',
            field=models.ImageField(blank=True, upload_to='', verbose_name='Первое изображение'),
        ),
        migrations.AlterField(
            model_name='shopproduct',
            name='image_2',
            field=models.ImageField(blank=True, upload_to='', verbose_name='Второе изображение'),
        ),
        migrations.AlterField(
            model_name='shopproduct',
            name='image_3',
            field=models.ImageField(blank=True, upload_to='', verbose_name='Третье изображение'),
        ),
        migrations.AlterField(
            model_name='shopproduct',
            name='thumbnail',
            field=models.ImageField(blank=True, default='ags_site/media/default.png', upload_to='', verbose_name='Обложка товара'),
        ),
    ]
