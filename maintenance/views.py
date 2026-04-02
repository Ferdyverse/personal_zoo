import os
import shutil
import sqlite3
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from animals.models import Animal
from terrariums.models import Terrarium
from accounts.models import User
from app_settings.models import AppSetting
from core.utils import allowed_file, insert_defaults


def db_path():
    return str(settings.DATABASES['default']['NAME'])


def db_fetch(query, mode=True):
    try:
        conn = sqlite3.connect(db_path())
        c = conn.cursor()
        c.execute(query)
        data = c.fetchall() if mode else c.fetchone()
        conn.close()
        return data
    except Exception:
        return False


def db_update(query):
    try:
        conn = sqlite3.connect(db_path())
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def db_col_exists(table, col):
    try:
        result = db_fetch(
            f"SELECT COUNT(*) FROM pragma_table_info('{table}') WHERE name='{col}'",
            False
        )
        return result and result[0] > 0
    except Exception:
        return False


@login_required
def main(request):
    return render(request, 'maintenance/maintenance.html', {'location': 'maintenance'})


@login_required
def tasks(request, task):
    UPLOAD_FOLDER = settings.MEDIA_ROOT

    if task == 'cleanup_images':
        animal_images = set(Animal.objects.values_list('image', flat=True))
        terrarium_images = set(Terrarium.objects.values_list('image', flat=True))

        for image in os.listdir(os.path.join(UPLOAD_FOLDER, 'animals')):
            if image != 'dummy.jpg' and image not in animal_images:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, 'animals', image))
                except Exception:
                    pass

        for image in os.listdir(os.path.join(UPLOAD_FOLDER, 'terrariums')):
            if image != 'dummy.jpg' and image not in terrarium_images:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, 'terrariums', image))
                except Exception:
                    pass

        messages.success(request, 'Deleted old images!')
        return redirect('maintenance:main')

    if task == 'color_reset':
        AppSetting.objects.filter(setting='color_female').update(value='#e481e4')
        AppSetting.objects.filter(setting='color_male').update(value='#89cff0')
        AppSetting.objects.filter(setting='color_other').update(value='#29a039')
        messages.success(request, 'Reset colors to default!')
        return redirect('maintenance:main')

    messages.warning(request, f'Unknown task: {task}')
    return redirect('maintenance:main')


@login_required
def do_update(request):
    error = ''
    UPLOAD_FOLDER = settings.MEDIA_ROOT

    # Ensure admin exists
    users_count = User.objects.count()
    admins_count = User.objects.filter(is_staff=True).count()
    if users_count > 0 and admins_count == 0:
        first_user = User.objects.first()
        first_user.is_staff = True
        first_user.save(update_fields=['is_staff'])
        error += f'No admin found! {first_user.email} is now administrator!'

    # Migrate old images to subdirectory
    try:
        for image in os.listdir(UPLOAD_FOLDER):
            if allowed_file(image):
                src = os.path.join(UPLOAD_FOLDER, image)
                dst = os.path.join(UPLOAD_FOLDER, 'animals', image)
                shutil.move(src, dst)
    except Exception as e:
        error += f'Migrate animal images -> Error: {e}\n'

    # Insert defaults
    try:
        insert_defaults()
    except Exception as e:
        error += f'Insert defaults -> Error: {e}\n'

    if error:
        messages.warning(request, f'Update with warnings: {error}')
    else:
        messages.success(request, 'Update done!')

    return redirect('/')
