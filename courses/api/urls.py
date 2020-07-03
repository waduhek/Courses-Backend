from django.urls import path

from . import loginViews, teacherViews

app_name = 'api'

urlpatterns = [
    # Login URLs.
    path('login/', loginViews.LoginView.as_view(), name='login'),
    path('logout/', loginViews.LogoutView.as_view(), name='logout'),
    path('signup/', loginViews.SignupView.as_view(), name='signup'),
    path(
        'validate/', loginViews.ValidateSessionView.as_view(),
        name='validate'
    ),

    # Teacher URLs.
    # All courses.
    path('teacher/course/all/', teacherViews.AllCourses.as_view()),
    # Detail view of course.
    # path('teacher/course/<int:courseID>/'),
    # Update view for course.
    # path('teacher/course/update/<int:courseID>/'),
]