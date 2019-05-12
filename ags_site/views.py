import json
from datetime import datetime

from ags_site.forms import ProfileForm, BookWalkingForm, FeedbackForm
from ags_site.models import Walker, WalkingZone, WalkingDate, Q, ShopProductCategory, ShopProduct, IndexCarouselPhoto, \
    News, Sale
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound, \
    HttpResponseServerError
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
from rikevoltz.settings import AGS_GROUP_ID, AGS_GROUP_CONFIRMATION_ANSWER, AGS_GROUP_SECRET_KEY
from rikevoltz.settings import STATIC_URL

from .scripts import get_cur_month_days_amount, send_message_to_email


def robots(request):
    return render_to_response('robots.txt', content_type="text/plain")


def sitemap(request):
    return render_to_response('sitemap.xml', content_type="text/xml")


def add_feedback_form(view):
    def wrapper(request, url_title=None, *args, **kwargs):
        if request.method == 'POST':
            form = FeedbackForm(request.POST)
            if form.is_valid():
                send_message_to_email(request.POST)
        else:
            form = FeedbackForm()
        return view(request, url_title, form=form)

    return wrapper


@csrf_exempt
def vk_callbacks(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest()
    if 'secret' not in data or data['secret'] != AGS_GROUP_SECRET_KEY:
        return HttpResponseBadRequest()
    if 'type' in data:
        if data['type'] == 'confirmation':
            if 'group_id' in data and data['group_id'] == AGS_GROUP_ID:
                return HttpResponse(AGS_GROUP_CONFIRMATION_ANSWER)
        elif data['type'] == 'wall_post_new':
            try:
                if 'object' in data and 'post_type' in data['object'] and data['object']['post_type'] == 'post':
                    text = data['object']['text']
                    videos = [attachment['video'] for attachment in data['object']['attachments'] if
                              attachment['type'] == 'video']
                    photos = [attachment['photo'] for attachment in data['object']['attachments'] if
                              attachment['type'] == 'photo']
                    video_links = []
                    photo_links = []
                    for video in videos:
                        video_links.append('{image_link}>>https://vk.com/ags178?z=video{owner_id}_{video_id}'.format(
                            image_link=video.get('photo_800') or video.get('photo_640') or video['photo_320'],
                            owner_id=video['owner_id'], video_id=video['id']))
                    for photo in photos:
                        photo_links.append(photo['sizes'][-1]['url'])
                    date = data['object']['date']
                    date = datetime.fromtimestamp(date)
                    News.objects.create(text=text, videos=';'.join(video_links), photos=';'.join(photo_links),
                                        date=date)
            except Exception as e:
                return HttpResponse(str(e))
            else:
                return HttpResponse('ok')
    else:
        return HttpResponseBadRequest()


@add_feedback_form
def training(request, *args, **kwargs):
    return render(request, 'training.html', {'form': kwargs['form']})


@add_feedback_form
def news(request, *args, **kwargs):
    all_news = sorted(News.objects.all(), key=lambda obj: obj.date, reverse=True)
    for new in all_news:
        new.videos = list(filter(None, new.videos.split(';')))
        videos = []
        for video in new.videos:
            lst = video.split('>>')
            if len(lst) == 2:
                videos.append({'video': lst[1], 'image': lst[0]})
            elif len(lst) == 1:
                videos.append({'video': lst[0], 'image': ''})
        new.videos = videos
        new.photos = list(filter(None, new.photos.split(';')))
    page = request.GET.get('page', 1)
    paginator = Paginator(all_news, 2)
    try:
        all_news = paginator.page(page)
    except PageNotAnInteger:
        all_news = paginator.page(1)
    except EmptyPage:
        all_news = paginator.page(paginator.num_pages)
    return render(request, 'news.html', {'news': all_news, 'form': kwargs['form']})


@add_feedback_form
def specialists(request, *args, **kwargs):
    walkers = Walker.objects.all()
    return render(request, 'specialists.html', {'walkers': walkers, 'form': kwargs['form']})


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


@add_feedback_form
def walking(request, *args, **kwargs):
    walkers = Walker.objects.all()
    walking_zones = WalkingZone.objects.values('id', 'name')
    cur_month_days = get_cur_month_days_amount()
    now = datetime.now()
    if 'walking_zone' in request.POST:
        walking_zone_id = int(request.POST['walking_zone'])
        if 'day_month' in request.POST:
            day, month = request.POST['day_month'].split('.')
            day = int(day) - 1
            month = bool(int(month) - now.month)
            green_walkers = _get_walkers(is_blue=False, month=month, day=day, walking_zone_id=walking_zone_id)
            blue_walkers = _get_walkers(is_blue=True, month=month, day=day, walking_zone_id=walking_zone_id)
            return HttpResponse(json.dumps([list(green_walkers.values()), list(blue_walkers.values())]))
        else:
            days = _get_days(now, cur_month_days, walking_zone_id)
            return HttpResponse(json.dumps(days))
    return render(request, 'walking.html', {'walking_zones': walking_zones, 'walkers': walkers, 'form': kwargs['form']})


def test(request):
    if request.GET:
        return render(request, 'test.html', {'type': request.GET['type']})
    else:
        return HttpResponseNotFound()


@add_feedback_form
def shop_category(request, url_title, **kwargs):
    products = ShopProduct.objects.filter(category__url_title=url_title)
    data = ShopProductCategory.objects.filter(url_title=url_title).values('title', 'description', 'text_explanation',
                                                                          'image_explanation')[0]
    return render(request, 'shop_category.html',
                  {'title': data['title'], 'text_explanation': data['text_explanation'],
                   'image_explanation': data['image_explanation'], 'url_title': url_title,
                   'description': data['description'],
                   'products': products, 'form': kwargs['form']})


@add_feedback_form
def shop(request, *args, **kwargs):
    categories = ShopProductCategory.objects.all()
    return render(request, 'shop.html', {'categories': categories, 'form': kwargs['form']})


@add_feedback_form
def price(request, *args, **kwargs):
    sales = Sale.objects.all()
    return render(request, 'price.html', {'form': kwargs['form'], 'sales': sales})


@add_feedback_form
def order(request, *args, **kwargs):
    return render(request, 'order.html', {'form': kwargs['form']})


@add_feedback_form
def interesting(request, *args, **kwargs):
    return render(request, 'interesting.html', {'form': kwargs['form']})


@add_feedback_form
def index(request, *args, **kwargs):
    carousel_photos = IndexCarouselPhoto.objects.all().order_by('number')
    return render(request, 'index.html', {'carousel_photos': carousel_photos, 'form': kwargs['form']})


@add_feedback_form
def discounts(request, *args, **kwargs):
    from django.core.cache import cache
    cache.clear()
    sales = Sale.objects.all()
    return render(request, 'discounts.html', {'form': kwargs['form'], 'sales': sales})


@add_feedback_form
def contacts(request, *args, **kwargs):
    return render(request, 'contacts.html', {'form': kwargs['form']})


@add_feedback_form
def consultation(request, *args, **kwargs):
    return render(request, 'consultation.html', {'form': kwargs['form']})


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
    now = datetime.now()
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
    return render(request, 'profile.html', {'walker': walker, 'profile_form': form})


def save_walking_dates(walking_dates, walker):
    if walker.can_change_dates:
        walker.set_walking_dates(walking_dates.rstrip(';'))
