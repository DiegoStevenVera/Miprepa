from enum import Enum
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
from ..universities.models import University, KnowledgeArea
from miprepa.utils.mixins import UidMixin


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser,
                     **extra_fields):
        user = self.model(email=email, is_active=True,
                          is_staff=is_staff, is_superuser=is_superuser,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class User(UidMixin, AbstractBaseUser, PermissionsMixin):
    class Gender(Enum):
        m = "Masculino"
        f = "Femenino"

    email = models.EmailField(max_length=150, unique=True)
    nickname = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='users/photos/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    gender = models.CharField(max_length=1, blank=True, choices=[(item.name, item.value) for item in Gender])
    birthday = models.DateField(blank=True, null=True)
    desired_university = models.ManyToManyField(University, related_name='candidates', through='UserUniversity')
    is_new = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    objects = UserManager()

    def get_short_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def get_user_face(self):
        if self.social_auth.count() > 0:
            return True
        else:
            return False

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

        # def save(self, *args, **kwargs):
        #     if self.professional_career:
        #         self.desired_university = self.professional_career.university
        #     super(User, self).save(*args, **kwargs)


class UserUniversity(UidMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name='user_universities')
    desired_university = models.ForeignKey(University, related_name='user_universities')
    knowledge_area = models.ForeignKey(KnowledgeArea, related_name='user_universities', null=True, blank=True)
    experience = models.IntegerField(default=0, verbose_name='Experiencia')
    follows = ArrayField(models.IntegerField(), blank=True, null=True, verbose_name='Seguidos')
    first_option = models.BooleanField(default=False)

    def __str__(self):
        return u'{} entre {} - {}'.format(self.user, self.desired_university, self.knowledge_area)

    class Meta:
        unique_together = ('user', 'desired_university')
