from .views import ListCreateCommentAPI, CreateAnswerAPI, ListCreateErrorAPI
from django.conf.urls import url

urlpatterns = [
    url(r'^questions/(?P<uid>\w+)/errors/$', ListCreateErrorAPI.as_view()),
    url(r'^questions/(?P<uid>\w+)/comments/$', ListCreateCommentAPI.as_view()),
    url(r'^comments/(?P<uid>\w+)/$', CreateAnswerAPI.as_view()),

]
