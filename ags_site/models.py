import datetime
from io import BytesIO
from os import path
from uuid import uuid4

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db.models import Model, Q, CharField, IntegerField, BooleanField, ForeignKey, CASCADE, OneToOneField, \
    ImageField, DateField, ManyToManyField, FloatField, DO_NOTHING, TextField, DateTimeField
from django.db.models.signals import post_delete
from django.dispatch import receiver
from rikevoltz.settings import MEDIA_ROOT

from .scripts import get_cur_month_days_amount, cut_into_weeks

MAX_INDEX_CAROUSEL_PHOTO_AMOUNT = 20
INDEX_CAROUSEL_PHOTO_NUMBERS = [(idx, str(idx)) for idx in range(1, MAX_INDEX_CAROUSEL_PHOTO_AMOUNT + 1)]


class Sale(Model):
    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'

    full_title = CharField(max_length=100, verbose_name="Полное название акции")
    short_title = CharField(max_length=30, verbose_name="Краткое название акции")
    description = TextField(verbose_name="Описание акции")
    price = IntegerField(verbose_name="Стоимость")

    def __str__(self):
        return self.short_title


class News(Model):
    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    photos = TextField(blank=True, verbose_name='Ссылки на фотографии')
    videos = TextField(blank=True, verbose_name='Ссылки на видео')
    text = TextField(blank=True, verbose_name='Текст новости')
    date = DateTimeField(verbose_name='Дата публикации')

    def __str__(self):
        return self.text[:30] + ('...' if len(self.text) > 30 else '')


class IndexCarouselPhoto(Model):
    class Meta:
        verbose_name = 'Фото в карусели на главной странице'
        verbose_name_plural = 'Фото в карусели на главной странице'

    photo = ImageField(verbose_name='Фотография')
    number = IntegerField(verbose_name='Порядковый номер',
                          choices=INDEX_CAROUSEL_PHOTO_NUMBERS)

    def __str__(self):
        return 'Фото №%d' % self.number

    def save(self, *args, **kwargs):
        all_photos = IndexCarouselPhoto.objects.all()
        if len(all_photos) > 20:
            return
        if self._state.adding:
            for photo in all_photos:
                is_number_taken = (photo.number == self.number)
                if is_number_taken:
                    for cphoto in all_photos:
                        if cphoto.number >= self.number:
                            IndexCarouselPhoto.objects.filter(pk=cphoto.id).update(number=cphoto.number + 1)
                    break
            img = Image.open(self.photo)
            img.thumbnail((10000, 800), Image.ANTIALIAS)
            cropped_img_io = BytesIO()
            img.save(cropped_img_io, format='JPEG', quality=75)
            self.photo.save(uuid4().hex + '.jpg', ContentFile(cropped_img_io.getvalue()), save=False)
        else:
            cur_number = IndexCarouselPhoto.objects.get(pk=self.id).number
            for photo in all_photos:
                is_number_taken = (photo.number == self.number)
                if is_number_taken:
                    if cur_number < self.number:
                        for idx in range(cur_number + 1, self.number + 1):
                            IndexCarouselPhoto.objects.filter(number=idx).update(number=idx - 1)
                    else:
                        for idx in range(cur_number - 1, self.number - 1, -1):
                            IndexCarouselPhoto.objects.filter(number=idx).update(number=idx + 1)
                    break
        super(IndexCarouselPhoto, self).save(*args, **kwargs)


@receiver(post_delete, sender=IndexCarouselPhoto)
def submission_delete(sender, instance, **kwargs):
    instance.photo.delete(False)


class ShopProductCategory(Model):
    class Meta:
        verbose_name = 'Категория товаров'
        verbose_name_plural = 'Категории товаров'

    text_explanation = TextField(blank=True, verbose_name='Текст-пояснение')
    image_explanation = ImageField(blank=True, null=True, verbose_name='Картинка-пояснение')
    title = CharField(max_length=30, verbose_name='Название категории')
    thumbnail = ImageField(blank=True, verbose_name='Обложка категории',
                           default=path.join(MEDIA_ROOT, 'default.png'))
    url_regex = RegexValidator(regex=r'^[a-zA-Z_]+$',
                               message="Имя должно состоять из латинских букв и знаков подчёркивания")
    description = CharField(max_length=200, verbose_name='Описание товара', blank=True)
    url_title = CharField(validators=[url_regex], max_length=30, verbose_name="Имя в адресе страницы")

    def __str__(self):
        return self.title


class ShopProduct(Model):
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    title = CharField(max_length=30, verbose_name='Название товара')
    thumbnail = ImageField(blank=True, verbose_name='Обложка товара',
                           default='default.png')
    description = TextField(blank=True, verbose_name='Описание товара')
    image_1 = ImageField(verbose_name='Первое изображение', blank=True)
    image_2 = ImageField(verbose_name='Второе изображение', blank=True)
    image_3 = ImageField(verbose_name='Третье изображение', blank=True)
    price = FloatField(verbose_name='Цена')
    category = ForeignKey(ShopProductCategory, on_delete=DO_NOTHING, blank=True, null=True,
                          verbose_name='Категория товара')

    def __str__(self):
        return self.title


class WalkingZone(Model):
    class Meta:
        verbose_name = 'Зона выгула(район)'
        verbose_name_plural = 'Зоны выгула(районы)'

    name = CharField(max_length=20, verbose_name='Название района')

    def __str__(self):
        return self.name


def user_directory_path(instance, filename):
    return '{0}/{1}'.format(instance.user.username, filename)


