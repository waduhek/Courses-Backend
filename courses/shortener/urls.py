from django.urls import path

from .views import LengthenURL

app_name = 'shortener'

urlpatterns = [
    path('<str:shortHash>/', LengthenURL.as_view(), name='shortenAPI'),
]
