from typing import Tuple

import magic
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.fields.files import FieldFile
from django.utils.deconstruct import deconstructible


class UserSessionMapping(models.Model):
    """This table stores the mapping between a user and the assigned
    session.

    There can be only one session assigned to a user.
    """

    user = models.OneToOneField(User, models.CASCADE)
    session = models.OneToOneField(Session, models.CASCADE)

    objects = models.Manager()

    def __str__(self):
        return 'Session map created for {}'.format(self.user.username)

    class Meta:
        db_table = 'courses_user_session_mapping'
        verbose_name = 'User Session Mapping'
        verbose_name_plural = 'User Session Mappings'


class Teacher(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    biography = models.TextField()

    objects = models.Manager()

    def __str__(self):
        return 'Teacher: {}'.format(self.user.username)

    class Meta:
        db_table = 'courses_teacher'
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'


class Student(models.Model):
    user = models.OneToOneField(User, models.CASCADE)

    objects = models.Manager()

    def __str__(self):
        return 'Student: {}'.format(self.user.username)

    class Meta:
        db_table = 'courses_student'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'


class Course(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='course/image/%Y/%m/%d/')
    description = models.TextField()

    objects = models.Manager()

    def __str__(self):
        return 'Course: {}'.format(self.name)

    class Meta:
        db_table = 'courses_course'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'


class CourseTaughtByTeacher(models.Model):
    teacher = models.ForeignKey(Teacher, models.SET_NULL, null=True)
    course = models.ForeignKey(Course, models.SET_NULL, null=True)

    objects = models.Manager()

    def __str__(self):
        return 'Course \'{}\' is taught by \'{}\''.format(
            self.course.name, self.teacher
        )

    class Meta:
        db_table = 'courses_course_taught_by_teacher'
        verbose_name = 'Course Taught By Teacher'
        verbose_name_plural = 'Course(s) Taught By Teacher(s)'


@deconstructible
class CourseVideoValidator:
    """A validator for file fields that uses `libmagic` to verify the
    type of file.
    """

    def __init__(self, allowedContentTypes: Tuple[str]):
        """A validator for file fields that uses `libmagic` to verify the
        type of file.

        :param allowedContentTypes: A tuple of MIME type strings of
            supported file types.
        """
        self.allowedContentTypes: Tuple[str] = allowedContentTypes

    def __call__(self, video: FieldFile):
        # Get the MIME type string of this video.
        videoContentType = magic.from_buffer(video.read(), mime=True)
        # Point the cursor to the beginning of the file.
        video.seek(0)

        if videoContentType not in self.allowedContentTypes:
            raise ValidationError(
                'The file type %(contentType)s is not supported.',
                params={'contentType': videoContentType}
            )

    def __eq__(self, other):
        return (isinstance(other, CourseVideoValidator) and
                self.allowedContentTypes == other.allowedContentTypes)


class CourseVideo(models.Model):
    course = models.ForeignKey(Course, models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    dateAdded = models.DateTimeField(auto_now_add=True)

    videoValidator = CourseVideoValidator(('video/mp4',))
    video = models.FileField(
        upload_to='course/videos/%Y/%m/%d/',
        validators=[videoValidator, ]
    )

    objects = models.Manager()

    def __str__(self):
        return 'Video: {} for course {}'.format(self.title, self.course.name)

    class Meta:
        db_table = 'courses_video'
        verbose_name = 'Course Video'
        verbose_name_plural = 'Course Videos'


class CourseRating(models.Model):
    course = models.ForeignKey(Course, models.SET_NULL, null=True)
    student = models.ForeignKey(Student, models.SET_NULL, null=True)
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        null=True
    )

    objects = models.Manager()

    def __str__(self):
        return 'Rating for course: {}'.format(self.course.name)

    class Meta:
        db_table = 'courses_course_rating'
        verbose_name = 'Course Rating'
        verbose_name_plural = 'Course Ratings'


class CourseComment(models.Model):
    course = models.ForeignKey(Course, models.SET_NULL, null=True)
    user = models.ForeignKey(User, models.SET_NULL, null=True)
    comment = models.TextField()

    objects = models.Manager()

    def __str__(self):
        return 'User \'{}\' commented on course \'{}\''.format(
            self.user.username, self.course.name
        )

    class Meta:
        db_table = 'courses_course_comment'
        verbose_name = 'Course Comment'
        verbose_name_plural = 'Course Comments'


class CourseReply(models.Model):
    comment = models.ForeignKey(CourseComment, models.SET_NULL, null=True)
    user = models.ForeignKey(User, models.SET_NULL, null=True)
    reply = models.TextField()

    objects = models.Manager()

    def __str__(self):
        return 'User \'{}\' replied to comment \'{}\''.format(
            self.user.username, self.comment.id
        )

    class Meta:
        db_table = 'courses_course_reply'
        verbose_name = 'Course Reply'
        verbose_name_plural = 'Course Replies'
