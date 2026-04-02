from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.profile, name='profile'),
    path('admin/', views.admin_panel, name='admin'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change_password/<int:id>/', views.update_password, name='update_password'),
    path('change_language/<str:lang>/', views.update_language, name='update_language'),
    path('change/<str:mode>/<int:id>/', views.change, name='change'),
]
