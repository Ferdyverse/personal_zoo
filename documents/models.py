from django.db import models


class Document(models.Model):
    name = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    animal = models.ForeignKey(
        'animals.Animal',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
        db_column='animal_id',
    )
    terrarium = models.ForeignKey(
        'terrariums.Terrarium',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
        db_column='terrarium_id',
    )

    class Meta:
        db_table = 'documents'

    def __str__(self):
        return self.name
