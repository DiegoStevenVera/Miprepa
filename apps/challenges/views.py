from django.conf import settings
from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView, get_object_or_404, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..accounts.authentication import ExpiringTokenAuthentication
from .models import ChallengeTimeOut, ChallengeSurvival, ChallengeTest, CountQuestion, History
from .pagination import TenPagination
from .serializers import ChallengeTimeOutSerializer, ChallengeSurvivalSerializer, ChallengeTestSerializer, \
    ListChallengeSurvivalSerializer, ListChallengeTestSerializer, \
    RankingTimeOutSerializer, RankingSurvivalSerializer, RankingTestSerializer
from ..courses.models import Question
from .tasks import create_historys_survival, create_historys_test, create_historys_timeout
from miprepa.settings.base import LIST_RANKING, EXPERIENCE_FIRST, EXPERIENCE_SECOND, EXPERIENCE_OTHER


class CreateChallengeTimeOutAPI(ListCreateAPIView):  # List and create
    permission_classes = (IsAuthenticated,)
    serializer_class = ChallengeTimeOutSerializer
    pagination_class = TenPagination

    def get_uu(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return get_object_or_404(self.request.user.user_universities.all(), id=id)

    def get_queryset(self):
        user_university = self.get_uu()
        return user_university.challengestimeout.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,
                                         context={'request': request, 'user_university': self.get_uu()})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user_university = self.get_uu()
        queryset = Question.objects.order_by('?')[:20].values_list('id', flat=True)
        serializer.save(user_university=user_university, questions_requested=list(queryset))


