from rest_framework import serializers

from .models import University, KnowledgeArea


class KnowledgeAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeArea
        fields = ('uid', 'name', 'image')


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ('uid', 'name', 'image')
