from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.main, name='main'),
    path('tasks/<str:task>/', views.tasks, name='tasks'),
    path('update/', views.do_update, name='update'),
]
