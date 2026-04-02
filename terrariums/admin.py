from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Terrarium, TerrariumType, TerrariumEquipment, TerrariumLamps, TerrariumHistory, TerrariumHistoryType


@admin.register(TerrariumType)
class TerrariumTypeAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(TerrariumHistoryType)
class TerrariumHistoryTypeAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Terrarium)
class TerrariumAdmin(ModelAdmin):
    list_display = ('name', 'terrarium_type', 'size')
    list_filter = ('terrarium_type',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(TerrariumEquipment)
class TerrariumEquipmentAdmin(ModelAdmin):
    list_display = ('terrarium', 'name', 'text')
    search_fields = ('name', 'terrarium__name')
    ordering = ('terrarium', 'name')


@admin.register(TerrariumLamps)
class TerrariumLampsAdmin(ModelAdmin):
    list_display = ('terrarium', 'lamp_type', 'watt')
    search_fields = ('terrarium__name',)
    ordering = ('terrarium', 'lamp_type')


@admin.register(TerrariumHistory)
class TerrariumHistoryAdmin(ModelAdmin):
    list_display = ('terrarium', 'event', 'text', 'date')
    list_filter = ('event',)
    search_fields = ('terrarium__name', 'text')
    ordering = ('-date',)
