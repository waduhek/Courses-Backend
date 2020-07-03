from django.contrib.sessions.models import Session
from rest_framework import serializers

from .models import Course


class SessionSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['session_key', 'expire_date', ]


class CourseSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
