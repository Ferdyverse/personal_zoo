import os
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.conf import settings
from django.utils.text import get_valid_filename

from .models import Document
from .forms import DocumentForm
from animals.models import Animal
from terrariums.models import Terrarium
from core.utils import allowed_file


@login_required
def download(request, id):
    UPLOAD_FOLDER = settings.MEDIA_ROOT
    doc = get_object_or_404(Document, pk=id)
    file_path = os.path.join(UPLOAD_FOLDER, 'documents', doc.filename)
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=doc.filename)


@login_required
def add(request, target, id):
    UPLOAD_FOLDER = settings.MEDIA_ROOT

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES.get('filename')
            name = form.cleaned_data['name']

            if uploaded_file and uploaded_file.name:
                if allowed_file(uploaded_file.name):
                    filename = f"{uuid.uuid4().hex[:8]}_{get_valid_filename(uploaded_file.name)}"
                    with open(os.path.join(UPLOAD_FOLDER, 'documents', filename), 'wb+') as dest:
                        for chunk in uploaded_file.chunks():
                            dest.write(chunk)
                else:
                    messages.error(request, 'Invalid file type. Please upload a valid file. (pdf, png, jpg)')
                    return redirect(f'/{target}/{id}/' if target == 'animal' else f'/terrarium/{id}/')

                Document.objects.create(
                    name=name,
                    filename=filename,
                    animal_id=id if target == 'animal' else None,
                    terrarium_id=id if target == 'terrarium' else None,
                )
                messages.success(request, 'Added document successfully!')
            else:
                messages.error(request, 'No file found!')

            return redirect(f'/animal/{id}/' if target == 'animal' else f'/terrarium/{id}/')

    form = DocumentForm()
    context = {'id': id, 'form': form, 'target': target}
    if target == 'animal':
        context['animal'] = get_object_or_404(Animal, pk=id)
    elif target == 'terrarium':
        context['terrarium'] = get_object_or_404(Terrarium, pk=id)

    return render(request, 'documents/document_add.html', context)


@login_required
def edit(request, id):
    UPLOAD_FOLDER = settings.MEDIA_ROOT
    document = get_object_or_404(Document, pk=id)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document.name = form.cleaned_data['name']
            uploaded_file = request.FILES.get('filename')

            if uploaded_file and uploaded_file.name:
                if allowed_file(uploaded_file.name):
                    filename = f"{uuid.uuid4().hex[:8]}_{get_valid_filename(uploaded_file.name)}"
                    with open(os.path.join(UPLOAD_FOLDER, 'documents', filename), 'wb+') as dest:
                        for chunk in uploaded_file.chunks():
                            dest.write(chunk)
                    old_path = os.path.join(UPLOAD_FOLDER, 'documents', document.filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                    document.filename = filename
                else:
                    messages.error(request, 'Invalid file format.')

            document.save()
            messages.success(request, 'Changes to document saved!')

            if document.animal_id:
                return redirect(f'/animal/{document.animal_id}/')
            else:
                return redirect(f'/terrarium/{document.terrarium_id}/')

    form = DocumentForm(initial={'name': document.name})
    return JsonResponse({
        'htmlresponse': render(request, 'documents/document_edit.html', {
            'form': form,
            'id': id,
        }).content.decode()
    })


@login_required
def delete(request, id):
    if request.method == 'POST':
        UPLOAD_FOLDER = settings.MEDIA_ROOT
        document = get_object_or_404(Document, pk=id)

        file_path = os.path.join(UPLOAD_FOLDER, 'documents', document.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        document.delete()
        messages.success(request, 'Deleted document successfully!')
        return HttpResponse(status=200)
