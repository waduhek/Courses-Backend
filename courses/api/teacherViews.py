from typing import List

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from .models import Course, CourseTaughtByTeacher, UserSessionMapping
from .serialisers import CourseSerialiser


class AllCourses(APIView):
    def get(self, request: Request) -> Response:
        # Get the session ID from the cookies
        sessionID: str = request.COOKIES['sessionID']

        # Obtain the `User` object from `UserSessionMapping` model.
        mapping: UserSessionMapping = UserSessionMapping.objects.get(
            session=sessionID
        )

        # Getting all the courses taught by this teacher.
        courses: QuerySet = CourseTaughtByTeacher.objects.filter(
            teacher__user=mapping.user
        )

        # Response data.
        responseData: List[dict] = list()

        for course in courses:
            # Obtain course information for each of the course taught
            # by this teacher.
            try:
                courseTaught: Course = Course.objects.get(
                    id=course.course.id
                )
            except ObjectDoesNotExist:
                pass
            else:
                # Serialise this course information.
                serialisedCourse = CourseSerialiser(courseTaught)

                responseData.append(serialisedCourse.data)

        return Response(responseData, HTTP_200_OK)
