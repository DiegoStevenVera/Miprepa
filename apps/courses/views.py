from django.conf import settings
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.universities.models import KnowledgeArea
from .models import Course, Topic, Question
from .serializers import (ListCourseSerializer, ListTopicSerializer, ListQuestionSerializer,
                          CreateQuestionSerializer, DetailCourseSerializer, RetrieveTopicSerializer,
                          DetailCourseALLSerializer, ListCoursesBookmarkedSerializer,
                          ListCoursesMarkedSerializer)


class DetailCourseAPI(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DetailCourseSerializer
    queryset = Course.objects.all()

    def get_object(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return get_object_or_404(self.get_queryset(), id=id)


class ListCoursesAPI(ListAPIView):  # Lista los cursos por el area inscrita (UserUniversity)
    serializer_class = ListCourseSerializer
    permission_classes = (IsAuthenticated,)
    # queryset = Course.objects.filter(is_enabled=True)

    def get_queryset(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        user_university = get_object_or_404(self.request.user.user_universities.all().prefetch_related(
            Prefetch('knowledge_area',
                     queryset=KnowledgeArea.objects.filter(is_enabled=True).prefetch_related('courses'))
        ), id=id)
        return user_university.knowledge_area.courses.filter(is_enabled=True)


class DetailTopicAPI(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RetrieveTopicSerializer
    queryset = Topic.objects.all()

    def get_object(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return get_object_or_404(self.get_queryset(), id=id)


class ListTopicAPI(ListAPIView):
    serializer_class = ListTopicSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        course = get_object_or_404(Course.objects.filter(is_enabled=True), id=id)
        return course.topics.filter(is_enabled=True).order_by('-name')


class ListQuestionAPI(ListAPIView):
    serializer_class = ListQuestionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        topic = get_object_or_404(Topic, id=id)
        exclude = [int(x) for x in self.request.GET.get('exclude', '').split(",") if x.isdigit()]
        limit = self.request.GET.get('limit', '')
        queryset = topic.questions.exclude(id__in=exclude).order_by('?')
        if limit and limit.isdigit() and int(limit) > 0:
            queryset = queryset[:limit]
        return queryset


class BookmarkQuestionAPI(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ListQuestionSerializer

    def put(self, request, *args, **kwargs):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        question = get_object_or_404(Question, id=id)
        bookmarked_by = question.bookmarked_by
        bookmarked_by.append(self.request.user.id)
        question.bookmarked_by = list(set(bookmarked_by))
        question.save()
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        question = get_object_or_404(Question, id=id)
        bookmarked_by = question.bookmarked_by
        if self.request.user.id in bookmarked_by:
            bookmarked_by.remove(self.request.user.id)
        question.bookmarked_by = list(set(bookmarked_by))
        question.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateQuestionAPI(CreateAPIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = CreateQuestionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_201_CREATED, headers=headers)


class ListQuestionByCourseAPI(ListAPIView):
    serializer_class = ListQuestionSerializer

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return Question.objects.filter(topic__course__id=id).order_by("created_at")


class ListQuestionMarkedCourseAPI(RetrieveAPIView):
    serializer_class = ListCoursesBookmarkedSerializer

    permission_classes = (IsAuthenticated,)

    def get_object(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return get_object_or_404(Course, id=id)

    def get_courses(self):
        topics_id = Question.objects.filter(bookmarked_by__contains=[self.request.user.id]).values_list('topic_id',
                                                                                                        flat=True)
        courses_id = Topic.objects.filter(id__in=topics_id).values_list('course_id', flat=True)
        return Course.objects.filter(id__in=courses_id).order_by('name')


class ListCoursesMarkedAPI(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ListCoursesMarkedSerializer

    def get_queryset(self):
        return Course.objects.filter(is_enabled=True).order_by('name')


class CountQuestionsTopicAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = []
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        course = get_object_or_404(Course.objects.filter(is_enabled=True), id=id)
        if hasattr(course.logo, 'url'):
            url = request.build_absolute_uri(course.logo.url)
        else:
            url = None
        if hasattr(course.cover, 'url'):
            url_cover = request.build_absolute_uri(course.cover.url)
        else:
            url_cover = None
        data_course = {"uid": course.uid, "name": course.name, "cover": url_cover,
                       "identify": course.identify, "logo": url, "topics": data}
        counts=[]
        for topic in course.topics.all():
            counts = {"id": 0, "name": topic.name, "number_questions": topic.countquestions(),
                      "frequency": topic.frequency, "70": 0, "80": 0, "90": 0, "00": 0, "10": 0,
                      'uid': topic.uid,
                      '70': topic.questions.filter(year_show__lt=1980).count(),
                      "order_customize": topic.order_customize,
                      '80': topic.questions.filter(year_show__gte=1980).filter(year_show__lt=1990).count(),
                      '90': topic.questions.filter(year_show__gte=1990).filter(year_show__lt=2000).count(),
                      '00': topic.questions.filter(year_show__gte=2000).filter(year_show__lt=2010).count(),
                      '10': topic.questions.filter(year_show__gte=2010).count()}
        data.append(counts)

        return Response({"course": data_course}, status=status.HTTP_200_OK)


class ListAllQuestionsAPI(ListAPIView):
    serializer_class = DetailCourseALLSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Course.objects.all()