class WalkingDate(Model):
    class Meta:
        verbose_name = 'Выгул'
        verbose_name_plural = 'Выгулы'

    walker = ForeignKey('Walker', on_delete=CASCADE)
    day = IntegerField()
    hour = IntegerField(validators=[MinValueValidator(7), MaxValueValidator(22)])
    month = BooleanField()
    dog_owner_name = CharField(max_length=50, blank=True, verbose_name='Владелец собаки')
    address = CharField(max_length=30, blank=True, verbose_name='Адрес владельца')
    breed = CharField(max_length=30, blank=True, verbose_name='Порода собаки')
    type = CharField(max_length=30, verbose_name='Тип прогулки', choices=(("C", 'Классический'), ("A", 'Активный')))

    def __str__(self):
        return '{walker}: {day:02d}.{month:02d} {hour}'.format(walker=self.walker.user.first_name,
                                                               month=self.month + datetime.datetime.now().month,
                                                               day=self.day + 1,
                                                               hour='{:02d}:00'.format(self.hour))


class Walker(Model):
    class Meta:
        verbose_name = 'Волкер'
        verbose_name_plural = 'Волкеры'

    user = OneToOneField(User, on_delete=CASCADE, verbose_name='Пользователь')
    photo = ImageField(verbose_name='Аватар', upload_to=user_directory_path)
    specialization = CharField(max_length=50, verbose_name='Специализация')
    extra_photo_1 = ImageField(verbose_name='Дополнительное фото 1 на странице специалистов', blank=True, null=True,
                               upload_to=user_directory_path)
    extra_photo_2 = ImageField(verbose_name='Дополнительное фото 2 на странице специалистов', blank=True, null=True,
                               upload_to=user_directory_path)
    extra_photo_3 = ImageField(verbose_name='Дополнительное фото 3 на странице специалистов', blank=True, null=True,
                               upload_to=user_directory_path)
    short_card_photo_1 = ImageField(verbose_name='1 фото на странице выгула', upload_to=user_directory_path)
    short_card_photo_2 = ImageField(verbose_name='2 фото на странице выгула', upload_to=user_directory_path)
    history = TextField(verbose_name='Текст на странице специалистов', blank=True, null=True)
    phrase = CharField(max_length=100, verbose_name="Фраза на странице выгула", blank=True)
    walking_map = ImageField(verbose_name='Карта выгула', upload_to=user_directory_path, blank=True)
    birth_date = DateField(verbose_name='Дата рождения')
    green_zones = ManyToManyField(WalkingZone, related_name='green_zones', verbose_name='Зеленые зоны')
    blue_zones = ManyToManyField(WalkingZone, related_name='blue_zones', verbose_name='Голубые зоны')
    can_change_dates = BooleanField(default=True, verbose_name='Может изменить даты выгула')
    phone_regex = RegexValidator(regex=r'^\+7\d{10}$',
                                 message="Телефонный номер должен быть в формате: '+79999999999'")
    phone = CharField(validators=[phone_regex], max_length=12, blank=True, verbose_name='Телефон')

    def __str__(self):
        return self.user.get_full_name()

    @staticmethod
    def _get_structured_walking_dates(month_days_amount, walking_dates):
        month = [(idx + 1, [{'is_free': True} for _ in range(16)]) for idx in range(month_days_amount)]
        for walking_date in walking_dates:
            if walking_date.dog_owner_name:
                month[walking_date.day][1][walking_date.hour - 7] = {'is_free': False,
                                                                     'address': walking_date.address,
                                                                     'dog_owner_name': walking_date.dog_owner_name,
                                                                     'breed': walking_date.breed,
                                                                     'type': walking_date.get_type_display()}
            else:
                month[walking_date.day][1][walking_date.hour - 7] = {'is_free': False}
        return month

    def get_walking_dates(self):
        cur_month_days_amount = get_cur_month_days_amount()
        next_month_days_amount = get_cur_month_days_amount(is_next_month=True)
        walking_dates = list(self.walkingdate_set.get_queryset())
        cur_month_walking_dates = [date for date in walking_dates if not date.month]
        next_month_walking_dates = [date for date in walking_dates if date.month]
        cur_month = self._get_structured_walking_dates(cur_month_days_amount, cur_month_walking_dates)
        next_month = self._get_structured_walking_dates(next_month_days_amount, next_month_walking_dates)
        cur_month = cut_into_weeks(cur_month)
        next_month = cut_into_weeks(next_month)
        return cur_month, next_month

    def _get_walking_dates_list(self):
        return list(WalkingDate.objects.filter(walker_id=self.id).values('day', 'hour', 'month', 'dog_owner_name',
                                                                         'address', 'breed', 'type'))

    def _fill_walking_dates_from_form_data(self, form_data):
        cur_month_days_amount = get_cur_month_days_amount()
        for walking_date in form_data:
            day, hours = walking_date.split('-')
            day = int(day)
            month = day > cur_month_days_amount - 1
            if month:
                day -= cur_month_days_amount
            for hour in hours.split(','):
                WalkingDate.objects.create(day=day, hour=hour, walker_id=self.id, month=month)

    def set_walking_dates(self, data):
        prev_walking_dates_version = self._get_walking_dates_list()
        WalkingDate.objects.filter(walker_id=self.id).exclude(~Q(dog_owner_name='')).exclude(~Q(address='')).delete()
        if data:
            data = data.split(';')
        self._fill_walking_dates_from_form_data(data)
        cur_walking_dates_version = self._get_walking_dates_list()
        if prev_walking_dates_version != cur_walking_dates_version:
            Walker.objects.filter(id=self.id).update(can_change_dates=False)
