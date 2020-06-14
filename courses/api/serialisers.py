from django.contrib.sessions.models import Session
from rest_framework import serializers


class SessionSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['session_key', 'expire_date', ]
