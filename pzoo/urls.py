from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

import core.views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Core routes
    path('', core_views.home, name='home'),
    path('print/', core_views.print_data, name='print'),
    path('print/<int:id>/', core_views.print_data, name='print_with_id'),

    # Legacy redirects
    path('update', lambda req: redirect('/maintenance/update'), name='old_update'),
    path('django-admin/', lambda req: redirect('/admin/'), name='old_admin'),
    path('login', lambda req: redirect('/account/login'), name='to_login'),

    # Apps
    path('account/', include('accounts.urls', namespace='accounts')),
    path('animal/', include('animals.urls', namespace='animals')),
    path('feeding/', include('feeding.urls', namespace='feeding')),
    path('history/', include('history.urls', namespace='history')),
    path('terrarium/', include('terrariums.urls', namespace='terrariums')),
    path('document/', include('documents.urls', namespace='documents')),
    path('settings/', include('app_settings.urls', namespace='app_settings')),
    path('api/v1/', include('api.urls', namespace='api')),
    path('maintenance/', include('maintenance.urls', namespace='maintenance')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
