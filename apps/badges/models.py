from enum import Enum
from django.db import models
from ..accounts.models import User, UserUniversity
from apps.universities.models import University
from ..courses.models import Course
from miprepa.utils.mixins import UidMixin


class Level(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, verbose_name='Nombre del Nivel')
    logo = models.ImageField(upload_to='levels/logo', null=True, blank=True)
    is_enabled = models.BooleanField(verbose_name='Habilitar', default=True)
    min_experience = models.IntegerField(verbose_name='Experiencia mínima')
    max_experience = models.IntegerField(verbose_name='Experiencia máxima')

    def __str__(self):
        return u'{} entre {} - {}'.format(self.name, self.min_experience, self.max_experience)

    class Meta:
        ordering = ("-created_at",)


class Badge(UidMixin, models.Model):
    class Type(Enum):
        practice = "Práctica"
        survival = "Sobreviviente"
        miscellany = "Miscelánea"

    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, verbose_name='Nombre del badge')
    logo = models.ImageField(upload_to='badges/logo', null=True, blank=True)
    is_enabled = models.BooleanField(verbose_name='Habilitar', default=True)
    university = models.ForeignKey(University, related_name='badges', null=True, blank=True)
    all_universities = models.BooleanField(default=False)
    min_questions = models.IntegerField(verbose_name='Cantidad mínima de preguntas de la universidad', blank=True,
                                        null=True)
    type = models.CharField(max_length=10, choices=[(item.name, item.value) for item in Type], blank=True, null=True)
    min_quantity_challenge = models.IntegerField(verbose_name='Cantidad mínima por Reto', blank=True, null=True)
    user_university = models.ManyToManyField(UserUniversity, related_name='badges', through='UserUniversityBadge')

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        ordering = ("-created_at",)


class UserUniversityBadge(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    user_university = models.ForeignKey(UserUniversity, related_name='useruniversity_badges', on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, related_name='useruniversity_badges', on_delete=models.CASCADE)

    def __str__(self):
        return 'User:{} -Badge:{}'.format(self.user_university, self.badge)

    class Meta:
        ordering = ("-created_at",)
