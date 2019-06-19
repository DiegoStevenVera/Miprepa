from django.conf import settings
from rest_framework import serializers
from rest_framework.fields import DictField
from ..accounts.serializers import UserInListFollowSerializer
from .models import ChallengeTimeOut, ChallengeSurvival, ChallengeTest
from ..courses.models import Question, Course
from ..courses.serializers import ListQuestionSerializer


class ChallengeTimeOutSerializer(serializers.ModelSerializer):
    questions_saved = serializers.ListField(child=DictField(), required=False)
    page_questions = serializers.SerializerMethodField(read_only=True)

    def get_page_questions(self, obj):
        page = self.context.get("page", 1)
        questions = obj.questions_requested[(page - 1) * 20:page * 20]
        return ListQuestionSerializer(Question.objects.filter(id__in=questions), many=True,
                                      context={'user_university': obj.user_university}).data

    class Meta:
        model = ChallengeTimeOut
        fields = ('uid', 'created_at', 'page_questions', 'questions_saved', 'quantity_questions')


class ChallengeSurvivalSerializer(serializers.ModelSerializer):
    questions_saved = serializers.ListField(child=DictField(), required=False)
    page_questions = serializers.SerializerMethodField(read_only=True)
    time = serializers.IntegerField(required=False)

    def get_page_questions(self, obj):
        page = self.context.get("page", 1)
        questions = obj.questions_requested[(page - 1) * 20:page * 20]
        return ListQuestionSerializer(Question.objects.filter(id__in=questions), many=True,
                                      context={'user_university': obj.user_university}).data

    class Meta:
        model = ChallengeSurvival
        fields = ('uid', 'created_at', 'page_questions', 'questions_saved', 'quantity_questions', 'time')


class ListChallengeSurvivalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeSurvival
        fields = ('uid', 'created_at', 'quantity_questions', 'time')


class ListCoursesWithQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('uid', 'name', 'logo', 'identify')


class ChallengeTestSerializer(serializers.ModelSerializer):
    questions_saved = serializers.ListField(child=DictField(), required=False)
    courses_id = serializers.ListField(child=DictField(), write_only=True)
    questions_requested = serializers.ListField(child=DictField(), required=False, write_only=True)
    questions = serializers.SerializerMethodField(read_only=True)

    def get_questions(self, obj):
        serializer = []
        for course in obj.questions_requested:
            uid = course.get('course')
            decoded = settings.HASHIDS.decode(uid)
            course_id = decoded[0] if decoded else None
            serializer.append(
                {"course": ListCoursesWithQuestionsSerializer(
                    Course.objects.filter(id=course_id).first()).data,
                 "questions": ListQuestionSerializer(Question.objects.filter(id__in=course.get('questions_id')),
                                                     many=True, context={'user_university': obj.user_university}).data}
            )
        return serializer

    class Meta:
        model = ChallengeTest
        fields = ('uid', 'created_at', 'questions_saved', 'questions_requested', 'courses_id', 'time',
                  'questions')


# class ListChallengeTimeOutSerializer(serializers.ModelSerializer):
#     questions_save = serializers.ListField(child=DictField(), required=False, write_only=True)
#     page_questions = serializers.SerializerMethodField(read_only=True)
#
#     def get_page_questions(self, obj):
#         page = self.context.get("page", 1)
#         questions = obj.questions_requested[(page - 1) * 20:page * 20]
#         return ListQuestionSerializer(Question.objects.filter(id__in=questions), many=True).data
#
#     class Meta:
#         model = ChallengeTimeOut
#         fields = ('uid', 'created_at', 'page_questions', 'questions_save', 'quantity_questions')




class ListChallengeTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeTest
        fields = ('uid', 'created_at', 'time', 'goods', 'bads', 'blanks')


class RankingTimeOutSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)

    def get_user(self, obj):
        return UserInListFollowSerializer(obj.user_university.user).data

    class Meta:
        model = ChallengeTimeOut
        fields = ('uid', 'created_at', 'quantity_questions', 'user')


class RankingSurvivalSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)

    def get_user(self, obj):
        return UserInListFollowSerializer(obj.user_university.user).data

    class Meta:
        model = ChallengeSurvival
        fields = ('uid', 'created_at', 'quantity_questions', 'time', 'user')


class RankingTestSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)

    def get_user(self, obj):
        return UserInListFollowSerializer(obj.user_university.user).data

    class Meta:
        model = ChallengeTest
        fields = ('uid', 'created_at', 'time', 'goods', 'bads', 'blanks', 'user')
