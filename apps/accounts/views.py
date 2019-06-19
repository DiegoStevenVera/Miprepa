import csv
import hashlib
import base64
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import user_logged_in, get_user
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from push_notifications.models import GCMDevice
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView, CreateAPIView, ListAPIView, \
    get_object_or_404, ListCreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from social.apps.django_app.utils import load_strategy, load_backend, psa
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework import filters
from django.core.mail import send_mail
from apps.badges.serializers import BadgeSerializer
from apps.challenges.models import History
from apps.universities.models import University
from .models import User, UserUniversity
from .pagination import TenUserPagination, PaginateBy50
from .serializers import (UserSerializer, RegisterUserSerializer, UserFollowSerializer, GCMDeviceSerializer,
                          OwnJSONWebTokenSerializer, FacebookLoginSerializer, UserInListFollowSerializer,
                          ValidateUserDataSerializer,
                          UserUniversitySerializer, CreateUserUniversitySerializer, UpdateUserUniversitySerializer,
                          RetrieveUserUniversitySerializer, UserSearchSerializer, UserUniversitySearchSerializer,
                          RetrievePasswordSerializer)


class RetrieveUpdateUserProfileAPI(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserRegisterAPI(CreateAPIView):
    """{gender: m | f, birthday: aaaa-mm-dd}"""
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = RegisterUserSerializer

    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        return super(UserRegisterAPI, self).dispatch(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = serializer.save()
        if serializer.validated_data.get('access_token'):
            self.request.social_strategy = load_strategy(self.request)
            if not hasattr(self.request, 'strategy'):
                self.request.strategy = self.request.social_strategy
                self.request.backend = load_backend(self.request.social_strategy, "facebook",
                                                    reverse("accounts:token-auth"))
            self.request.social_strategy = load_strategy(self.request)
            self.request.backend = load_backend(self.request.social_strategy, 'facebook', None)
            self.request.backend.do_auth(serializer.validated_data.get("access_token"), None, user=user, is_new=True)
        return user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not User.objects.filter(email=serializer.validated_data.get('email')).exists():
            if not User.objects.filter(nickname=serializer.validated_data.get('nickname')).exists():
                user = self.perform_create(serializer)
                payload = jwt_payload_handler(user)
                return Response({'token': jwt_encode_handler(payload)})
            else:
                return Response({"detail": 'Nickname ya resgistrado'}, status=status.HTTP_306_RESERVED)
        else:
            return Response({"detail": 'Correo ya resgistrado'}, status=status.HTTP_303_SEE_OTHER)


class RetrievePasswordView(generics.GenericAPIView):
    serializer_class = RetrievePasswordSerializer
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        email = vd.get("email")
        new_password = vd.get("password")
        user = get_object_or_404(User, email=email)
        user.set_password(new_password)
        user.save()
        subject = 'MiPrepa'
        message = 'Hi '+user.first_name+'\nYour new password is: '+new_password+'\nBe careful next time :)'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]

        send_mail(subject, message, email_from, recipient_list)
        return Response({"detail": "OK"}, status=status.HTTP_200_OK)


class ValidateUserDataAPI(generics.GenericAPIView):
    serializer_class = ValidateUserDataSerializer
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "OK"}, status=status.HTTP_200_OK)


