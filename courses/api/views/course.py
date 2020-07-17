from typing import Dict, List, Union

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from api.models import Course, CourseVideo, CourseTaughtByTeacher
from shortener.views import shortenURL


class CourseDetailView(APIView):
    def get(self, request: Request, courseID: int) -> Response:
        # Get a `Course` object for this course ID.
        try:
            course: Course = Course.objects.get(id=courseID)
        except ObjectDoesNotExist:
            return Response(
                {'body': 'No course was found with ID {}.'.format(courseID)},
                HTTP_404_NOT_FOUND
            )

        # Obtaining the teacher(s) of this course.
        courseTaughtBy: QuerySet = CourseTaughtByTeacher.objects.\
            filter(course=course)

        teachers: List[str] = list()
        for teacher in courseTaughtBy:
            teachers.append(
                teacher.teacher.user.first_name + " "
                + teacher.teacher.user.last_name
            )

        # Constructing the response dictionary.
        CourseVideoType = Dict[str, Union[str, int]]
        Mapping = Union[List[CourseVideoType], List[str], int, str]
        responseData: Dict[str, Mapping] = {
            'id': course.id,
            'name': course.name,
            'description': course.description,
            'image': ('http://' + request.get_host() + '/short/'
                      + shortenURL('/' + course.image.url) + '/'),
            'teachers': teachers,
            'videos': list(),
        }

        # Getting the list of course videos.
        courseVideos: QuerySet = CourseVideo.objects.filter(course=course)

        # Adding information for each course video to the response.
        for video in courseVideos:
            current: CourseVideoType = {
                'id': video.id,
                'title': video.title,
                'description': video.description,
                'dateUploaded': video.dateAdded.isoformat(),
                'url': ('http://' + request.get_host() + '/short/'
                        + shortenURL('/' + video.video.url) + '/')
            }

            responseData['videos'].append(current)

        # Constructing and sending the response.
        return Response(responseData, HTTP_200_OK)
