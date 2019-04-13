from django.shortcuts import render, redirect

from ags_site.forms import ProfileForm
from ags_site.models import Walker


def training(request):
    return render(request, 'training.html')


def walking(request):
    return render(request, 'walking.html')


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


def profile(request):
    if request.user.is_authenticated:
        try:
            walker = request.user.walker
            print(walker.can_change_dates)
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
