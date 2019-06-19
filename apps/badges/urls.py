from .views import ListLevelAPIVIew, ListBadgesAPI

__author__ = 'carlos'
from django.conf.urls import url

urlpatterns = [
    url(r'^levels/$', ListLevelAPIVIew.as_view(), name="list-levels"),
    url(r'^universities/(?P<uid>\w+)/badges/$', ListBadgesAPI.as_view(), name="list-badge"),
]
