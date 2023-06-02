from django.contrib import admin

from .models import (
    Session,
    Semester,
    NewsAndEvents
)

admin.site.register(Semester)
admin.site.register(Session)
admin.site.register(NewsAndEvents)
