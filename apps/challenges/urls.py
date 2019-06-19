from django.conf.urls import url

from .views import CreateChallengeTimeOutAPI, RetrievePageChallengeTimeOutAPI, CreateChallengeSurvivalAPI, \
    RetrievePageChallengeSurvivalAPI, CreateChallengeTestAPI, \
    UpdateChallengeTestAPI, RankingTimeOutAPI, RankingSurvivalAPI, RankingTestAPI, CorrectPracticeAPI

urlpatterns = [
    url(r'^enroll/(?P<uid>\w+)/challenges/timeouts/ranking/$', RankingTimeOutAPI.as_view(),
        name="ranking_challenge_timeout"),
    url(r'^enroll/(?P<uid>\w+)/challenges/timeouts/$', CreateChallengeTimeOutAPI.as_view(),
        name="create_challenge_timeout"),
    url(r'^enroll/challenges/timeouts/(?P<uid>\w+)/$', RetrievePageChallengeTimeOutAPI.as_view(),
        name="retrieve_update_challenge_timeout"),

    url(r'^enroll/(?P<uid>\w+)/challenges/survivals/ranking/$', RankingSurvivalAPI.as_view(),
        name="ranking_challenge_survival"),
    url(r'^enroll/(?P<uid>\w+)/challenges/survivals/$', CreateChallengeSurvivalAPI.as_view(),
        name="create_challenge_survival"),
    url(r'^enroll/challenges/survivals/(?P<uid>\w+)/$', RetrievePageChallengeSurvivalAPI.as_view(),
        name="retrieve_update_challenge_survival"),

    url(r'^enroll/(?P<uid>\w+)/challenges/tests/ranking/$', RankingTestAPI.as_view(), name="ranking_test_survival"),
    url(r'^enroll/(?P<uid>\w+)/challenges/tests/$', CreateChallengeTestAPI.as_view(),
        name="create_test_survival"),
    url(r'^enroll/challenges/tests/(?P<uid>\w+)/$', UpdateChallengeTestAPI.as_view(),
        name="retrieve_update_test_survival"),
    url(r'^enroll/(?P<uid>\w+)/practice/$', CorrectPracticeAPI.as_view(),
        name="practices")
]
