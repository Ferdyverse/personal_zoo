from django.db import models


class AppSetting(models.Model):
    setting = models.CharField(max_length=100, unique=True, verbose_name='Setting Key')
    value = models.CharField(max_length=1000, blank=True, verbose_name='Value')
    name = models.CharField(max_length=255, blank=True, verbose_name='Display Name')
    description = models.CharField(max_length=500, blank=True, verbose_name='Description')

    class Meta:
        db_table = 'settings'
        verbose_name = 'Setting'
        verbose_name_plural = 'Settings'

    def __str__(self):
        return self.name or self.setting


class Notification(models.Model):
    date = models.DateField(null=True, blank=True, verbose_name='Date')
    message = models.CharField(max_length=500, blank=True, verbose_name='Message')
    interval = models.CharField(max_length=50, blank=True, verbose_name='Interval')

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return self.message
