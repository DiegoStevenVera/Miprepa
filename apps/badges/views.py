# coding=utf-8
from django.conf import settings
from django.db.models import Q
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from apps.universities.models import University

from .models import Level, Badge
from .serializers import SerializerLevel, BadgeSerializer


class ListLevelAPIVIew(ListAPIView):
    serializer_class = SerializerLevel
    permission_classes = (IsAuthenticated,)
    queryset = Level.objects.filter(is_enabled=True)


class ListBadgesAPI(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BadgeSerializer

    def get_queryset(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        university = get_object_or_404(University.objects.filter(is_enabled=True), id=id)
        return (university.badges.filter(is_enabled=True) | Badge.objects.filter(is_enabled=True,
                                                                                 all_universities=True)).distinct()
