from django.urls import path
from . import views

app_name = 'feeding'

urlpatterns = [
    path('get_units/<int:id>/', views.get_units, name='get_units'),
    path('get_all/<int:id>/', views.get_all, name='get_all'),
    path('get_qr/<int:id>/', views.qr_code, name='qr_code'),
    path('add/<int:id>/', views.add, name='add'),
    path('multi/', views.multi_add, name='multi_add'),
    path('edit/<int:id>/', views.edit, name='edit'),
    path('delete/<int:id>/', views.delete, name='delete'),
]
