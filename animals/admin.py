from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Animal, AnimalType


@admin.register(AnimalType)
class AnimalTypeAdmin(ModelAdmin):
    list_display = ('name', 'f_min', 'f_max')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Animal)
class AnimalAdmin(ModelAdmin):
    list_display = ('name', 'art', 'morph', 'gender', 'birth', 'terrarium')
    list_filter = ('gender', 'art')
    search_fields = ('name', 'morph')
    ordering = ('name',)
