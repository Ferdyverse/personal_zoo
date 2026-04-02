import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils.text import get_valid_filename

from .models import Terrarium, TerrariumEquipment, TerrariumLamps, TerrariumHistory
from .forms import TerrariumForm, EquipmentForm, LampsForm, EventsForm
from core.utils import get_tr, get_ad, get_te, get_tl, get_thd, get_setting, get_tt, get_htt, allowed_file


def terrarium_detail(request, id):
    terrarium_data = get_tr(id)
    return render(request, 'terrarium/terrarium.html', {
        'location': 'terrarium',
        'settings': get_setting(),
        'animals': get_ad(None, terrarium_data['id']),
        'terrarium': terrarium_data,
        'equipment': get_te(None, terrarium_data['id']),
        'lamps': get_tl(None, terrarium_data['id']),
        'terrarium_history': get_thd(None, terrarium_data['id'], limit=5),
    })


def add(request):
    UPLOAD_FOLDER = settings.MEDIA_ROOT
    tt_choices = [(tt.id, tt.name) for tt in get_tt()]

    if request.method == 'POST':
        form = TerrariumForm(request.POST, request.FILES)
        form.fields['type'].choices = tt_choices
        if form.is_valid():
            image_file = request.FILES.get('image')
            if image_file and image_file.name:
                if allowed_file(image_file.name):
                    filename = get_valid_filename(image_file.name)
                    with open(os.path.join(UPLOAD_FOLDER, 'terrariums', filename), 'wb+') as dest:
                        for chunk in image_file.chunks():
                            dest.write(chunk)
                else:
                    messages.error(request, 'Invalid file. Please upload an image file.')
                    return redirect('terrariums:add')
            else:
                filename = 'dummy.jpg'

            Terrarium.objects.create(
                name=form.cleaned_data['name'],
                size=form.cleaned_data['size'],
                terrarium_type_id=form.cleaned_data['type'],
                notes=form.cleaned_data['notes'],
                image=filename,
            )
            messages.success(request, 'Data submitted successfully!')
            return redirect('/')
    else:
        form = TerrariumForm()
        form.fields['type'].choices = tt_choices

    return render(request, 'terrarium/terrarium_add.html', {
        'form': form,
        'location': 'terrarium_add',
    })


def edit(request, id):
    UPLOAD_FOLDER = settings.MEDIA_ROOT
    terrarium = get_object_or_404(Terrarium, pk=id)
    tt_choices = [(tt.id, tt.name) for tt in get_tt()]

    if request.method == 'POST':
        form = TerrariumForm(request.POST, request.FILES)
        form.fields['type'].choices = tt_choices
        if form.is_valid():
            image_file = request.FILES.get('image')
            if image_file and image_file.name:
                if allowed_file(image_file.name):
                    filename = get_valid_filename(image_file.name)
                    with open(os.path.join(UPLOAD_FOLDER, 'terrariums', filename), 'wb+') as dest:
                        for chunk in image_file.chunks():
                            dest.write(chunk)
                    if terrarium.image and terrarium.image != 'dummy.jpg':
                        old_path = os.path.join(UPLOAD_FOLDER, 'terrariums', terrarium.image)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                else:
                    messages.error(request, 'Invalid file format.')
                    return redirect('terrariums:edit', id=id)
            else:
                filename = terrarium.image

            terrarium.name = form.cleaned_data['name']
            terrarium.terrarium_type_id = form.cleaned_data['type']
            terrarium.size = form.cleaned_data['size']
            terrarium.notes = form.cleaned_data['notes']
            terrarium.image = filename
            terrarium.save()

            messages.success(request, 'Data submitted successfully!')
            return redirect('terrariums:detail', id=id)
    else:
        form = TerrariumForm(initial={
            'name': terrarium.name,
            'size': terrarium.size,
            'type': terrarium.terrarium_type_id,
            'notes': terrarium.notes,
        })
        form.fields['type'].choices = tt_choices

    return render(request, 'terrarium/terrarium_edit.html', {
        'form': form,
        'data': terrarium,
    })


def delete(request, id):
    if request.method == 'POST':
        UPLOAD_FOLDER = settings.MEDIA_ROOT
        terrarium = get_object_or_404(Terrarium, pk=id)

        if terrarium.image and terrarium.image != 'dummy.jpg':
            img_path = os.path.join(UPLOAD_FOLDER, 'terrariums', terrarium.image)
            if os.path.exists(img_path):
                os.remove(img_path)

        terrarium.delete()
        messages.success(request, 'Terrarium deleted successfully!')
        return HttpResponse(status=200)


def equipment_add(request, id):
    terrarium = get_object_or_404(Terrarium, pk=id)
    form = EquipmentForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        TerrariumEquipment.objects.create(
            terrarium_id=id,
            name=form.cleaned_data['name'],
            text=form.cleaned_data['text'],
        )
        messages.success(request, 'Added equipment successfully!')
        return redirect('terrariums:detail', id=id)

    return render(request, 'terrarium/equipment_add.html', {
        'form': form,
        'id': id,
        'data': terrarium,
    })


