from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.utils import timezone
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND,
                                   HTTP_500_INTERNAL_SERVER_ERROR)
from rest_framework.views import APIView

from .models import Student, Teacher, UserSessionMapping
from .serialisers import SessionSerialiser
from .utils import _updateSessionExpiryDate, createSessionForUser


class LoginView(APIView):
    def post(self, request: Request) -> Response:
        requestData = dict(request.data)

        # Try to find a user with the matching username and password.
        user: User = authenticate(
            username=requestData['username'],
            password=requestData['password']
        )

        # Check if the user is authenticated or not.
        if user is not None:
            # Find out if the user is a teacher or not.
            try:
                teacherUser = Teacher.objects.get(user=user)
            except ObjectDoesNotExist:
                teacherUser = None

            # User is authenticated, obtain a session for them. If an
            # already existing session exists for this user, return it.
            # Otherwise, create a new one.
            newSession: Session = createSessionForUser(user)

            # Update session expiry date if needed.
            _updateSessionExpiryDate(newSession)

            # Serialiser instance to serialise the session data
            sessionSerialiser: SessionSerialiser = SessionSerialiser(
                newSession
            )

            responseData: dict = {
                # User information.
                'firstName': user.first_name,
                'lastName': user.last_name,
                'email': user.email,
                'lastLogin': user.last_login,
                # Session ID information.
                # Even though the session ID will be set as a cookie, it
                # is sent as the response body for storage at the client
                # side.
                'sessionID': newSession.session_key,
                # The serialiser returns an RFC 3339 compliant date
                # which is a string and so it can be sent to the client.
                'sessionExpireDate': sessionSerialiser.data['expire_date'],
                # Flag set only if the user is a teacher.
                'isTeacher': True if teacherUser is not None else False
            }

            # Change the last login time to the current time.
            user.last_login = timezone.now()

            # Save the updated information in the database.
            user.save()

            # User is authorised, prepare OK response.
            # Creating a response.
            response: Response = Response(responseData, status=HTTP_200_OK)
            # Place the session ID in a cookie.
            response.set_cookie(
                'sessionID', newSession.session_key,
                expires=newSession.expire_date
            )

            return response
        else:
            responseData: dict = {'body': 'Invalid user credentials.'}
            # User is unauthorised, return UNAUTHORIZED.
            return Response(responseData, status=HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request: Request) -> Response:
        # Obtain the session ID from cookies.
        # If the session ID is not found in the cookies search for it
        # in the request body. If not found return BAD_REQUEST.
        if request.COOKIES.get('sessionID') is not None:
            print('Found session ID in cookies')
            sessionID = request.COOKIES.get('sessionID')
        elif request.data.get('sessionID') is not None:
            print('Found session ID in request body')
            sessionID = request.data['sessionID']
        else:
            responseData: dict = {
                'body': 'Could not obtain the session ID. Make sure that'
                        + 'the session ID is either in the body or set as a '
                        + 'cookie.'
            }
            return Response(responseData, status=HTTP_400_BAD_REQUEST)

        # Get the existing session object.
        try:
            existingSession: Session = Session.objects.get(pk=sessionID)
        except ObjectDoesNotExist:
            responseData: dict = {
                'body': 'Could not find the requested session.'
            }
            return Response(responseData, status=HTTP_404_NOT_FOUND)

        # Delete this session.
        existingSession.delete()

        # Check if the delete operation was successful.
        if existingSession.session_key is None:
            responseData: dict = {
                'body': 'Successfully deleted session.'
            }
            # Create a new response.
            response: Response = Response(responseData, status=HTTP_200_OK)
            # Delete the `sessionID` cookie if it is set.
            if request.COOKIES.get('sessionID') is not None:
                response.delete_cookie('sessionID')

            return response
        else:
            responseData: dict = {
                'body': 'Session was found but could not be terminated.'
            }
            # Create a new response.
            response: Response = Response(
                responseData, status=HTTP_500_INTERNAL_SERVER_ERROR
            )
            # Delete the `sessionID` cookie if it is set.
            if request.COOKIES.get('sessionID') is not None:
                response.delete_cookie('sessionID')

            return response


