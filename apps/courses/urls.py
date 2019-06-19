from django.conf.urls import url

from .views import (ListCoursesAPI, ListTopicAPI, ListQuestionAPI, CreateQuestionAPI, DetailCourseAPI,
                    DetailTopicAPI, BookmarkQuestionAPI, ListQuestionByCourseAPI, ListQuestionMarkedCourseAPI,
                    CountQuestionsTopicAPI, ListAllQuestionsAPI, ListCoursesMarkedAPI)

urlpatterns = [
    url(r'^enroll/(?P<uid>\w+)/courses/$', ListCoursesAPI.as_view(), name="courses"),
    url(r'^courses/(?P<uid>\w+)/$', DetailCourseAPI.as_view(), name="course-detail"),
    url(r'^courses/(?P<uid>\w+)/topics/$', ListTopicAPI.as_view(), name="topics"),
    url(r'^courses/topics/(?P<uid>\w+)/$', DetailTopicAPI.as_view(), name="topic-retrieve"),
    url(r'^courses/(?P<uid>\w+)/counts/$', CountQuestionsTopicAPI.as_view(), name="topic-counts-questions"),
    url(r'^courses/topics/(?P<uid>\w+)/questions/$', ListQuestionAPI.as_view(), name="questions"),
    url(r'^courses/(?P<uid>\w+)/questions/$', ListQuestionByCourseAPI.as_view(), name="questions"),
    url(r'^questions/(?P<uid>\w+)/bookmark/$', BookmarkQuestionAPI.as_view(), name="bookmark-question"),
    url(r'questions/bookmark/courses/(?P<uid>\w+)/$', ListQuestionMarkedCourseAPI.as_view(),
        name="bookmark-question-list"),
    url(r'^courses/bookmarks/$', ListCoursesMarkedAPI.as_view(),
        name="bookmark-courses-list"),
    url(r'^courses/questions/create/$', CreateQuestionAPI.as_view(), name="create_question"),
    url(r'^courses/questions/all/$', ListAllQuestionsAPI.as_view(), name="list-question-all"),
]
