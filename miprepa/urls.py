"""traina URL Configuration
def perform_update(self, serializer):
        serializer.save()
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url, static
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('apps.accounts.urls', namespace='accounts', app_name='accounts')),
    url(r'^', include('apps.courses.urls', namespace='courses', app_name='courses')),
    url(r'^', include('apps.badges.urls', namespace='badges', app_name='badges')),
    url(r'^', include('apps.universities.urls', namespace='universities', app_name='universities')),
    url(r'^', include('apps.challenges.urls', namespace='challenges', app_name='challenges')),
    url(r'^', include('apps.feedback.urls', namespace='feedback', app_name='feedback')),
    # url(r'^', include('apps.notifications.urls', namespace='notifications', app_name='notifications')),
    url(r'^docs/', include('rest_framework_docs.urls')),
]

if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
