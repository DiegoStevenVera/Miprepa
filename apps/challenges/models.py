from enum import Enum
from django.contrib.postgres.fields import JSONField
from django.db import models
from ..accounts.models import User, UserUniversity
from ..courses.models import Question
from miprepa.utils.mixins import UidMixin


class ChallengeTimeOut(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    user_university = models.ForeignKey(UserUniversity, related_name='challengestimeout', verbose_name='Usuario')
    questions_saved = JSONField(default=[], blank=True, verbose_name='Preguntas Guardadas')  # {"id":id,"marked":"a"}
    questions_requested = JSONField(default=[], blank=True, verbose_name='Preguntas Pedidas')  # [id,id,...]
    quantity_questions = models.IntegerField(null=True, blank=True, verbose_name='Preguntas correctas')

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = "Reto Time Out"
        verbose_name_plural = "Retos Time Out"
        ordering = ('-created_at', '-quantity_questions')


class ChallengeSurvival(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    user_university = models.ForeignKey(UserUniversity, related_name='challengessurvival')
    questions_saved = JSONField(default=[], blank=True)  # [{"id":id,"marked":"a","correct":True},...]
    questions_requested = JSONField(default=[], blank=True)  # [id,id,...]
    quantity_questions = models.IntegerField(default=0)
    time = models.IntegerField(default=0)

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = "Reto Survival"
        verbose_name_plural = "Retos Survival"
        ordering = ('-created_at', '-quantity_questions', 'time')


class ChallengeTest(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    user_university = models.ForeignKey(UserUniversity, related_name='challengestest')
    questions_saved = JSONField(default=[], blank=True)  # {"id":id,"marked":"a"}
    questions_requested = JSONField(default=[], blank=True)  # [id,id,...]
    courses_id = JSONField(default=[], blank=True)  # [id,id,...]
    goods = models.IntegerField(default=0)
    bads = models.IntegerField(default=0)
    blanks = models.IntegerField(default=0)
    time = models.IntegerField(default=0)

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = "Reto Test"
        verbose_name_plural = "Retos Test"
        ordering = ('-created_at', '-goods', 'bads', 'blanks', 'time')


class History(UidMixin, models.Model):
    class Type(Enum):
        correct = "Correcto"
        wrong = "Erróneo"
        blank = "En blanco"

    created_at = models.DateTimeField(auto_now_add=True)
    date_at = models.DateField(auto_now_add=True)
    user_university = models.ForeignKey(UserUniversity, related_name='history', db_index=True)
    question = models.ForeignKey(Question, related_name='resolutions')
    answer = models.CharField(max_length=1, blank=True)
    ch_timeout = models.ForeignKey(ChallengeTimeOut, null=True, blank=True, related_name='history')
    ch_survival = models.ForeignKey(ChallengeSurvival, null=True, blank=True, related_name='history')
    ch_test = models.ForeignKey(ChallengeTest, null=True, blank=True, related_name='history')
    status = models.CharField(max_length=8, choices=[(item.name, item.value) for item in Type], db_index=True)
    experience = models.PositiveIntegerField(default=0)


class CountQuestion(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user_university = models.ForeignKey(UserUniversity, related_name='count_history', db_index=True)
    question = models.ForeignKey(Question, related_name='count_history')
    count = models.IntegerField(default=0)

    def __str__(self):
        return u'{} entre {} - {}'.format(self.user_university, self.question, self.count)

    class Meta:
        unique_together = ('user_university', 'question')
