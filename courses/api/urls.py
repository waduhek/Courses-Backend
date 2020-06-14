from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('test/', views.TestAPIView.as_view(), name='test'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('validate/', views.ValidateSessionView.as_view(), name='validate'),
]
