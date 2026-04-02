import datetime
from django.db import models


class AnimalType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Name')
    f_min = models.IntegerField(default=0, verbose_name='Feeding Min (%)',
        help_text='Minimum feeding size as percentage of body weight')
    f_max = models.IntegerField(default=0, verbose_name='Feeding Max (%)',
        help_text='Maximum feeding size as percentage of body weight')

    class Meta:
        db_table = 'animal_type'
        verbose_name = 'Animal Type'
        verbose_name_plural = 'Animal Types'

    def __str__(self):
        return self.name


class Animal(models.Model):
    GENDER_CHOICES = [
        ('female', 'Female'),
        ('male', 'Male'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255, verbose_name='Name')
    art = models.ForeignKey(
        AnimalType, on_delete=models.SET_NULL, null=True, related_name='animals',
        verbose_name='Animal Type',
    )
    morph = models.CharField(max_length=255, blank=True, verbose_name='Morph')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, verbose_name='Gender')
    birth = models.CharField(max_length=40, blank=True, verbose_name='Date of Birth')
    notes = models.TextField(blank=True, verbose_name='Notes')
    image = models.CharField(max_length=255, default='dummy.jpg', verbose_name='Image Filename')
    default_ft = models.ForeignKey(
        'feeding.FeedingType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        db_column='default_ft',
        verbose_name='Default Feeding Type',
    )
    terrarium = models.ForeignKey(
        'terrariums.Terrarium',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='animals',
        db_column='terrarium',
        verbose_name='Terrarium',
    )
    background_color = models.CharField(max_length=20, blank=True, verbose_name='Card Color')
    created_date = models.DateField(default=datetime.date.today, verbose_name='Created')
    updated_date = models.DateField(default=datetime.date.today, verbose_name='Last Updated')

    class Meta:
        db_table = 'animals'
        verbose_name = 'Animal'
        verbose_name_plural = 'Animals'

    def __str__(self):
        return self.name
