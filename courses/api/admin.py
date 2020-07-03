from django.contrib import admin

from .models import (Course, CourseComment, CourseRating, CourseReply,
                     CourseTaughtByTeacher, CourseVideo, Student, Teacher,
                     UserSessionMapping)

admin.site.register(UserSessionMapping)
admin.site.register(Course)
admin.site.register(CourseComment)
admin.site.register(CourseReply)
admin.site.register(CourseRating)
admin.site.register(CourseVideo)
admin.site.register(CourseTaughtByTeacher)
admin.site.register(Student)
admin.site.register(Teacher)
