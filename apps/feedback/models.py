from django.db import models
from ..accounts.models import User
from ..courses.models import Question
from miprepa.utils.mixins import UidMixin


class Comment(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    text = models.TextField(verbose_name='Texto')
    user = models.ForeignKey(User, related_name='feedback', verbose_name='Usuario')
    question = models.ForeignKey(Question, related_name='feedback', verbose_name='Pregunta')
    is_closed = models.BooleanField(default=False, verbose_name='Cerrada')

    def __str__(self):
        return 'User:{}  Question:{}'.format(self.user, self.questions)

    class Meta:
        ordering = ("-created_at",)


class Answer(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    text = models.TextField(verbose_name='Texto')
    user = models.ForeignKey(User, related_name='comments', verbose_name='Usuario')
    feedback = models.ForeignKey(Comment, related_name='comments', verbose_name='Comment')

    def __str__(self):
        return 'User:{}  Comment:{}'.format(self.user, self.text)

    class Meta:
        ordering = ("-created_at",)


class Error(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    text = models.TextField(verbose_name='Texto')
    user = models.ForeignKey(User, related_name='errors', verbose_name='Usuario')
    question = models.ForeignKey(Question, related_name='errors', verbose_name='Pregunta')
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return 'User:{} Question:{} Error:{}'.format(self.user, self.questions, self.text)

    class Meta:
        ordering = ("-created_at",)
