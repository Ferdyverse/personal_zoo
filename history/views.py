from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse

from .models import History
from .forms import HistoryForm, HistoryMultiForm
from animals.models import Animal
from core.utils import get_hd, get_ht, get_tr


def get_all(request, id):
    less = request.GET.get('less')
    history = get_hd(None, id, 5 if less else None)
    return render(request, 'history/history_all.html', {'history': history})


@login_required
def add(request, id):
    ht_choices = [(ht.id, ht.name) for ht in get_ht()]

    if request.method == 'POST':
        form = HistoryForm(request.POST)
        form.fields['event'].choices = ht_choices
        if form.is_valid():
            History.objects.create(
                animal_id=id,
                event_id=form.cleaned_data['event'],
                text=form.cleaned_data['text'],
                date=form.cleaned_data['date'],
            )
            messages.success(request, 'Added event/action successfully!')
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse(form.errors)

    form = HistoryForm()
    form.fields['event'].choices = ht_choices
    return render(request, 'history/history_add.html', {
        'id': id,
        'form': form,
        'target': f'/history/add/{id}/',
    })


@login_required
def multi_add(request):
    ht_choices = [(ht.id, ht.name) for ht in get_ht()]
    animal_choices = [(a.id, a.name) for a in Animal.objects.all()]
    terrarium_choices = [(t['id'], t['name']) for t in get_tr()]
    terrarium = request.GET.get('terrarium')

    if request.method == 'POST':
        form = HistoryMultiForm(request.POST)
        form.fields['event'].choices = ht_choices
        form.fields['animals'].choices = animal_choices
        form.fields['terrariums'].choices = terrarium_choices

        if form.is_valid():
            selected_animals = list(form.cleaned_data['animals'])
            for t_id in form.cleaned_data['terrariums']:
                for a in Animal.objects.filter(terrarium_id=t_id):
                    if str(a.id) not in selected_animals:
                        selected_animals.append(str(a.id))

            for animal_id in selected_animals:
                History.objects.create(
                    animal_id=animal_id,
                    event_id=form.cleaned_data['event'],
                    text=form.cleaned_data['text'],
                    date=form.cleaned_data['date'],
                )

            messages.success(request, 'Added event/action successfully!')
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse(form.errors)

    form = HistoryMultiForm()
    form.fields['event'].choices = ht_choices
    form.fields['animals'].choices = animal_choices
    form.fields['terrariums'].choices = terrarium_choices

    return render(request, 'history/history_multi_add.html', {
        'form': form,
        'terrarium': terrarium,
        'location': 'multi_event',
        'target': '/history/multi_add/',
    })


@login_required
def edit(request, id):
    event = get_object_or_404(History, pk=id)
    ht_choices = [(ht.id, ht.name) for ht in get_ht()]

    if request.method == 'POST':
        form = HistoryForm(request.POST)
        form.fields['event'].choices = ht_choices
        if form.is_valid():
            event.event_id = form.cleaned_data['event']
            event.text = form.cleaned_data['text']
            event.date = form.cleaned_data['date']
            event.save()
            messages.success(request, 'Changes to history saved!')
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse(form.errors)

    form = HistoryForm(initial={
        'event': event.event_id,
        'text': event.text,
        'date': event.date,
    })
    form.fields['event'].choices = ht_choices

    return JsonResponse({
        'htmlresponse': render(request, 'history/history_edit.html', {
            'form': form,
            'id': id,
            'target': f'/history/edit/{id}/',
        }).content.decode()
    })


@login_required
def delete(request, id):
    if request.method == 'POST':
        event = get_object_or_404(History, pk=id)
        event.delete()
        messages.success(request, 'Deleted history successfully!')
        return HttpResponse(status=200)
