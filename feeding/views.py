import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse

from .models import Feeding, FeedingType
from .forms import FeedingForm, FeedingMultiForm
from animals.models import Animal
from core.utils import get_fd, get_ft, get_tr


def get_units(request, id):
    unit_data = get_object_or_404(FeedingType, pk=id)
    value = request.GET.get('value', '')
    return render(request, 'feeding/feeding_unit.html', {
        'unit_data': unit_data,
        'value': value,
    })


def get_all(request, id):
    less = request.GET.get('less')
    feedings = get_fd(None, id, 5 if less else None)
    return render(request, 'feeding/feeding_all.html', {'feedings': feedings})


def qr_code(request, id):
    animal = get_object_or_404(Animal, pk=id)
    feed_url = request.build_absolute_uri(f'/feeding/add/{id}/?external')
    return render(request, 'feeding/feeding_qr.html', {
        'id': id,
        'animal': animal.name,
        'feed_url': feed_url,
    })


@login_required
def add(request, id):
    ft_choices = [(ft.id, ft.name) for ft in get_ft()]

    if request.method == 'POST':
        form = FeedingForm(request.POST)
        form.fields['type'].choices = ft_choices
        if form.is_valid():
            Feeding.objects.create(
                animal_id=id,
                feeding_type_id=form.cleaned_data['type'],
                count=form.cleaned_data['count'],
                unit=form.cleaned_data['unit'],
                date=form.cleaned_data['date'],
            )
            messages.success(request, 'Added feeding successfully!')
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse(form.errors)

    form = FeedingForm()
    form.fields['type'].choices = ft_choices

    animal = get_object_or_404(Animal, pk=id)
    external = request.GET.get('external')
    template = 'feeding/feeding_add_external.html' if external is not None else 'feeding/feeding_add.html'
    return render(request, template, {
        'id': id,
        'form': form,
        'animal': animal.name,
        'dft': animal.default_ft_id,
        'target': f'/feeding/add/{id}/',
    })


@login_required
def multi_add(request):
    ft_choices = [(ft.id, ft.name) for ft in get_ft()]
    animal_choices = [(a.id, a.name) for a in Animal.objects.all()]
    terrarium_choices = [(t['id'], t['name']) for t in get_tr()]
    terrarium = request.GET.get('terrarium')

    if request.method == 'POST':
        form = FeedingMultiForm(request.POST)
        form.fields['type'].choices = ft_choices
        form.fields['animals'].choices = animal_choices
        form.fields['terrariums'].choices = terrarium_choices

        if form.is_valid():
            selected_animals = list(form.cleaned_data['animals'])
            selected_terrariums = form.cleaned_data['terrariums']

            for t_id in selected_terrariums:
                for a in Animal.objects.filter(terrarium_id=t_id):
                    if str(a.id) not in selected_animals:
                        selected_animals.append(str(a.id))

            for animal_id in selected_animals:
                Feeding.objects.create(
                    animal_id=animal_id,
                    feeding_type_id=form.cleaned_data['type'],
                    count=form.cleaned_data['count'],
                    unit=form.cleaned_data['unit'],
                    date=form.cleaned_data['date'],
                )

            messages.success(request, 'Added multi feeding successfully!')
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse(form.errors)

    form = FeedingMultiForm()
    form.fields['type'].choices = ft_choices
    form.fields['animals'].choices = animal_choices
    form.fields['terrariums'].choices = terrarium_choices

    return render(request, 'feeding/feeding_multi_add.html', {
        'form': form,
        'terrarium': terrarium,
        'location': 'multi_feeding',
        'target': '/feeding/multi_add/',
    })


@login_required
def edit(request, id):
    feeding = get_object_or_404(Feeding, pk=id)
    ft_choices = [(ft.id, ft.name) for ft in get_ft()]

    if request.method == 'POST':
        form = FeedingForm(request.POST)
        form.fields['type'].choices = ft_choices
        if form.is_valid():
            feeding.feeding_type_id = form.cleaned_data['type']
            feeding.count = form.cleaned_data['count']
            feeding.unit = form.cleaned_data['unit']
            feeding.date = form.cleaned_data['date']
            feeding.save()
            messages.success(request, 'Changes to feeding saved!')
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse(form.errors)

    form = FeedingForm(initial={
        'type': feeding.feeding_type_id,
        'count': feeding.count,
        'unit': feeding.unit,
        'date': feeding.date,
    })
    form.fields['type'].choices = ft_choices

    return JsonResponse({
        'htmlresponse': render(request, 'feeding/feeding_edit.html', {
            'form': form,
            'id': id,
            'target': f'/feeding/edit/{id}/',
        }).content.decode()
    })


@login_required
def delete(request, id):
    if request.method == 'POST':
        feeding = get_object_or_404(Feeding, pk=id)
        feeding.delete()
        messages.success(request, 'Deleted feeding successfully!')
        return HttpResponse(status=200)