class SignupView(APIView):
    def post(self, request: Request) -> Response:
        requestData: dict = dict(request.data)

        # Make sure that the both the passwords entered are the same.
        # Although client side validation takes place this is done as a
        # redundancy step.
        if requestData['password'] != requestData['confirmPassword']:
            responseData: dict = {'body': 'The passwords don\'t match.'}
            return Response(responseData, status=HTTP_400_BAD_REQUEST)

        # Try to create a new user with the received credentials.
        # Django will raise an `IntegrityError` signalling that the
        # username is taken.
        try:
            newUser: User = User.objects.create_user(
                requestData['username'],
                requestData['email'],
                requestData['password']
            )
        except IntegrityError:
            # Username is already taken return error to the client.
            responseData: dict = {'body': 'Requested username is taken.'}
            # Here, we use a custom HTTP response code if the username
            # could not be allocated to the user.
            return Response(responseData, status=599)
        else:
            # The user was successfully created. Now, saving some more
            # information.
            newUser.first_name = requestData['firstName']
            newUser.last_name = requestData['lastName']
            newUser.date_joined = timezone.now()
            newUser.last_login = timezone.now()
            # Saving all of this information.
            newUser.save()

            # Since the users are categorised into teachers and
            # students, we need to make sure that this user is put in
            # the right category.
            if requestData['isTeacher']:
                # User is a teacher, make an entry in the `Teacher`
                # table.
                Teacher.objects.create(user=newUser)
            else:
                # User is a student, make an entry in the `Student`
                # table.
                Student.objects.create(user=newUser)

        # Create a new session for this user.
        newSession: Session = createSessionForUser(newUser)

        if newSession is not None:
            # Serialise the current session to get the session expiry
            # date in RFC 3339 format.
            serialisedSession: SessionSerialiser = SessionSerialiser(
                newSession
            )

            # Construct the same type of response data as constructed in
            # the login view.
            responseData: dict = {
                'firstName': newUser.first_name,
                'lastName': newUser.last_name,
                'email': newUser.email,
                'lastLogin': newUser.last_login,
                'sessionID': serialisedSession.data['session_key'],
                'sessionExpireDate': serialisedSession.data['expire_date'],
                'isTeacher': requestData['isTeacher'],
            }

            response: Response = Response(responseData, status=HTTP_200_OK)
            # Setting the session ID as cookie.
            response.set_cookie(
                'sessionID', newSession.session_key,
                expires=newSession.expire_date
            )

            return response
        else:
            # Something went wrong while creating a session. Send out a
            # 500 HTTP code.
            responseData: dict = {
                'body': 'Could not create a session for the user.'
            }
            return Response(
                responseData, status=HTTP_500_INTERNAL_SERVER_ERROR
            )


class ValidateSessionView(APIView):
    """A view to make sure that a client's session ID is a valid one."""

    def post(self, request: Request) -> Response:
        receivedSessionID = request.data['sessionID']
        receivedSessionExpiryDate = request.data['sessionExpireDate']

        # Check if the received session ID exists in the mapping table.
        try:
            sessionMapping: UserSessionMapping = UserSessionMapping.objects\
                .get(
                    session__pk=receivedSessionID
                )
        except ObjectDoesNotExist:
            # No object was found that matched the received session ID
            # and so the session is not valid.
            return Response(status=HTTP_401_UNAUTHORIZED)
        else:
            # Obtain session information from database.
            session: Session = Session.objects.get(pk=receivedSessionID)

            # Update the session's expiry date if needed.
            _updateSessionExpiryDate(session)

            # Construct the response to the client.
            responseData: dict = {
                'firstName': sessionMapping.user.first_name,
                'lastName': sessionMapping.user.last_name,
                'email': sessionMapping.user.email,
                'lastLogin': sessionMapping.user.last_login,
                'sessionID': session.session_key,
                'sessionExpireDate': session.expire_date,
            }

            # The session is authorised. Set the session ID as the cookie.
            response = Response(responseData, status=HTTP_200_OK)
            response.set_cookie(
                'sessionID', receivedSessionID,
                expires=session.expire_date
            )

            return response
