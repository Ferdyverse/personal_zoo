from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Feeding, FeedingType


@admin.register(FeedingType)
class FeedingTypeAdmin(ModelAdmin):
    list_display = ('name', 'unit', 'detail')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Feeding)
class FeedingAdmin(ModelAdmin):
    list_display = ('animal', 'feeding_type', 'count', 'unit', 'date')
    list_filter = ('feeding_type',)
    search_fields = ('animal__name',)
    ordering = ('-date',)
