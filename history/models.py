import datetime
from django.db import models


class HistoryType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Name')
    note = models.CharField(max_length=255, blank=True, verbose_name='Note')

    class Meta:
        db_table = 'history_type'
        verbose_name = 'Event Type'
        verbose_name_plural = 'Event Types'

    def __str__(self):
        return self.name


class History(models.Model):
    animal = models.ForeignKey(
        'animals.Animal',
        on_delete=models.CASCADE,
        related_name='history',
        db_column='animal',
        verbose_name='Animal',
    )
    event = models.ForeignKey(
        HistoryType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='history',
        db_column='event',
        verbose_name='Event Type',
    )
    text = models.CharField(max_length=255, blank=True, verbose_name='Details')
    date = models.DateField(default=datetime.date.today, verbose_name='Date')

    class Meta:
        db_table = 'history'
        verbose_name = 'History Entry'
        verbose_name_plural = 'History'

    def __str__(self):
        return f'{self.animal} – {self.event} ({self.date})'
