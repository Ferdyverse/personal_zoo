from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('download/<int:id>/', views.download, name='download'),
    path('add/<str:target>/<int:id>/', views.add, name='add'),
    path('edit/<int:id>/', views.edit, name='edit'),
    path('delete/<int:id>/', views.delete, name='delete'),
]
