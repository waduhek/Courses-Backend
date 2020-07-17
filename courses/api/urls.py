from django.urls import path

from .views import course, login, teacher

app_name = 'api'

urlpatterns = [
    # Login URLs.
    path('login/', login.LoginView.as_view(), name='login'),
    path('logout/', login.LogoutView.as_view(), name='logout'),
    path('signup/', login.SignupView.as_view(), name='signup'),
    path(
        'validate/', login.ValidateSessionView.as_view(),
        name='validate'
    ),

    # Teacher URLs.
    # All courses.
    path(
        'teacher/course/all/', teacher.AllCourses.as_view(),
        name='courseAll'
    ),
    # Update view for course.
    # path('teacher/course/update/<int:courseID>/'),

    # Course URLs.
    # Detail view of course.
    path('course/detail/<int:courseID>/', course.CourseDetailView.as_view(),
         name='courseDetail'
    ),
]