def equipment_edit(request, id):
    equipment = get_object_or_404(TerrariumEquipment, pk=id)

    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            equipment.name = form.cleaned_data['name']
            equipment.text = form.cleaned_data['text']
            equipment.save()
            messages.success(request, 'Changes to equipment saved!')
            return redirect('terrariums:detail', id=request.POST.get('terrarium_id'))
    else:
        form = EquipmentForm(initial={'name': equipment.name, 'text': equipment.text})

    return JsonResponse({
        'htmlresponse': render(request, 'terrarium/equipment_edit.html', {
            'form': form,
            'data': equipment,
        }).content.decode()
    })


def equipment_delete(request, id):
    if request.method == 'POST':
        equipment = get_object_or_404(TerrariumEquipment, pk=id)
        equipment.delete()
        messages.success(request, 'Deleted equipment successfully!')
        return HttpResponse(status=200)


def lamp_add(request, id):
    terrarium = get_object_or_404(Terrarium, pk=id)
    form = LampsForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        TerrariumLamps.objects.create(
            terrarium_id=id,
            lamp_type=form.cleaned_data['lamp_type'],
            watt=form.cleaned_data['watt'],
            position=form.cleaned_data['position'],
            changed=form.cleaned_data['changed'],
        )
        messages.success(request, 'Added lamp successfully!')
        return redirect('terrariums:detail', id=id)

    return render(request, 'terrarium/lamp_add.html', {
        'form': form,
        'id': id,
        'data': terrarium,
    })


def lamp_edit(request, id):
    lamp = get_object_or_404(TerrariumLamps, pk=id)

    if request.method == 'POST':
        form = LampsForm(request.POST)
        if form.is_valid():
            lamp.lamp_type = form.cleaned_data['lamp_type']
            lamp.watt = form.cleaned_data['watt']
            lamp.position = form.cleaned_data['position']
            lamp.changed = form.cleaned_data['changed']
            lamp.save()
            messages.success(request, 'Changes to lamp saved!')
            return redirect('terrariums:detail', id=lamp.terrarium_id)
    else:
        form = LampsForm(initial={
            'lamp_type': lamp.lamp_type,
            'watt': lamp.watt,
            'position': lamp.position,
            'changed': lamp.changed,
        })

    return JsonResponse({
        'htmlresponse': render(request, 'terrarium/lamp_edit.html', {
            'form': form,
            'data': lamp,
        }).content.decode()
    })


def lamp_delete(request, id):
    if request.method == 'POST':
        lamp = get_object_or_404(TerrariumLamps, pk=id)
        lamp.delete()
        messages.success(request, 'Deleted lamp successfully!')
        return HttpResponse(status=200)


def terrarium_history_get_all(request, id):
    less = request.GET.get('less')
    terrarium_history = get_thd(None, id, 5 if less else None)
    return render(request, 'terrarium/t_history_all.html', {
        'terrarium_history': terrarium_history,
    })


def terrarium_history_add(request, id):
    htt_choices = [(htt.id, htt.name) for htt in get_htt()]
    form = EventsForm(request.POST or None)
    form.fields['event'].choices = htt_choices

    if request.method == 'POST' and form.is_valid():
        TerrariumHistory.objects.create(
            terrarium_id=id,
            event_id=form.cleaned_data['event'],
            text=form.cleaned_data['text'],
            date=form.cleaned_data['date'],
        )
        messages.success(request, 'Added terrarium event/action successfully!')
        return redirect('terrariums:detail', id=id)

    return render(request, 'terrarium/t_history_add.html', {
        'form': form,
        'id': id,
    })


def terrarium_history_edit(request, id):
    event = get_object_or_404(TerrariumHistory, pk=id)
    htt_choices = [(htt.id, htt.name) for htt in get_htt()]

    if request.method == 'POST':
        form = EventsForm(request.POST)
        form.fields['event'].choices = htt_choices
        if form.is_valid():
            event.event_id = form.cleaned_data['event']
            event.text = form.cleaned_data['text']
            event.date = form.cleaned_data['date']
            event.save()
            messages.success(request, 'Changes to terrarium history saved!')
            return redirect('terrariums:detail', id=event.terrarium_id)
    else:
        form = EventsForm(initial={
            'event': event.event_id,
            'text': event.text,
            'date': event.date,
        })
        form.fields['event'].choices = htt_choices

    return JsonResponse({
        'htmlresponse': render(request, 'terrarium/t_history_edit.html', {
            'form': form,
            'data': event,
        }).content.decode()
    })


def terrarium_history_delete(request, id):
    if request.method == 'POST':
        event = get_object_or_404(TerrariumHistory, pk=id)
        event.delete()
        messages.success(request, 'Deleted terrarium history successfully!')
        return HttpResponse(status=200)
