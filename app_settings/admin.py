import json
from django import forms
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldAdminColorInputWidget, UnfoldAdminSelectMultipleWidget
from .models import AppSetting, Notification

COLOR_SETTINGS = {'color_female', 'color_male', 'color_other'}


class AppSettingForm(forms.ModelForm):
    class Meta:
        model = AppSetting
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if not instance:
            return

        if instance.setting in COLOR_SETTINGS:
            self.fields['value'].widget = UnfoldAdminColorInputWidget()

        elif instance.setting == 'feeding_size':
            from animals.models import AnimalType
            choices = [(str(at.id), at.name) for at in AnimalType.objects.all().order_by('name')]
            try:
                initial = json.loads(instance.value or '[]')
            except Exception:
                initial = []
            self.fields['value'] = forms.MultipleChoiceField(
                label='Feeding Size',
                choices=choices,
                initial=initial,
                required=False,
                widget=UnfoldAdminSelectMultipleWidget(),
            )
            self.initial['value'] = initial

    def clean_value(self):
        setting = self.instance.setting if self.instance else None
        val = self.cleaned_data.get('value')
        if setting == 'feeding_size':
            return json.dumps(val if val else [])
        return val


@admin.register(AppSetting)
class AppSettingAdmin(ModelAdmin):
    form = AppSettingForm
    list_display = ('setting', 'name', 'display_value', 'description')
    search_fields = ('setting', 'name')
    ordering = ('setting',)

    @admin.display(description='Value')
    def display_value(self, obj):
        val = obj.value
        if val and val.startswith('#') and len(val) in (4, 7):
            return format_html(
                '<span style="display:inline-flex;align-items:center;gap:8px;">'
                '<span style="display:inline-block;width:20px;height:20px;'
                'background:{};border-radius:4px;border:1px solid #555;"></span>'
                '{}</span>',
                val, val,
            )
        if obj.setting == 'feeding_size':
            try:
                from animals.models import AnimalType
                ids = json.loads(val or '[]')
                names = list(AnimalType.objects.filter(pk__in=ids).values_list('name', flat=True))
                return ', '.join(names) if names else '—'
            except Exception:
                pass
        return val


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ('message', 'date', 'interval')
    ordering = ('date',)
