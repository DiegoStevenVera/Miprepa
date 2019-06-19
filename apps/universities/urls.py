from .views import ListUniversitiesAPI, ListKnowledgeAreaAPI
from django.conf.urls import url

urlpatterns = [
    url(r'^universities/$', ListUniversitiesAPI.as_view(), name="universities"),
    url(r'^knowledge-areas/$', ListKnowledgeAreaAPI.as_view(), name="knowledge-areas"),
]
