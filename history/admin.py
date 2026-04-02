from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import History, HistoryType


@admin.register(HistoryType)
class HistoryTypeAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(History)
class HistoryAdmin(ModelAdmin):
    list_display = ('animal', 'event', 'text', 'date')
    list_filter = ('event',)
    search_fields = ('animal__name', 'text')
    ordering = ('-date',)
