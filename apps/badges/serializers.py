# coding=utf-8
from rest_framework import serializers

from .models import Level, Badge

__author__ = 'carlos'


class SerializerLevel(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ('uid', 'name', 'logo', 'min_experience', 'max_experience')


class SerializerLevelInProfile(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ('uid', 'name', 'logo')


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ('uid', 'name', 'logo', 'type', 'all_universities')
