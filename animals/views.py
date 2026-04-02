import os
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.utils.text import get_valid_filename

from .models import Animal
from .forms import AnimalForm
from core.utils import get_ad, get_fd, get_hd, get_docs, get_setting, get_at, get_ft, get_tr, get_weight_chart, allowed_file


def animal_detail(request, id):
    printing = request.GET.get('print', '0')
    limit = 10 if printing == '1' else 5

    animal_data = get_ad(id)
    feeding_data = get_fd(None, id, limit)
    history_data = get_hd(None, id, limit)
    documents = get_docs('animal', id)

    if printing == '1':
        return render(request, 'animal/animal_print.html', {
            'animal': animal_data,
            'feedings': feeding_data,
            'history': history_data,
            'location': 'animal',
        })
    return render(request, 'animal/animal.html', {
        'animal': animal_data,
        'feedings': feeding_data,
        'history': history_data,
        'location': 'animal',
        'settings': get_setting(),
        'documents': documents,
    })


def get_weight(request, id):
    weight_list = get_weight_chart(id) or []
    unit = weight_list[0]['weight_unit'] if weight_list else 'g'
    return render(request, 'animal/weight_chart.html', {
        'weight_list': weight_list,
        'weight_unit': unit,
    })


@login_required
def add(request):
    UPLOAD_FOLDER = settings.MEDIA_ROOT

    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES.get('image')
            if image_file and image_file.name:
                if allowed_file(image_file.name):
                    filename = get_valid_filename(image_file.name)
                    with open(os.path.join(UPLOAD_FOLDER, 'animals', filename), 'wb+') as dest:
                        for chunk in image_file.chunks():
                            dest.write(chunk)
                else:
                    messages.error(request, 'Invalid file. Please upload an image file.')
                    return redirect('animals:add')
            else:
                filename = 'dummy.jpg'

            animal = form.save(commit=False)
            animal.image = filename
            animal.save()

            messages.success(request, 'Data submitted successfully!')
            return redirect('/')
    else:
        form = AnimalForm()

    return render(request, 'animal/animal_add.html', {
        'form': form,
        'location': 'animal_add',
        'target': '/animal/add/',
        'animal_types': get_at(),
        'feeding_types': get_ft(),
        'terrariums': get_tr(),
    })


@login_required
def edit(request, id):
    UPLOAD_FOLDER = settings.MEDIA_ROOT
    animal = get_object_or_404(Animal, pk=id)

    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES, instance=animal)
        if form.is_valid():
            image_file = request.FILES.get('image')
            if image_file and image_file.name:
                if allowed_file(image_file.name):
                    filename = get_valid_filename(image_file.name)
                    with open(os.path.join(UPLOAD_FOLDER, 'animals', filename), 'wb+') as dest:
                        for chunk in image_file.chunks():
                            dest.write(chunk)
                    # Delete old image
                    if animal.image and animal.image != 'dummy.jpg':
                        old_path = os.path.join(UPLOAD_FOLDER, 'animals', animal.image)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                else:
                    messages.error(request, 'Invalid file format.')
                    return redirect('animals:edit', id=id)
            else:
                filename = animal.image

            updated = form.save(commit=False)
            updated.image = filename
            updated.updated_date = datetime.date.today()
            updated.save()

            messages.success(request, 'Data submitted successfully!')
            return redirect('animals:detail', id=id)
    else:
        form = AnimalForm(instance=animal)

    return render(request, 'animal/animal_edit.html', {
        'form': form,
        'animal': animal,
        'target': f'/animal/edit/{id}/',
        'animal_types': get_at(),
        'feeding_types': get_ft(),
        'terrariums': get_tr(),
    })


@login_required
def delete(request, id):
    if request.method == 'POST':
        UPLOAD_FOLDER = settings.MEDIA_ROOT
        animal = get_object_or_404(Animal, pk=id)

        if animal.image and animal.image != 'dummy.jpg':
            img_path = os.path.join(UPLOAD_FOLDER, 'animals', animal.image)
            if os.path.exists(img_path):
                os.remove(img_path)

        animal.delete()
        messages.success(request, 'Animal deleted successfully!')
        return HttpResponse(status=200)
