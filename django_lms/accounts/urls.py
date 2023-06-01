from django.urls import path, include

from .views import (
    admin_panel,
    profile_update, change_password,
    LecturerListView,
    staff_add_view, edit_staff,
    delete_staff,
    edit_student, validate_username
)

urlpatterns = [
    path('', include('django.contrib.auth.urls')),

    path('admin_panel/', admin_panel, name='admin_panel'),

    path('setting/', profile_update, name='edit_profile'),
    path('change_password/', change_password, name='change_password'),

    path('lecturers/', LecturerListView.as_view(), name='lecturer_list'),
    path('lecturer/add/', staff_add_view, name='add_lecturer'),
    path('staff/<int:pk>/edit/', edit_staff, name='staff_edit'),
    path('lecturers/<int:pk>/delete/', delete_staff, name='lecturer_delete'),

    path('student/<int:pk>/edit/', edit_student, name='student_edit'),

    path('ajax/validate-username/', validate_username, name='validate_username'),

]
