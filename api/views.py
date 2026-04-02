from django.http import JsonResponse
from django.views.decorators.http import require_GET

from core.utils import get_ad, get_fd, get_hd


def main(request):
    return JsonResponse({'status': 'ok', 'version': 'v1'})


@require_GET
def animals(request, id=None):
    if id:
        data = get_ad(id)
    else:
        data = get_ad()
    return JsonResponse(data, safe=False)


@require_GET
def animal_feedings(request, id, argument=None):
    if argument == 'last':
        data = get_fd(None, id, 1)
    else:
        data = get_fd(None, id)
    return JsonResponse(data, safe=False)


@require_GET
def animal_history(request, id, e_type=None):
    if e_type:
        data = get_hd(None, id, 10, e_type)
    else:
        data = get_hd(None, id)
    return JsonResponse(data, safe=False)


def get_feeding_types(request):
    return JsonResponse({'message': 'Not implemented!'}, status=404)
