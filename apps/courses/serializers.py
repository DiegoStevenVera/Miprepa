# coding=utf-8
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta
from ..challenges.models import CountQuestion
from miprepa.settings.base import EXPERIENCE_FIRST, EXPERIENCE_SECOND, EXPERIENCE_OTHER

from miprepa.utils.fields import UidRelatedField
from .models import Course, Topic, Question


class ListCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('uid', 'name', 'logo', 'identify', 'cover')


class ListTopicSerializer(serializers.ModelSerializer):
    number_questions = serializers.SerializerMethodField()

    def get_number_questions(self, obj):
        return obj.questions.all().count()

    class Meta:
        model = Topic
        fields = ('uid', 'name', 'number_questions', 'order_customize', 'desc_order_customizer', 'frequency')


class DetailCourseSerializer(serializers.ModelSerializer):
    topics = ListTopicSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ('uid', 'name', 'logo', 'identify', 'topics', 'cover')


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('uid', 'name')


class ListQuestionSerializer(serializers.ModelSerializer):
    options = serializers.DictField(read_only=True)
    bookmarked = serializers.SerializerMethodField(read_only=True)
    feedback = serializers.SerializerMethodField(read_only=True)
    topic = UidRelatedField(queryset=Topic.objects.all(), representation_serializer=TopicSerializer)
    experience = serializers.SerializerMethodField(read_only=True)
    errors = serializers.SerializerMethodField(read_only=True)

    def get_experience(self, obj):
        if self.context.get('user_university'):
            count_question = CountQuestion.objects.filter(user_university=self.context.get('user_university'),
                                                          question=obj).first()
            if count_question:
                if count_question.count == 0:
                    return EXPERIENCE_FIRST
                elif count_question.count == 1:
                    return EXPERIENCE_SECOND
                else:
                    return EXPERIENCE_OTHER
            else:
                return EXPERIENCE_FIRST
        else:
            return None

    def get_feedback(self, obj):
        return obj.feedback.count()

    def get_errors(self, obj):
        return obj.errors.count()

    def get_bookmarked(self, obj):
        request = self.context.get('request')
        if request:
            user = getattr(request, 'user')
            return user.id in obj.bookmarked_by
        return False

    class Meta:
        model = Question
        fields = ('uid', 'date_show', 'year_show', 'text', 'options', 'bookmarked', 'topic', 'verified',
                  'source_number', 'feedback', 'experience', 'errors')


class ListQuestionInTopicSerializer(serializers.ModelSerializer):
    options = serializers.DictField(read_only=True)

    class Meta:
        model = Question
        fields = ('uid', 'date_show', 'year_show', 'text', 'options')


class RetrieveTopicSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    def get_questions(self, obj):
        queryset = obj.questions.all().order_by("?")[:8]
        return ListQuestionSerializer(queryset, many=True, context=self.context).data

    class Meta:
        model = Topic
        fields = ('uid', 'name', 'order_customize', 'desc_order_customizer', 'frequency', 'questions')


class ACreateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('uid', 'text', 'options', 'date_show', 'topic')


class CreateQuestionSerializer(serializers.ModelSerializer):
    option_a = serializers.CharField(write_only=True)
    option_b = serializers.CharField(write_only=True)
    option_c = serializers.CharField(write_only=True)
    option_d = serializers.CharField(write_only=True)
    option_e = serializers.CharField(write_only=True)
    answer = serializers.CharField(write_only=True)
    options = serializers.DictField(read_only=True)

    def create(self, validated_data):
        raise_errors_on_nested_writes('create', self, validated_data)

        ModelClass = self.Meta.model

        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            options = {'a': validated_data.get('option_a'), 'b': validated_data.get('option_b'),
                       'c': validated_data.get('option_c'), 'd': validated_data.get('option_d'),
                       'e': validated_data.get('option_e')}
            dictionary = {'options': options, 'answer': validated_data.get('answer')}
            instance = ModelClass.objects.create(
                text=validated_data.get('text'), options=dictionary,
                topic=validated_data.get('topic'),
                date_show=validated_data.get('date_show'),
                year_show=validated_data.get('year_show'),
                argument_answer=validated_data.get('argument_answer'),
                source_number=validated_data.get('source_number')
            )
        except TypeError as exc:
            msg = (
                'Got a `TypeError` when calling `%s.objects.create()`. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                '`%s.objects.create()`. You may need to make the field '
                'read-only, or override the %s.create() method to handle '
                'this correctly.\nOriginal exception text was: %s.' %
                (
                    ModelClass.__name__,
                    ModelClass.__name__,
                    self.__class__.__name__,
                    exc
                )
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                setattr(instance, field_name, value)

        return instance

    class Meta:
        model = Question
        fields = (
            'id', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'option_e', 'date_show', 'year_show',
            'answer', 'argument_answer', 'topic', 'options', 'source_number')


class ListQuestionALLSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('uid', 'text', 'options', 'date_show', 'year_show', 'argument_answer')


class ListTopicALLSerializer(serializers.ModelSerializer):
    questions = ListQuestionALLSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ('uid', 'name', 'order_customize', 'desc_order_customizer', 'frequency', 'questions')


class DetailCourseALLSerializer(serializers.ModelSerializer):
    topics = ListTopicALLSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ('uid', 'name', 'logo', 'identify', 'topics', 'cover')


class ListTopicQuestionsBookmarkedSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    def get_questions(self, obj):
        serializer = ListQuestionInTopicSerializer(
            obj.questions.filter(bookmarked_by__contains=[self.context.get('request').user.id]),
            many=True)
        return serializer.data

    class Meta:
        model = Topic
        fields = ('uid', 'name', 'questions')


class ListCoursesBookmarkedSerializer(serializers.ModelSerializer):
    topics = serializers.SerializerMethodField()

    # courses = serializers.SerializerMethodField()

    # def get_courses(self, obj):
    # courses = []
    # for c in self.context.get('view').get_courses():
    # courses.append({"id": c.id, "name": c.name})
    #     return courses

    def get_topics(self, obj):
        topics_id = Question.objects.filter(bookmarked_by__contains=[self.context.get('request').user.id]).values_list(
            'topic_id', flat=True)
        serializer = ListTopicQuestionsBookmarkedSerializer(obj.topics.filter(id__in=topics_id), many=True,
                                                            context={'request': self.context.get('request')})
        return serializer.data

    class Meta:
        model = Course
        fields = ('uid', 'name', 'topics', 'cover')


class ListCoursesMarkedSerializer(serializers.ModelSerializer):
    marked = serializers.SerializerMethodField()

    def get_marked(self, obj):
        is_marked = False
        count = 0
        for topic in obj.topics.all():
            count += topic.questions.filter(bookmarked_by__contains=[self.context.get('request').user.id]).count()
        if count > 0:
            is_marked = True
        return {"count": count, "is_marked": is_marked}

    class Meta:
        model = Course
        fields = ('uid', 'name', 'identify', 'marked', 'cover')
