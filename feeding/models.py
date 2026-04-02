import datetime
from django.db import models


class FeedingType(models.Model):
    UNIT_CHOICES = [
        ('weight', 'Weight'),
        ('text', 'Text'),
        ('size', 'Size'),
    ]

    name = models.CharField(max_length=255, verbose_name='Name')
    unit = models.CharField(max_length=50, choices=UNIT_CHOICES, verbose_name='Unit Type')
    detail = models.CharField(max_length=255, blank=True, verbose_name='Detail',
        help_text='For weight: unit label (e.g. "gr"). For size: comma-separated options (e.g. "small,medium,large"). For text: description.')

    class Meta:
        db_table = 'feeding_type'
        verbose_name = 'Feeding Type'
        verbose_name_plural = 'Feeding Types'

    def __str__(self):
        return self.name


class Feeding(models.Model):
    animal = models.ForeignKey(
        'animals.Animal',
        on_delete=models.CASCADE,
        related_name='feedings',
        db_column='animal',
        verbose_name='Animal',
    )
    feeding_type = models.ForeignKey(
        FeedingType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='feedings',
        db_column='type',
        verbose_name='Feeding Type',
    )
    count = models.IntegerField(default=1, verbose_name='Count')
    unit = models.CharField(max_length=255, blank=True, verbose_name='Amount / Size')
    date = models.DateField(default=datetime.date.today, verbose_name='Date')

    class Meta:
        db_table = 'feedings'
        verbose_name = 'Feeding'
        verbose_name_plural = 'Feedings'

    def __str__(self):
        return f'{self.animal} – {self.feeding_type} ({self.date})'
