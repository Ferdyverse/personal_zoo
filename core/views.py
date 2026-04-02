from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.utils import get_ad, get_tr, get_setting, insert_defaults


def home(request):
    insert_defaults()

    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    phones = ['android', 'iphone']

    context = {
        'animals': get_ad(),
        'terrariums': get_tr(),
        'settings': get_setting(),
        'location': 'home',
    }

    if any(phone in user_agent for phone in phones):
        return render(request, 'home_mobile.html', context)
    else:
        return render(request, 'home.html', context)


def print_data(request, id=None):
    if id:
        animal_data = get_ad(id)
    else:
        animal_data = get_ad()

    feed_url = request.build_absolute_uri('/feeding/add/')

    return render(request, 'print.html', {
        'animals': animal_data,
        'location': 'print',
        'feed_url': feed_url,
    })
