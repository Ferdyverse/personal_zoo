from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('', views.main, name='main'),
    path('animals/', views.animals, name='animals'),
    path('animals/<int:id>/', views.animals, name='animal'),
    path('animals/<int:id>/feedings/', views.animal_feedings, name='animal_feedings'),
    path('animals/<int:id>/feedings/<str:argument>/', views.animal_feedings, name='animal_feedings_arg'),
    path('animals/<int:id>/history/', views.animal_history, name='animal_history'),
    path('animals/<int:id>/history/<int:e_type>/', views.animal_history, name='animal_history_type'),
    path('feeding_types/', views.get_feeding_types, name='feeding_types'),
]
