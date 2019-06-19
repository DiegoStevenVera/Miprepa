from enum import Enum
from django.db import models
from ..accounts.models import User
from ..universities.models import University, KnowledgeArea
from miprepa.utils.mixins import UidMixin


class Notification(UidMixin, models.Model):
    class Gender(Enum):
        m = "Masculino"
        f = "Femenino"
        b = "Ambos"

    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=500, verbose_name='Título')
    image = models.ImageField(upload_to='notifications/images/', null=True, blank=True, verbose_name='Imagen')
    text = models.TextField(blank=True, null=True, verbose_name='Texto')
    min_age = models.PositiveIntegerField(blank=True, null=True, verbose_name='Edad mínima')
    max_age = models.PositiveIntegerField(blank=True, null=True, verbose_name='Edad máxima')
    gender = models.CharField(max_length=1, blank=True, choices=[(item.name, item.value) for item in Gender])
    universities = models.ManyToManyField(University, blank=True, related_name='notifications',
                                          verbose_name='Universidades')
    knowldge_area = models.ManyToManyField(KnowledgeArea, blank=True, related_name='notifications',
                                           verbose_name='Area')
    target_users = models.ManyToManyField(User, blank=True, related_name='notifications', verbose_name='Usuarios')
    viewed = models.PositiveIntegerField(default=0, verbose_name='Numero de Recibidos')

    def __str__(self):
        return '{}'.format(self.text)

    class Meta:
        ordering = ("-created_at",)


class NotificationUser(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    seen_at = models.DateTimeField(blank=True, null=True, verbose_name='Día y hora de lectura')
    user = models.ForeignKey(User, related_name='notifications_user', verbose_name='Usuarios')
    push_notification = models.ForeignKey(Notification, related_name='notifications_user',
                                          verbose_name='Push notifications')

    def __str__(self):
        return 'Usuario:{}    PushNotification:{}'.format(self.user, self.push_notification)

    class Meta:
        ordering = ("-created_at",)
