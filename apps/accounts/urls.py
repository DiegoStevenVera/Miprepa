from rest_framework_jwt.views import RefreshJSONWebToken
from django.conf.urls import url
from .views import (RetrieveUpdateUserProfileAPI, UserRegisterAPI, csv_report_files, FollowUserAPI, UnFollowUserAPI,
                    RegisterGCMDeviceAPI, OwnObtainJSONWebToken, FacebookMobileLoginAPI, ValidateUserDataAPI,
                    ListRegisterUserUniversityAPI, RegisterCareerUniversityAPI, RetriveUserUniversityAPIView,
                    ListMeBadgesAPI, SearchUserAPI, MeStatisticsAPI, MeReportAPI, RetrievePasswordView)

urlpatterns = [
    url(r'^token-auth/$', OwnObtainJSONWebToken.as_view(), name='token-auth'),
    url(r'^token-auth/(?P<backend>[^/]+)/$', FacebookMobileLoginAPI.as_view(), name='facebook-mobile-login'),
    url(r'^token-refresh/$', RefreshJSONWebToken.as_view()),
    url(r'^register/$', UserRegisterAPI.as_view()),
    url(r'^change-password/$', RetrievePasswordView.as_view()),
    url(r'^me/$', RetrieveUpdateUserProfileAPI.as_view()),
    url(r'^user_report/$', csv_report_files),
    url(r'^universities/users/$', ListRegisterUserUniversityAPI.as_view()),
    url(r'^universities/enroll/(?P<uid>\w+)/users/$', SearchUserAPI.as_view()),
    url(r'^universities/enroll/(?P<uid>\w+)/$', RegisterCareerUniversityAPI.as_view()),
    url(r'^universities/enroll/(?P<uid>\w+)/me/$', RetriveUserUniversityAPIView.as_view()),
    url(r'^universities/enroll/(?P<uid>\w+)/me/statistics/$', MeStatisticsAPI.as_view()),
    url(r'^universities/enroll/(?P<uid>\w+)/me/report/$', MeReportAPI.as_view()),
    url(r'^universities/enroll/(?P<uid>\w+)/me/follows/$', FollowUserAPI.as_view()),
    url(r'^universities/enroll/(?P<uid>\w+)/me/badges/$', ListMeBadgesAPI.as_view()),
    url(r'^universities/enroll/me/follows/(?P<uid>\w+)/$', UnFollowUserAPI.as_view()),
    url(r'^me/devices/gcm/$', RegisterGCMDeviceAPI.as_view()),
    url(r'^validate/$', ValidateUserDataAPI.as_view()),

]
