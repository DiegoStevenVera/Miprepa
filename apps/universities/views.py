from django.db.models import Prefetch
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import University, KnowledgeArea
from .serializers import UniversitySerializer, KnowledgeAreaSerializer


class ListUniversitiesAPI(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UniversitySerializer
    queryset = University.objects.filter(is_enabled=True)


class ListKnowledgeAreaAPI(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = KnowledgeAreaSerializer
    queryset = KnowledgeArea.objects.filter(is_enabled=True)
