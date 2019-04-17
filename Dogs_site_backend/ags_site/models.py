import calendar
import datetime

from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db.models import Model, Q, CharField, IntegerField, BooleanField, ForeignKey, CASCADE, OneToOneField, \
    ImageField, DateField, ManyToManyField


class ShopProduct(Model):
    title = CharField(max_length=30, verbose_name='Название товара')
    thumbnail = ImageField(max_length=30, verbose_name='Название товара')
    Video = CharField(max_length=30, verbose_name='Название товара')


class WalkingZone(Model):
    name = CharField(max_length=20, verbose_name='Название района')

    def __str__(self):
        return self.name


def user_directory_path(instance, filename):
    return '{0}/{1}'.format(instance.user.username, filename)


class WalkingDate(Model):
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
    user = OneToOneField(User, on_delete=CASCADE, verbose_name='Пользователь')
    photo = ImageField(verbose_name='Аватар', upload_to=user_directory_path)
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

    def get_walking_dates(self):
        now = datetime.datetime.now()
        cur_month_days = calendar.monthrange(now.year, now.month)[1]
        next_month_days = calendar.monthrange(*calendar.nextmonth(now.year, now.month))[1]
        walking_dates = list(self.walkingdate_set.get_queryset())
        tmp_cur_month = [(idx + 1, [{'is_free': True} for _ in range(16)]) for idx in range(cur_month_days)]
        tmp_next_month = [(idx + 1, [{'is_free': True} for _ in range(16)]) for idx in range(next_month_days)]
        for walking_date in walking_dates:
            if not walking_date.month:
                if walking_date.dog_owner_name:
                    tmp_cur_month[walking_date.day][1][walking_date.hour - 7] = {'is_free': False,
                                                                                 'address': walking_date.address,
                                                                                 'dog_owner_name': walking_date.dog_owner_name,
                                                                                 'breed': walking_date.breed,
                                                                                 'type': walking_date.get_type_display()}
                else:
                    tmp_cur_month[walking_date.day][1][walking_date.hour - 7] = {'is_free': False}
            else:
                if walking_date.dog_owner_name:
                    tmp_next_month[walking_date.day][1][walking_date.hour - 7] = {'is_free': False,
                                                                                        'address': walking_date.address,
                                                                                        'dog_owner_name': walking_date.dog_owner_name,
                                                                                        'breed': walking_date.breed,
                                                                                        'type': walking_date.get_type_display()}
                else:
                    tmp_next_month[walking_date.day][1][walking_date.hour - 7] = {'is_free': False}
        tmp_cur_month_weeks = []
        tmp_next_month_weeks = []
        while len(tmp_cur_month) > 7:
            tmp_cur_month_weeks.append(tmp_cur_month[:7])
            tmp_cur_month = tmp_cur_month[7:]
        while len(tmp_next_month) > 7:
            tmp_next_month_weeks.append(tmp_next_month[:7])
            tmp_next_month = tmp_next_month[7:]
        if tmp_cur_month:
            tmp_cur_month_weeks.append(tmp_cur_month)
        if tmp_next_month:
            tmp_next_month_weeks.append(tmp_next_month)

        return tmp_cur_month_weeks, tmp_next_month_weeks

    def set_walking_dates(self, serialized):
        prev = list(
            WalkingDate.objects.filter(walker_id=self.id).values('day', 'hour', 'month', 'dog_owner_name', 'address',
                                                                 'breed', 'type'))
        WalkingDate.objects.filter(walker_id=self.id).exclude(~Q(dog_owner_name='')).exclude(~Q(address='')).delete()
        if serialized:
            serialized = serialized.split(';')
        now = datetime.datetime.now()
        cur_month_days = calendar.monthrange(now.year, now.month)[1]
        for walking_date in serialized:
            day, hours = walking_date.split('-')
            day = int(day)
            if day > cur_month_days - 1:
                day -= cur_month_days
                month = True
            else:
                month = False
            hours = hours.split(',')
            for hour in hours:
                WalkingDate.objects.create(day=day, hour=hour, walker_id=self.id, month=month)
        cur = list(
            WalkingDate.objects.filter(walker_id=self.id).values('day', 'hour', 'month', 'dog_owner_name', 'address',
                                                                 'breed', 'type'))
        if prev != cur:
            Walker.objects.filter(id=self.id).update(can_change_dates=False)