class RetrievePageChallengeTimeOutAPI(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChallengeTimeOutSerializer
    queryset = ChallengeTimeOut.objects.all()

    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        return super(RetrievePageChallengeTimeOutAPI, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return get_object_or_404(self.get_queryset(), id=id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        page = request.data.get("page")
        page = int(page) if page else 1
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        challenge = self.perform_update(serializer)
        questions = challenge.questions_requested
        if 20 * page > len(questions):
            queryset = Question.objects.all()
            queryset = queryset.exclude(id__in=challenge.questions_requested).order_by('?')[:20].values_list('id',
                                                                                                             flat=True)
            challenge.questions_requested = list(set(challenge.questions_requested + list(queryset)))
            challenge.save()
        serializer = self.get_serializer(challenge, context={"page": page})
        return Response(serializer.data)

    def perform_update(self, serializer):
        if serializer.validated_data.get("questions_save"):
            q_saved = serializer.validated_data.get("questions_save")
            serializer.instance.questions_saved = list(serializer.instance.questions_saved + list(q_saved))
            corrects = 0
            for q in q_saved:
                if q.get('correct') == 'True':
                    corrects += 1
            serializer.instance.quantity_questions += corrects
            challenge = serializer.save()
            create_historys_timeout.delay(self.request.user.id, q_saved, challenge.id)
            return challenge
        else:
            return serializer.save()


class CreateChallengeSurvivalAPI(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChallengeSurvivalSerializer
    pagination_class = TenPagination

    def get_uu(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return get_object_or_404(self.request.user.user_universities.all(), id=id)

    def get_queryset(self):
        user_university = self.get_uu()
        return user_university.challengessurvival.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ListChallengeSurvivalSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ListChallengeSurvivalSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,
                                         context={'request': request, 'user_university': self.get_uu()})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user_university = self.get_uu()
        queryset = Question.objects.order_by('?')[:20].values_list('id', flat=True)
        serializer.save(user_university=user_university, questions_requested=list(queryset))


#
# class ListChallengesSurvivalAPI(ListAPIView):
#     permission_classes = (IsAuthenticated,)
#     serializer_class = ListChallengeSurvivalSerializer
#     pagination_class = TenPagination
#
#     def get_queryset(self):
#         return self.request.user.challengessurvival.all()


class RetrievePageChallengeSurvivalAPI(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChallengeSurvivalSerializer
    queryset = ChallengeSurvival.objects.all()

    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        return super(RetrievePageChallengeSurvivalAPI, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return get_object_or_404(self.get_queryset(), id=id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        page = request.data.get("page")
        page = int(page) if page else 1
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        challenge = self.perform_update(serializer)
        questions = challenge.questions_requested
        if 20 * page > len(questions):
            queryset = Question.objects.all()
            queryset = queryset.exclude(id__in=challenge.questions_requested).order_by('?')[:20].values_list('id',
                                                                                                             flat=True)
            challenge.questions_requested = list(set(challenge.questions_requested + list(queryset)))
            challenge.save()
        serializer = self.get_serializer(challenge, context={"page": page})
        return Response(serializer.data)

    def perform_update(self, serializer):
        if serializer.validated_data.get("questions_save"):
            q_saved = serializer.validated_data.get("questions_save")
            if serializer.validated_data.get('time'):
                serializer.instance.time = serializer.validated_data.get('time')
            serializer.instance.questions_saved = list(serializer.instance.questions_saved + list(q_saved))
            corrects = 0
            for q in q_saved:
                if q.get('correct') == 'True':
                    corrects += 1
            serializer.instance.quantity_questions += corrects
            challenge = serializer.save()
            create_historys_survival.delay(q_saved, challenge.id)
            return challenge
        else:
            return serializer.save()


class CreateChallengeTestAPI(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChallengeTestSerializer
    pagination_class = TenPagination

    def get_uu(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return get_object_or_404(self.request.user.user_universities.all(), id=id)

    def get_queryset(self):
        user_university = self.get_uu()
        return user_university.challengestest.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ListChallengeTestSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ListChallengeTestSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,
                                         context={'request': request, 'user_university': self.get_uu()})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user_university = self.get_uu()
        courses = serializer.validated_data.get('courses_id') if serializer.validated_data.get('courses_id') else []
        query = Question.objects.all()
        questions = []
        for course in courses:
            uid = course.get('id')
            decoded = settings.HASHIDS.decode(uid)
            course_id = decoded[0] if decoded else None
            questions.append({"course": course.get('id'),
                              "questions_id": list(query.filter(topic__course__id=course_id).order_by('?')[
                                                   0:course.get('quantity')].values_list('id', flat=True))}
                             )
        serializer.save(user_university=user_university, questions_requested=questions)


#
# class ListChallengesTestAPI(ListAPIView):
#     permission_classes = (IsAuthenticated,)
#     serializer_class = ListChallengeTestSerializer
#     pagination_class = TenPagination
#
#     def get_queryset(self):
#         return self.request.user.challengestest.all()


class UpdateChallengeTestAPI(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChallengeTestSerializer
    queryset = ChallengeTest.objects.all()

    def get_object(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return get_object_or_404(self.get_queryset(), id=id)

    def perform_update(self, serializer):
        if serializer.validated_data.get("questions_save") and serializer.validated_data.get('time'):
            q_saved = serializer.validated_data.get("questions_save")
            serializer.instance.time = serializer.validated_data.get('time', 0)
            serializer.instance.questions_saved = list(q_saved)
            for q in q_saved:
                if q.get('correct') == 'True':
                    serializer.instance.goods += 1
                elif q.get('correct') == 'False':
                    serializer.instance.bads += 1
                else:
                    serializer.instance.blanks += 1
            challenge = serializer.save()
            create_historys_test.delay(q_saved, challenge.id)
            return challenge
        else:
            return serializer.save()


# class ListChallengesTimeOutAPI(ListAPIView):
#     permission_classes = (IsAuthenticated,)
#     serializer_class = ListChallengeTimeOutSerializer
#     pagination_class = TenPagination
#
#     def get_queryset(self):
#         uid = self.kwargs.get("uid")
#         decoded = settings.HASHIDS.decode(uid)
#         id = decoded[0] if decoded else None
#         user_university = get_object_or_404(self.request.user.user_universities.all(), id=id)
#         return user_university.challengestimeout.all()






class RankingTimeOutAPI(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RankingTimeOutSerializer

    def get_uu(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return get_object_or_404(self.request.user.user_universities.all(), id=id)

    def get_queryset(self):
        user_university = self.get_uu()
        if self.request.query_params.get('q') == 'general':
            query = ChallengeTimeOut.objects.filter(user_university__knowledge_area=user_university.knowledge_area)
            ids = query.order_by('user', '-quantity_questions').distinct('user').values_list('id', flat=True)
            general = query.filter(id__in=ids).order_by('-quantity_questions')
            i = general.filter(user=self.request.user).first()
            index = list(general.values_list('id', flat=True)).index(i.id)
            return general[index - LIST_RANKING:index + LIST_RANKING] \
                if index - LIST_RANKING > 0 else general[0:index + LIST_RANKING]

        else:
            users = list(set(user_university.follows + [self.request.user.id]))
            query = ChallengeTimeOut.objects.filter(user__in=users,
                                                    user_university__knowledge_area=user_university.knowledge_area)
            ids = query.filter(user__in=users).order_by('user', '-quantity_questions').distinct('user'). \
                values_list('id', flat=True)
            return query.filter(id__in=ids).order_by('-quantity_questions')


class RankingSurvivalAPI(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RankingSurvivalSerializer

    def get_uu(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return get_object_or_404(self.request.user.user_universities.all(), id=id)

    def get_queryset(self):
        user_university = self.get_uu()
        if self.request.query_params.get('q') == 'general':
            query = ChallengeSurvival.objects.filter(user_university__knowledge_area=user_university.knowledge_area)
            ids = query.order_by('user', '-quantity_questions', 'time').distinct(
                'user').values_list('id', flat=True)
            general = query.filter(id__in=ids).order_by('-quantity_questions', 'time')
            i = general.filter(user=self.request.user).first()
            index = list(general.values_list('id', flat=True)).index(i.id)
            return general[index - LIST_RANKING:index + LIST_RANKING] \
                if index - LIST_RANKING > 0 else general[0:index + LIST_RANKING]
        else:
            users = list(set(user_university.follows + [self.request.user.id]))
            query = ChallengeTimeOut.objects.filter(user__in=users,
                                                    user_university__knowledge_area=user_university.knowledge_area)
            ids = query.filter(user__in=users).order_by('user', '-quantity_questions', 'time').distinct(
                'user').values_list('id', flat=True)
            return query.filter(id__in=ids).order_by('-quantity_questions', 'time')


class RankingTestAPI(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RankingTestSerializer

    def get_uu(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return get_object_or_404(self.request.user.user_universities.all(), id=id)

    def get_queryset(self):
        user_university = self.get_uu()
        if self.request.query_params.get('q') == 'general':
            query = ChallengeTest.objects.filter(user_university__knowledge_area=user_university.knowledge_area)
            ids = query.order_by('user', '-goods', 'bads', 'blanks', 'time').distinct('user').values_list('id',
                                                                                                          flat=True)
            general = query.filter(id__in=ids).order_by('-goods', 'bads', 'blanks', 'time')
            i = general.filter(user=self.request.user).first()
            index = list(general.values_list('id', flat=True)).index(i.id)
            return general[index - LIST_RANKING:index + LIST_RANKING] \
                if index - LIST_RANKING > 0 else general[0:index + LIST_RANKING]

        else:
            users = list(set(self.request.user.follows + [self.request.user.id]))
            query = ChallengeTest.objects.filter(user__in=users,
                                                 user_university__knowledge_area=user_university.knowledge_area)
            ids = query.filter(user__in=users).order_by('user', '-goods', 'bads', 'blanks', 'time').distinct(
                'user').values_list('id', flat=True)
            return query.filter(id__in=ids).order_by('-goods', 'bads', 'blanks', 'time')


class CorrectPracticeAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        uu_id = decoded[0] if decoded else None
        user_university = get_object_or_404(self.request.user.user_universities.all(), id=uu_id)
        markeds = self.request.data.get('questions_saved')
        for marked in markeds:
            uid = marked.get('id')
            decoded = settings.HASHIDS.decode(uid)
            q_id = decoded[0] if decoded else None
            question = Question.objects.get(id=q_id)
            count_question, e = CountQuestion.objects.get_or_create(user_university=user_university, question=question)
            exp = 0
            if marked.get('correct') == 'True':
                q_status = History.Type.correct.name
                count_question.count += 1
                count_question.save()
                if count_question.count == 0:
                    user_university.experience += EXPERIENCE_FIRST
                    exp = EXPERIENCE_FIRST
                elif count_question.count == 1:
                    user_university.experience += EXPERIENCE_SECOND
                    exp = EXPERIENCE_SECOND
                else:
                    user_university.experience += EXPERIENCE_OTHER
                    exp = EXPERIENCE_OTHER
                user_university.save()



            elif marked.get('correct') == 'False':
                q_status = History.Type.wrong.name
            else:
                q_status = History.Type.blank.name
            History.objects.create(user_university=user_university, question=question,
                                   answer=marked.get('marked'), status=q_status, experience=exp)
        return Response(status=status.HTTP_201_CREATED)
