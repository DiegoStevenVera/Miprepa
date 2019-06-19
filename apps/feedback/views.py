from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..courses.models import Question
from .models import Comment, Error
from .serializers import CommentSerializer, ListCommentSerializer, AnswerSerializer, ErrorSerializer


class ListCreateCommentAPI(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        question = get_object_or_404(Question, id=id)
        serializer.save(user=self.request.user, question=question)

    def list(self, request, *args, **kwargs):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        question = get_object_or_404(Question, id=id)
        queryset = self.filter_queryset(question.feedback.all())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ListCommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ListCommentSerializer(queryset, many=True)
        return Response(serializer.data)


class CreateAnswerAPI(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AnswerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = self.perform_create(serializer)
        if comment:
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({'detail': 'Feedback cerrado'}, status=status.HTTP_303_SEE_OTHER)

    def perform_create(self, serializer):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        feedback = get_object_or_404(Comment, id=id)
        if not feedback.is_closed:
            return serializer.save(user=self.request.user, feedback=feedback)
        else:
            return None


class ListCreateErrorAPI(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ErrorSerializer

    def perform_create(self, serializer):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        question = get_object_or_404(Question, id=id)
        serializer.save(user=self.request.user, question=question)

    def get_queryset(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        question = get_object_or_404(Question, id=id)
        return question.errors.all()
