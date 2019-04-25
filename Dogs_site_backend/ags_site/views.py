import calendar
import datetime
from json import dumps

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, redirect

from ags_site.forms import ProfileForm, BookWalkingForm
from ags_site.models import Walker, WalkingZone, WalkingDate, Q


def training(request):
    return render(request, 'training.html')


def walking(request):
    walking_zones = WalkingZone.objects.values('id', 'name')
    now = datetime.datetime.now()
    cur_month_days = calendar.monthrange(now.year, now.month)[1]
    if 'walking_zone' in request.POST and 'day_month' in request.POST:
        day, month = request.POST['day_month'].split('.')
        day = int(day) - 1
        month = bool(int(month) - now.month)
        green_walkers = list(WalkingDate.objects.filter(
            (Q(month=month, day=day) & (Q(walker__green_zones__id=int(request.POST['walking_zone'])))))
                             .exclude(~Q(dog_owner_name='')).exclude(~Q(address='')).values('hour', 'walker__photo',
                                                                                            'walker__id',
                                                                                            'walker__user__first_name'))
        result_green_walkers = {}
        for walker in green_walkers:
            if walker['walker__id'] not in result_green_walkers:
                result_green_walkers[walker['walker__id']] = {
                    'walker_id': walker['walker__id'],
                    'photo': walker['walker__photo'],
                    'name': walker['walker__user__first_name'],
                    'hours': ['{:02d}:00'.format(walker['hour'])]
                }
            else:
                result_green_walkers[walker['walker__id']]['hours'].append('{:02d}:00'.format(walker['hour']))
        blue_walkers = list(WalkingDate.objects.filter(
            (Q(month=month, day=day) & (Q(walker__blue_zones__id=int(request.POST['walking_zone'])))))
                            .exclude(~Q(dog_owner_name='')).exclude(~Q(address='')).values('hour', 'walker__photo',
                                                                                           'walker__id',
                                                                                           'walker__user__first_name'))
        result_blue_walkers = {}
        for walker in blue_walkers:
            if walker['walker__id'] not in result_blue_walkers:
                result_blue_walkers[walker['walker__id']] = {
                    'walker_id': walker['walker__id'],
                    'photo': walker['walker__photo'],
                    'name': walker['walker__user__first_name'],
                    'hours': ['{:02d}:00'.format(walker['hour'])]
                }
            else:
                result_blue_walkers[walker['walker__id']]['hours'].append('{:02d}:00'.format(walker['hour']))

        return HttpResponse(dumps([list(result_green_walkers.values()), list(result_blue_walkers.values())]))
    elif 'walking_zone' in request.POST:
        days = list(WalkingDate.objects.filter(
            (Q(month=False, day__gte=now.day) | Q(month=True, day__lt=14 - (cur_month_days - now.day))) & (
                    Q(walker__green_zones__id=int(request.POST['walking_zone'])) |
                    Q(walker__blue_zones__id=int(request.POST['walking_zone'])))).exclude(~Q(dog_owner_name='')) \
            .exclude(~Q(address='')).values(
            'day', 'month'))
        days = sorted(days, key=lambda i: (i['month'], i['day']))
        result_days = []
        for day in days:
            formatted_day = '{day:02d}.{month:02d}'.format(day=day['day'] + 1, month=day['month'] + now.month)
            if formatted_day not in result_days:
                result_days.append(formatted_day)
        return HttpResponse(dumps(result_days))
    return render(request, 'walking.html', {'walking_zones': walking_zones})


def test(request):
    return render(request, 'test.html')


def shop(request):
    return render(request, 'shop.html')


def price(request):
    return render(request, 'price.html')


def order(request):
    return render(request, 'order.html')


def interesting(request):
    return render(request, 'interesting.html')


def index(request):
    return render(request, 'index.html')


def discounts(request):
    return render(request, 'discounts.html')


def contacts(request):
    return render(request, 'contacts.html')


def about_us(request):
    return render(request, 'about-us.html')


def consultation(request):
    return render(request, 'consultation.html')


def book_walking(request):
    if request.method == 'POST' and request.POST.keys() >= {'name', 'breed', 'type', 'hour', 'address', 'day'}:
        form = BookWalkingForm(request.POST)
        if form.is_valid():
            book_walking_date(request.POST)
            return HttpResponse()
        else:
            return HttpResponseBadRequest()
    else:
        return HttpResponseForbidden()


def book_walking_date(data):
    day, month = data['day'].split('.')
    now = datetime.datetime.now()
    day = int(day) - 1
    month = bool(int(month) - now.month)
    WalkingDate.objects.filter(walker__id=data['walker_id'], day=day, month=month, hour=data['hour']).update(
        breed=data['breed'],
        type=data['type'],
        dog_owner_name=data['name'],
        address=data['address'])


def profile(request):
    if request.user.is_authenticated:
        try:
            walker = request.user.walker
            if request.method == 'POST':
                form = ProfileForm(request.POST)
                if form.is_valid():
                    save_walking_dates(request.POST['walking_dates'], walker)
            else:
                form = ProfileForm()
        except Walker.DoesNotExist:
            walker = None
            form = None
        return render(request, 'profile.html', {'walker': walker, 'form': form})
    else:
        return redirect('/login')


def save_walking_dates(walking_dates, walker):
    if walker.can_change_dates:
        walker.set_walking_dates(walking_dates.rstrip(';'))
