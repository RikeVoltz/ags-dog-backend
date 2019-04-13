import calendar
import datetime

from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db.models import Model, Q, CharField, IntegerField, BooleanField, ForeignKey, CASCADE, OneToOneField, \
    ImageField, DateField, ManyToManyField


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
    dog_owner_name = CharField(max_length=50, blank=True)
    street = CharField(max_length=30, blank=True)


class Walker(Model):
    user = OneToOneField(User, on_delete=CASCADE, verbose_name='Пользователь')
    photo = ImageField(verbose_name='Аватар', upload_to=user_directory_path)
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
        walking_dates = list(self.walkingdate_set.values())
        tmp_cur_month = [(idx + 1, [{'is_free': True} for _ in range(16)]) for idx in range(cur_month_days)]
        tmp_next_month = [(idx + 1, [{'is_free': True} for _ in range(16)]) for idx in range(next_month_days)]
        for walking_date in walking_dates:
            if not walking_date['month']:
                if walking_date['dog_owner_name']:
                    tmp_cur_month[walking_date['day']][1][walking_date['hour'] - 7] = {'is_free': False,
                                                                                       'street': walking_date['street'],
                                                                                       'dog_owner_name': walking_date[
                                                                                           'dog_owner_name']}
                else:
                    tmp_cur_month[walking_date['day']][1][walking_date['hour'] - 7] = {'is_free': False}
            else:
                if walking_date['dog_owner_name']:
                    tmp_next_month[walking_date['day']][1][walking_date['hour'] - 7] = {'is_free': False,
                                                                                        'street': walking_date[
                                                                                            'street'],
                                                                                        'dog_owner_name': walking_date[
                                                                                            'dog_owner_name']}
                else:
                    tmp_next_month[walking_date['day']][1][walking_date['hour'] - 7] = {'is_free': False}
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
        WalkingDate.objects.all().exclude(~Q(dog_owner_name='')).exclude(~Q(street='')).delete()
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
        self.can_change_dates = False
