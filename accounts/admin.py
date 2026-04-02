from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from .models import User


@admin.register(User)
class UserAdmin(ModelAdmin, UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ('username', 'email', 'lang', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'lang')
    search_fields = ('username', 'email')
    ordering = ('username',)
    fieldsets = UserAdmin.fieldsets + (
        ('Personal Zoo', {'fields': ('lang',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Personal Zoo', {'fields': ('lang',)}),
    )
