from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.conf import settings

from .models import User
from .forms import RegisterForm, LoginForm, PasswordForm


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {
        'user_obj': request.user,
        'location': 'profile',
        'languages': settings.LANGUAGES,
    })


@login_required
def admin_panel(request):
    if not request.user.is_staff:
        messages.warning(request, 'You need to be an Administrator to view this page!')
        return redirect('/')
    users = User.objects.all()
    return render(request, 'accounts/admin.html', {'users': users, 'location': 'account'})


@login_required
def update_password(request, id):
    target_user = get_object_or_404(User, pk=id)
    if request.user != target_user:
        return HttpResponse(status=403)

    form = PasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        if target_user.check_password(form.cleaned_data['old_password']):
            target_user.set_password(form.cleaned_data['new_password'])
            target_user.save()
            messages.success(request, 'Password changed!')
            return JsonResponse({'status': 'ok'})
        else:
            messages.danger(request, 'Wrong current password entered!')
            return redirect('accounts:profile')
    elif request.method == 'GET':
        return render(request, 'accounts/password_form.html', {
            'form': form,
            'location': 'profile',
            'id': id,
        })
    else:
        return JsonResponse(form.errors)


@login_required
def update_language(request, lang):
    request.user.lang = lang
    request.user.save(update_fields=['lang'])
    return HttpResponse(status=200)


@login_required
def change(request, mode, id):
    if not request.user.is_staff:
        messages.warning(request, 'You need to be an Administrator to view this page!')
        return redirect('/')

    target_user = get_object_or_404(User, pk=id)

    if request.user == target_user:
        messages.warning(request, 'You can not change your own account!')
        return HttpResponse(status=200)

    if mode == 'admin':
        target_user.is_staff = not target_user.is_staff
        target_user.save(update_fields=['is_staff'])
    elif mode == 'active':
        target_user.is_active = not target_user.is_active
        target_user.save(update_fields=['is_active'])
    elif mode == 'delete':
        target_user.delete()

    return HttpResponse(status=200)


def register(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already registered.')
        return redirect('/')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        is_first_admin = not User.objects.filter(is_staff=True).exists()
        user = User(
            username=form.cleaned_data['email'],
            email=form.cleaned_data['email'],
            is_staff=is_first_admin,
            is_active=is_first_admin,
        )
        user.set_password(form.cleaned_data['password'])
        user.save()

        if is_first_admin:
            messages.success(request, 'Registration successful. You are an administrator!')
        else:
            messages.success(request, 'Registration successful. Ask an administrator to activate your account!')

        login(request, user)
        return redirect('/')

    return render(request, 'accounts/register.html', {'form': form, 'location': 'register'})


def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('/')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('/')
            else:
                messages.warning(request, 'Your account is not activated!')
        else:
            messages.warning(request, 'Invalid email and/or password.')

    return render(request, 'accounts/login.html', {'form': form, 'location': 'login'})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You were logged out.')
    return redirect('/account/login')
