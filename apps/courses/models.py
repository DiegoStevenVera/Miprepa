from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields.array import ArrayField
from django.db import models
from apps.universities.models import KnowledgeArea
from miprepa.utils.mixins import UidMixin


class Course(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Ingreso')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='Fecha de modificacion')
    is_enabled = models.BooleanField(default=True)
    logo = models.ImageField(upload_to='courses/logo', null=True, blank=True)
    name = models.CharField(max_length=400)
    count_questions = models.IntegerField(default=0)
    identify = models.CharField(max_length=400, unique=True)
    cover = models.ImageField(upload_to='courses/cover', null=True, blank=True)
    knowledge_area = models.ManyToManyField(KnowledgeArea, related_name='courses')

    def __str__(self):
        return self.name


class Topic(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Ingreso')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='Fecha de modificacion')
    is_enabled = models.BooleanField(default=True)
    name = models.CharField(max_length=250)
    course = models.ForeignKey(Course, related_name='topics')
    frequency = models.IntegerField(default=0)
    order_customize = models.IntegerField(default=0)
    desc_order_customizer = models.CharField(max_length=180, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tema"
        verbose_name_plural = "Temas"
        ordering = ['order_customize']

    def countquestions(self):
        return self.questions.all().count()


class Question(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Ingreso')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='Fecha de modificacion')
    text = models.CharField(max_length=600)
    options = JSONField(verbose_name='opciones', default={})
    topic = models.ForeignKey(Topic, related_name='questions')
    date_show = models.CharField(max_length=100, blank=True)
    year_show = models.IntegerField(default=0, verbose_name='Año de pregunta')
    argument_answer = models.TextField(blank=True, verbose_name='Argumento de la respuesta')
    bookmarked_by = ArrayField(models.IntegerField(), default=[], blank=True)
    verified = models.BooleanField(default=True)
    source_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"
