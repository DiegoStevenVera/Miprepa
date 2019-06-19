from django.conf.urls import url
from .views import UpdateNotificationAPI

urlpatterns = [
    url(r'^notifications/(?P<uid>\w+)/$', UpdateNotificationAPI.as_view(), name="update-notifications"),
]
