from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import models


class UserSessionMapping(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    session = models.OneToOneField(Session, models.CASCADE)

    def __str__(self):
        return 'Session map created for {}'.format(self.user.first_name)

    class Meta:
        db_table = 'courses_user_session_mapping'
        verbose_name = 'UserSessionMap'
        verbose_name_plural = 'UserSessionMaps'