def csv_report_files(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="traina_emails.csv"'
    writer = csv.writer(response)
    headers = ['name']
    writer.writerow(headers)

    emails = User.objects.exclude(email='').values_list('email', flat=True)
    for url in emails:
        row = []
        for field in headers:
            if field in headers:
                val = url
                if callable(val):
                    val = val()
                row.append(val)
        writer.writerow([s.encode("utf-8") for s in row])
    return response


class RetriveUserUniversityAPIView(RetrieveAPIView):
    serializer_class = RetrieveUserUniversitySerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = TenUserPagination

    def get_object(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return self.request.user.user_universities.filter(id=id).prefetch_related(
            'knowledge_area').prefetch_related('badges').first()


class FollowUserAPI(ListAPIView, GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserFollowSerializer
    pagination_class = PaginateBy50

    def get_uu(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return self.request.user.user_universities.filter(id=id).first()

    def get_queryset(self):
        return User.objects.filter(id__in=self.get_uu().follows)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserInListFollowSerializer(page, many=True,
                                                    context={'request': request,
                                                             'uu': self.get_uu().desired_university})
            return self.get_paginated_response(serializer.data)

        serializer = UserInListFollowSerializer(queryset, many=True,
                                                context={'request': request,
                                                         'uu': self.get_uu().desired_university})
        return Response(serializer.data)

    # def get_serializer_class(self):
    #     return self.serializer_class if self.request.method == "post" else UserInListFollowSerializer

    def post(self, request, *args, **kwargs):
        user_university = self.get_uu()
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        new_follows = list(set(user_university.follows + [serializer.validated_data.get("uid_user").id]))
        user_university.follows = new_follows
        user_university.save(update_fields=["follows"])
        return Response({"follows": new_follows}, status=status.HTTP_201_CREATED)


class UnFollowUserAPI(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        uid_user = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid_user)
        id_user = decoded[0] if decoded else None
        follow = get_object_or_404(User, id=id_user)
        user = self.request.user
        user.follows.remove(follow.id)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OwnObtainJSONWebToken(generics.GenericAPIView):
    serializer_class = OwnJSONWebTokenSerializer
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_logged_in.send(sender=serializer.validated_data.get("user").__class__, request=request,
                            user=serializer.validated_data.get("user"))
        response_data = {"token": serializer.validated_data.get('token')}
        return Response(response_data)


class FacebookMobileLoginAPI(OwnObtainJSONWebToken):
    serializer_class = FacebookLoginSerializer

    @method_decorator(psa('accounts:facebook-mobile-login'))
    def post(self, request, *args, **kwargs):
        return super(FacebookMobileLoginAPI, self).post(request, *args, **kwargs)


class RegisterGCMDeviceAPI(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GCMDeviceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        registration_id = serializer.validated_data.get("registration_id")
        device = GCMDevice.objects.filter(registration_id=registration_id).first()
        if device:
            device.user = self.request.user
            device.name = vd.get("name")
            device.device_id = vd.get("device_id")
            device.save()
            return Response(GCMDeviceSerializer(device).data, status=status.HTTP_201_CREATED)
        else:
            serializer.save(user=self.request.user)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ListRegisterUserUniversityAPI(ListCreateAPIView):  # Lista y crea los modelos UserUniversity del usuario
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateUserUniversitySerializer

    def get_queryset(self):
        return self.request.user.user_universities.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserUniversitySerializer(page, many=True, request=request)
            return self.get_paginated_response(serializer.data)

        serializer = UserUniversitySerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        if obj:
            serializer = UserUniversitySerializer(obj, context={'request': request})
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({'detail': 'Usuario ya esta registrado a la universidad'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

    def perform_create(self, serializer):
        user = self.request.user
        if not UserUniversity.objects.filter(desired_university=serializer.validated_data.get('desired_university'),
                                             user=user).exists():
            if user.is_new:
                user.is_new = False
                user.save()
            return serializer.save(user=user)
        else:
            return None


class RegisterCareerUniversityAPI(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserUniversitySerializer

    def post(self, request, *args, **kwargs):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        user_university = get_object_or_404(self.request.user.user_universities.all(), id=id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_university.knowledge_area = serializer.validated_data.get('knowledge_area',
                                                                       user_university.knowledge_area)
        user_university.first_option = serializer.validated_data.get('first_option', user_university.first_option)
        user_university.save()
        return Response(UserUniversitySerializer(user_university, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        user_university = get_object_or_404(self.request.user.user_universities.all(), id=id)
        return Response(UserUniversitySerializer(user_university, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class ListMeBadgesAPI(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BadgeSerializer

    def get_queryset(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        user_university = get_object_or_404(self.request.user.user_universities.all().prefetch('badges'), id=id)
        return user_university.badges.filter(is_enabled=True)


class SearchUserAPI(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserUniversitySearchSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('user__first_name', 'user__last_name', 'user__nickname')

    def get_queryset(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        user_university = get_object_or_404(self.request.user.user_universities.all(), id=id)
        return UserUniversity.objects.filter(desired_university=user_university.desired_university).select_related(
            'user')


class MeStatisticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        user_university = get_object_or_404(self.request.user.user_universities.all(), id=id)
        histories = user_university.history.all()
        good_total = histories.filter(status=History.Type.correct.name).count()
        total = histories.count()
        courses = histories.filter(status=History.Type.correct.name).values('question__topic__course__name').annotate(
            Count('id')).order_by('-id__count')
        return Response({'correct_percentage': round((good_total * 100) / total, 2) if good_total > 0 else 0,
                         'total_questions': total,
                         'more_successes': courses.first().get(
                             'question__topic__course__name') if len(courses) > 0 else '-',
                         'fewer_hits': courses.last().get(
                             'question__topic__course__name') if len(courses) > 0 else '-'
                         }, status=status.HTTP_200_OK)


class MeReportAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        user_university = get_object_or_404(self.request.user.user_universities.all(), id=id)
        now = datetime.now().date()
        init_week = now - timedelta(days=7)
        days = [now - timedelta(days=x) for x in range(0, 7)]
        histories = user_university.history.filter(status=History.Type.correct.name,
                                                   created_at__range=[init_week, now])
        report = []
        exp_acu = 0

        for day in days:
            h = histories.filter(date_at=day).values('date_at').annotate(day_experience=Sum('experience'))
            if h and len(h) > 0:
                exp_acu += int(h[0].get('day_experience'))
                report.append(
                    {'experience_at': user_university.experience - exp_acu,
                     'day_experience': h[0].get('day_experience'), 'day': h[0].get('date_at').strftime("%A"),
                     'date': h[0].get('date_at').strftime("%d-%m-%y")})
            else:
                report.append(
                    {'experience_at': user_university.experience - exp_acu, 'day_experience': 0,
                     'day': day.strftime("%A"), 'date': day.strftime("%d-%m-%y")})
        return Response({'total_experience': user_university.experience, 'days': report}, status=status.HTTP_200_OK)
