from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user model with language preference."""

    LANGUAGE_CHOICES = [('de', 'Deutsch'), ('en', 'English')]

    lang = models.CharField(max_length=5, default='en', choices=LANGUAGE_CHOICES)

    # AbstractUser already has is_active, is_staff (as admin equivalent),
    # email, password, date_joined (as created_on equivalent).
    # We use is_staff as the is_admin equivalent.

    class Meta:
        db_table = 'accounts_user'

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.is_staff

    @is_admin.setter
    def is_admin(self, value):
        self.is_staff = value
