import datetime
from django.db import models


class TerrariumType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Name')

    class Meta:
        db_table = 'terrarium_type'
        verbose_name = 'Terrarium Type'
        verbose_name_plural = 'Terrarium Types'

    def __str__(self):
        return self.name


class Terrarium(models.Model):
    name = models.CharField(max_length=255, verbose_name='Name')
    size = models.CharField(max_length=255, blank=True, verbose_name='Size',
        help_text='e.g. 120x60x60 cm')
    terrarium_type = models.ForeignKey(
        TerrariumType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='terrariums',
        db_column='type',
        verbose_name='Type',
    )
    notes = models.TextField(blank=True, verbose_name='Notes')
    image = models.CharField(max_length=255, default='dummy.jpg', verbose_name='Image Filename')

    class Meta:
        db_table = 'terrariums'
        verbose_name = 'Terrarium'
        verbose_name_plural = 'Terrariums'

    def __str__(self):
        return self.name


class TerrariumEquipment(models.Model):
    terrarium = models.ForeignKey(
        Terrarium,
        on_delete=models.CASCADE,
        related_name='equipment',
        db_column='terrarium',
        verbose_name='Terrarium',
    )
    name = models.CharField(max_length=255, verbose_name='Equipment Name')
    text = models.TextField(blank=True, verbose_name='Description')

    class Meta:
        db_table = 'terrarium_equipment'
        verbose_name = 'Equipment'
        verbose_name_plural = 'Equipment'

    def __str__(self):
        return f'{self.name} ({self.terrarium})'


class TerrariumLamps(models.Model):
    terrarium = models.ForeignKey(
        Terrarium,
        on_delete=models.CASCADE,
        related_name='lamps',
        db_column='terrarium',
        verbose_name='Terrarium',
    )
    lamp_type = models.CharField(max_length=255, db_column='type', verbose_name='Lamp Type')
    watt = models.CharField(max_length=50, blank=True, verbose_name='Wattage')
    position = models.CharField(max_length=255, blank=True, verbose_name='Position')
    changed = models.DateField(null=True, blank=True, verbose_name='Last Changed')

    class Meta:
        db_table = 'terrarium_lamps'
        verbose_name = 'Lamp'
        verbose_name_plural = 'Lamps'

    def __str__(self):
        return f'{self.lamp_type} {self.watt}W'


class TerrariumHistoryType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Name')
    note = models.CharField(max_length=255, blank=True, verbose_name='Note')

    class Meta:
        db_table = 'terrarium_history_type'
        verbose_name = 'Terrarium Event Type'
        verbose_name_plural = 'Terrarium Event Types'

    def __str__(self):
        return self.name


class TerrariumHistory(models.Model):
    terrarium = models.ForeignKey(
        Terrarium,
        on_delete=models.CASCADE,
        related_name='history',
        db_column='terrarium',
        verbose_name='Terrarium',
    )
    event = models.ForeignKey(
        TerrariumHistoryType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='history',
        db_column='event',
        verbose_name='Event Type',
    )
    text = models.CharField(max_length=255, blank=True, verbose_name='Details')
    date = models.DateField(default=datetime.date.today, verbose_name='Date')

    class Meta:
        db_table = 'terrarium_history'
        verbose_name = 'Terrarium History Entry'
        verbose_name_plural = 'Terrarium History'

    def __str__(self):
        return f'{self.terrarium} – {self.event} ({self.date})'
