from django.urls import path
from . import views

app_name = 'animals'

urlpatterns = [
    path('<int:id>/', views.animal_detail, name='detail'),
    path('add/', views.add, name='add'),
    path('edit/<int:id>/', views.edit, name='edit'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('get_weight/<int:id>/', views.get_weight, name='get_weight'),
]
