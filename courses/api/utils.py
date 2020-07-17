from datetime import timedelta
from typing import Optional

from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import timezone

from .models import UserSessionMapping


def createSessionForUser(user: User) -> Optional[Session]:
    """Will return a session for the given
    `django.contrib.auth.models.User` object. It will look up in the
    `api.models.UserSessionMapping` table to find out if a session
    already exists for the user. If an existing session is found, it
    returns it; otherwise, it will create a new session and return it.

    :param user: A `User` object.
    :type user: User

    :returns: A valid session if session was created. Otherwise none.
    :rtype: Session or None
    """
    # The return value.
    session: Optional[Session] = None

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
    except MultipleObjectsReturned:
        # TODO: Manage when multiple sessions were found.
        pass
    else:
        # A `UserSessionMapping` object was found for this user. So we
        # return that session for the user.
        session = Session.objects.get(pk=sessionMap.session)

    return session


def _updateSessionExpiryDate(session: Session):
    """Used to update the given session's expiry date.

    If there are less than 30 days for the session to expire, this
    function will add another 30 days to the session's expiry date.

    :param session: The session whose expiry date is to be checked.
    :type session: Session.
    """

    # Calculate the difference between the current time and the
    # expiry date of the session key.
    difference: timedelta = session.expire_date - timezone.now()

    # Add another 30 days if the number of days before the
    # expiry of the session is less than 30.
    if abs(difference.days) < 30:
        session.expire_date += timedelta(days=30)

    # Save this information.
    session.save()
