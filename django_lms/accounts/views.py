from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import PasswordChangeForm

from .decorators import admin_required
from .forms import StaffAddForm, ProfileUpdateForm
from .models import User


def validate_username(request):
    username = request.GET.get("username", None)
    data = {
        "is_taken": User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)


@login_required
@admin_required
def admin_panel(request):
    return render(request, 'setting/admin_panel.html', {})


# ########################################################


# ########################################################
# Setting views
# ########################################################
@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'setting/profile_info_change.html', {
        'title': 'Setting | DjangoSMS',
        'form': form,
    })


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error(s) below. ')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'setting/password_change.html', {
        'form': form,
    })


# ########################################################

@login_required
@admin_required
def staff_add_view(request):
    if request.method == 'POST':
        form = StaffAddForm(request.POST)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if form.is_valid():
            form.save()
            messages.success(request, "Account for lecturer " + first_name + ' ' + last_name + " has been created.")
            return redirect("lecturer_list")
    else:
        form = StaffAddForm()

    context = {
        'title': 'Lecturer Add | DjangoSMS',
        'form': form,
    }

    return render(request, 'accounts/add_staff.html', context)


@login_required
@admin_required
def edit_staff(request, pk):
    instance = get_object_or_404(User, is_lecturer=True, pk=pk)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, 'Lecturer ' + full_name + ' has been updated.')
            return redirect('lecturer_list')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ProfileUpdateForm(instance=instance)
    return render(request, 'accounts/edit_lecturer.html', {
        'title': 'Edit Lecturer | DjangoSMS',
        'form': form,
    })


@method_decorator([login_required, admin_required], name='dispatch')
class LecturerListView(ListView):
    queryset = User.objects.filter(is_lecturer=True)
    template_name = "accounts/lecturer_list.html"
    paginate_by = 10  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Lecturers | DjangoSMS"
        return context


@login_required
@admin_required
def delete_staff(request, pk):
    lecturer = get_object_or_404(User, pk=pk)
    full_name = lecturer.get_full_name
    lecturer.delete()
    messages.success(request, 'Lecturer ' + full_name + ' has been deleted.')
    return redirect('lecturer_list')


# ########################################################


# ########################################################
# Student views
# ########################################################

@login_required
@admin_required
def edit_student(request, pk):
    # instance = User.objects.get(pk=pk)
    instance = get_object_or_404(User, is_student=True, pk=pk)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, ('Student ' + full_name + ' has been updated.'))
            return redirect('student_list')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ProfileUpdateForm(instance=instance)
    return render(request, 'accounts/edit_student.html', {
        'title': 'Edit-profile | DjangoSMS',
        'form': form,
    })

# ########################################################
