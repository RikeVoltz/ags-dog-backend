import datetime
from json import dumps

from ags_site.forms import ProfileForm, BookWalkingForm
from ags_site.models import Walker, WalkingZone, WalkingDate, Q, ShopProductCategory, ShopProduct, IndexCarouselPhoto
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render

from .scripts import get_cur_month_days_amount


def training(request):
    return render(request, 'training.html')


def specialists(request):
    walkers = Walker.objects.all()
    return render(request, 'specialists.html', {'walkers': walkers})


def _get_structured_walkers(walkers):
    structured_walkers = {}
    for walker in walkers:
        if walker['walker__id'] not in structured_walkers:
            structured_walkers[walker['walker__id']] = {
                'walker_id': walker['walker__id'],
                'photo': walker['walker__photo'],
                'name': walker['walker__user__first_name'],
                'hours': ['{:02d}:00'.format(walker['hour'])]
            }
        else:
            structured_walkers[walker['walker__id']]['hours'].append('{:02d}:00'.format(walker['hour']))
    return structured_walkers


def _get_walkers(is_blue, month, day, walking_zone_id):
    main_query = Q(month=month, day=day, dog_owner_name='', address='')
    if is_blue:
        sub_query = Q(walker__blue_zones__id=walking_zone_id)
    else:
        sub_query = Q(walker__green_zones__id=walking_zone_id)
    walkers = list(WalkingDate.objects.filter(main_query & sub_query).values('hour', 'walker__photo', 'walker__id',
                                                                             'walker__user__first_name'))
    result_walkers = _get_structured_walkers(walkers)
    return result_walkers


def _get_formatted_days(days, cur_month):
    formatted_days = []
    for day in days:
        formatted_day = '{day:02d}.{month:02d}'.format(day=day['day'] + 1, month=day['month'] + cur_month)
        if formatted_day not in formatted_days:
            formatted_days.append(formatted_day)
    return formatted_days


def _get_days(now, cur_month_days, walking_zone_id):
    main_query = Q(dog_owner_name__gt='', address__gt='')
    two_weeks_day_query = Q(month=False, day__gte=now.day) | Q(month=True, day__lt=14 - (cur_month_days - now.day))
    walking_zones_query = Q(walker__green_zones__id=walking_zone_id) | Q(walker__blue_zones__id=walking_zone_id)
    days = WalkingDate.objects.filter(main_query & two_weeks_day_query & walking_zones_query).values('day', 'month')
    days = sorted(list(days), key=lambda i: (i['month'], i['day']))
    return _get_formatted_days(days, now.month)


def walking(request):
    walkers = Walker.objects.all()
    walking_zones = WalkingZone.objects.values('id', 'name')
    cur_month_days = get_cur_month_days_amount()
    now = datetime.datetime.now()
    if 'walking_zone' in request.POST:
        walking_zone_id = int(request.POST['walking_zone'])
        if 'day_month' in request.POST:
            day, month = request.POST['day_month'].split('.')
            day = int(day) - 1
            month = bool(int(month) - now.month)
            green_walkers = _get_walkers(is_blue=False, month=month, day=day, walking_zone_id=walking_zone_id)
            blue_walkers = _get_walkers(is_blue=True, month=month, day=day, walking_zone_id=walking_zone_id)
            return HttpResponse(dumps([list(green_walkers.values()), list(blue_walkers.values())]))
        else:
            days = _get_days(now, cur_month_days, walking_zone_id)
            return HttpResponse(dumps(days))
    return render(request, 'walking.html', {'walking_zones': walking_zones, 'walkers': walkers})


def test(request):
    if request.GET:
        return render(request, 'test.html', {'type': request.GET['type']})
    else:
        return HttpResponseNotFound()


def shop_category(request, url_title):
    products = ShopProduct.objects.filter(category__url_title=url_title)
    data = ShopProductCategory.objects.filter(url_title=url_title).values('title', 'description')[0]
    return render(request, 'shop_category.html',
                  {'title': data['title'], 'description': data['description'], 'products': products})


def shop(request):
    categories = ShopProductCategory.objects.all()
    return render(request, 'shop.html', {'categories': categories})


def price(request):
    return render(request, 'price.html')


def order(request):
    return render(request, 'order.html')


def interesting(request):
    return render(request, 'interesting.html')


def index(request):
    carousel_photos = IndexCarouselPhoto.objects.all().order_by('number')
    return render(request, 'index.html', {'carousel_photos': carousel_photos})


def discounts(request):
    return render(request, 'discounts.html')


def contacts(request):
    return render(request, 'contacts.html')


def about_us(request):
    return render(request, 'about-us.html')


def consultation(request):
    return render(request, 'consultation.html')


def book_walking(request):
    if request.method == 'POST':
        if BookWalkingForm(request.POST).is_valid():
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


@login_required(login_url='/login')
def profile(request):
    try:
        walker = request.user.walker
    except Walker.DoesNotExist:
        return HttpResponseNotFound()
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            save_walking_dates(request.POST['walking_dates'], walker)
    else:
        form = ProfileForm()
    return render(request, 'profile.html', {'walker': walker, 'form': form})


def save_walking_dates(walking_dates, walker):
    if walker.can_change_dates:
        walker.set_walking_dates(walking_dates.rstrip(';'))
