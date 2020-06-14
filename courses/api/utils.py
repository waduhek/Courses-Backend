from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist

from .models import UserSessionMapping


def createSessionForUser(user: User) -> Session:
    '''
    Description
    -----------
    Function that will return a session for the given
    `django.contrib.auth.models.User` object. It will look up in the
    `api.modlels.UserSessionMapping` table to find out if a session
    already exists for the user. If an existing session is found, it
    returns it; otherwise, it will create a new session and return it.

    Returns
    -------
    -   A valid `Session` object if session was created.
    -   `None` if session could not be created.
    '''
    # The return value.
    session: Session = None

    # Search the `UserSessionMapping` table for this user.
    try:
        sessionMap: UserSessionMapping = UserSessionMapping.objects.get(
            user=user
        )
    except ObjectDoesNotExist:
        # The user does not have an active session. So create one.
        newSessionStore: SessionStore = SessionStore()
        newSessionStore.create()

        # Now retrieve a `Session` object. This allows us to access
        # session data and session expiry date.
        session = Session.objects.get(pk=newSessionStore.session_key)

        # Create a `UserSessionMapping` object for this user and
        # session.
        UserSessionMapping(user=user, session=session).save()
    else:
        # A `UserSessionMapping` object was found fro this user. So we
        # return that session for the user.
        session = Session.objects.get(pk=sessionMap.session)

    return session
