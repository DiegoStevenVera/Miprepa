from django.db import models

from miprepa.utils.mixins import UidMixin


class University(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='universities/images/')
    is_enabled = models.BooleanField(default=True)

    def __str__(self):
        return '{}'.format(self.name)


class KnowledgeArea(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='universities/images/', null=True, blank=True)
    is_enabled = models.BooleanField(default=True)

    def __str__(self):
        return '{}'.format(self.name)


