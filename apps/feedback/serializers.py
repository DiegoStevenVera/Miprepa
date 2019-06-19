from rest_framework import serializers

from ..accounts.serializers import UserInListFollowSerializer
from apps.accounts.models import User
from miprepa.utils.fields import UidRelatedField
from .models import Comment, Answer, Error

__author__ = 'carlos'


class AnswerSerializer(serializers.ModelSerializer):
    user = UidRelatedField(queryset=User.objects.all(), representation_serializer=UserInListFollowSerializer)

    class Meta:
        model = Answer
        fields = ('uid', 'text', 'user')


class CommentSerializer(serializers.ModelSerializer):
    user = UidRelatedField(queryset=User.objects.all(), representation_serializer=UserInListFollowSerializer)

    class Meta:
        model = Comment
        read_only_fields = ('uid', 'question', 'user')


class ListCommentSerializer(serializers.ModelSerializer):
    user = UserInListFollowSerializer(read_only=True)
    comments = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ('uid', 'created_at', 'text', 'is_closed', 'user', 'comments')


class ErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Error
        fields = ('uid', 'text', 'user', 'question', 'is_resolved')
        read_only_fields = ('uid', 'user', 'question', 'is_resolved')
