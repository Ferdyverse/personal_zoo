from django.urls import path
from . import views

app_name = 'terrariums'

urlpatterns = [
    path('<int:id>/', views.terrarium_detail, name='detail'),
    path('add/', views.add, name='add'),
    path('edit/<int:id>/', views.edit, name='edit'),
    path('delete/<int:id>/', views.delete, name='delete'),
    # Equipment
    path('equipment/add/<int:id>/', views.equipment_add, name='equipment_add'),
    path('equipment/edit/<int:id>/', views.equipment_edit, name='equipment_edit'),
    path('equipment/delete/<int:id>/', views.equipment_delete, name='equipment_delete'),
    # Lamps
    path('lamp/add/<int:id>/', views.lamp_add, name='lamp_add'),
    path('lamp/edit/<int:id>/', views.lamp_edit, name='lamp_edit'),
    path('lamp/delete/<int:id>/', views.lamp_delete, name='lamp_delete'),
    # History
    path('history/get_all/<int:id>/', views.terrarium_history_get_all, name='terrarium_history_get_all'),
    path('history/add/<int:id>/', views.terrarium_history_add, name='terrarium_history_add'),
    path('history/edit/<int:id>/', views.terrarium_history_edit, name='terrarium_history_edit'),
    path('history/delete/<int:id>/', views.terrarium_history_delete, name='terrarium_history_delete'),
]
