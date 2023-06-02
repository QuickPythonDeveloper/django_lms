from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.decorators import method_decorator

from django_lms.accounts.models import User
from django_lms.accounts.decorators import lecturer_required
from .forms import (
    ProgramForm, CourseAddForm, CourseAllocationForm,
    EditCourseAllocationForm, UploadFormFile, UploadFormVideo
)
from .models import (
    Program,
    Course,
    CourseAllocation,
    Upload,
    UploadVideo
)


# ########################################################
# Program views
# ########################################################
@login_required
def program_view(request):
    programs = Program.objects.all()

    program_filter = request.GET.get('program_filter')
    if program_filter:
        programs = Program.objects.filter(title__icontains=program_filter)

    return render(request, 'course/program_list.html', {
        'title': "Programs | DjangoSMS",
        'programs': programs,
    })


@login_required
@lecturer_required
def program_add(request):
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, request.POST.get('title') + ' program has been created.')
            return redirect('programs')
        else:
            messages.error(request, 'Correct the error(S) below.')
    else:
        form = ProgramForm()

    return render(request, 'course/program_add.html', {
        'title': "Add Program | DjangoSMS",
        'form': form,
    })


@login_required
def program_detail(request, pk):
    program = Program.objects.get(pk=pk)
    courses = Course.objects.filter(program_id=pk).order_by('-year')
    credits = Course.objects.aggregate(Sum('credit'))

    paginator = Paginator(courses, 10)
    page = request.GET.get('page')

    courses = paginator.get_page(page)

    return render(request, 'course/program_single.html', {
        'title': program.title,
        'program': program, 'courses': courses, 'credits': credits
    }, )


@login_required
@lecturer_required
def program_edit(request, pk):
    program = Program.objects.get(pk=pk)

    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, str(request.POST.get('title')) + ' program has been updated.')
            return redirect('programs')
    else:
        form = ProgramForm(instance=program)

    return render(request, 'course/program_add.html', {
        'title': "Edit Program | DjangoSMS",
        'form': form
    })


@login_required
@lecturer_required
def program_delete(request, pk):
    program = Program.objects.get(pk=pk)
    title = program.title
    program.delete()
    messages.success(request, 'Program ' + title + ' has been deleted.')

    return redirect('programs')


# ########################################################

# ########################################################
# Course views
# ########################################################
@login_required
def course_single(request, slug):
    course = Course.objects.get(slug=slug)
    files = Upload.objects.filter(course__slug=slug)
    videos = UploadVideo.objects.filter(course__slug=slug)

    # lecturers = User.objects.filter(allocated_lecturer__pk=course.id)
    lecturers = CourseAllocation.objects.filter(courses__pk=course.id)

    return render(request, 'course/course_single.html', {
        'title': course.title,
        'course': course,
        'files': files,
        'videos': videos,
        'lecturers': lecturers,
        'media_url': settings.MEDIA_ROOT,
    }, )


@login_required
@lecturer_required
def course_add(request, pk):
    users = User.objects.all()
    if request.method == 'POST':
        form = CourseAddForm(request.POST)
        course_name = request.POST.get('title')
        course_code = request.POST.get('code')
        if form.is_valid():
            form.save()
            messages.success(request, (course_name + '(' + course_code + ')' + ' has been created.'))
            return redirect('program_detail', pk=request.POST.get('program'))
        else:
            messages.error(request, 'Correct the error(s) below.')
    else:
        form = CourseAddForm(initial={'program': Program.objects.get(pk=pk)})

    return render(request, 'course/course_add.html', {
        'title': "Add Course | DjangoSMS",
        'form': form, 'program': pk, 'users': users
    }, )


@login_required
@lecturer_required
def course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        form = CourseAddForm(request.POST, instance=course)
        course_name = request.POST.get('title')
        course_code = request.POST.get('code')
        if form.is_valid():
            form.save()
            messages.success(request, (course_name + '(' + course_code + ')' + ' has been updated.'))
            return redirect('program_detail', pk=request.POST.get('program'))
        else:
            messages.error(request, 'Correct the error(s) below.')
    else:
        form = CourseAddForm(instance=course)

    return render(request, 'course/course_add.html', {
        'title': "Edit Course | DjangoSMS",
        # 'form': form, 'program': pk, 'course': pk
        'form': form
    }, )


@login_required
@lecturer_required
def course_delete(request, slug):
    course = Course.objects.get(slug=slug)
    # course_name = course.title
    course.delete()
    messages.success(request, 'Course ' + course.title + ' has been deleted.')

    return redirect('program_detail', pk=course.program.id)


# ########################################################


# ########################################################
# Course Allocation
# ########################################################
@method_decorator([login_required], name='dispatch')
class CourseAllocationFormView(CreateView):
    form_class = CourseAllocationForm
    template_name = 'course/course_allocation_form.html'

    def get_form_kwargs(self):
        kwargs = super(CourseAllocationFormView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # if a staff has been allocated a course before update it else create new
        lecturer = form.cleaned_data['lecturer']
        selected_courses = form.cleaned_data['courses']
        courses = ()
        for course in selected_courses:
            courses += (course.pk,)
        # print(courses)

        try:
            a = CourseAllocation.objects.get(lecturer=lecturer)
        except:
            a = CourseAllocation.objects.create(lecturer=lecturer)
        for i in range(0, selected_courses.count()):
            a.courses.add(courses[i])
            a.save()
        return redirect('course_allocation_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Assign Course | DjangoSMS"
        return context


@login_required
def course_allocation_view(request):
    allocated_courses = CourseAllocation.objects.all()
    return render(request, 'course/course_allocation_view.html', {
        'title': "Course Allocations | DjangoSMS",
        "allocated_courses": allocated_courses
    })


@login_required
@lecturer_required
def edit_allocated_course(request, pk):
    allocated = get_object_or_404(CourseAllocation, pk=pk)
    if request.method == 'POST':
        form = EditCourseAllocationForm(request.POST, instance=allocated)
        if form.is_valid():
            form.save()
            messages.success(request, 'course assigned has been updated.')
            return redirect('course_allocation_view')
    else:
        form = EditCourseAllocationForm(instance=allocated)

    return render(request, 'course/course_allocation_form.html', {
        'title': "Edit Course Allocated | DjangoSMS",
        'form': form, 'allocated': pk
    }, )


@login_required
@lecturer_required
def deallocate_course(request, pk):
    course = CourseAllocation.objects.get(pk=pk)
    course.delete()
    messages.success(request, 'successfully deallocate!')
    return redirect("course_allocation_view")


# ########################################################


# ########################################################
# File Upload views
# ########################################################
@login_required
@lecturer_required
def handle_file_upload(request, slug):
    course = Course.objects.get(slug=slug)
    if request.method == 'POST':
        form = UploadFormFile(request.POST, request.FILES, {'course': course})
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' has been uploaded.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormFile()
    return render(request, 'upload/upload_file_form.html', {
        'title': "File Upload | DjangoSMS",
        'form': form, 'course': course
    })


@login_required
@lecturer_required
def handle_file_edit(request, slug, file_id):
    course = Course.objects.get(slug=slug)
    instance = Upload.objects.get(pk=file_id)
    if request.method == 'POST':
        form = UploadFormFile(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' has been updated.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormFile(instance=instance)

    return render(request, 'upload/upload_file_form.html', {
        'title': instance.title,
        'form': form, 'course': course})


def handle_file_delete(request, slug, file_id):
    file = Upload.objects.get(pk=file_id)
    file.delete()

    messages.success(request, (file.title + ' has been deleted.'))
    return redirect('course_detail', slug=slug)


# ########################################################
# Video Upload views
# ########################################################
@login_required
@lecturer_required
def handle_video_upload(request, slug):
    course = Course.objects.get(slug=slug)
    if request.method == 'POST':
        form = UploadFormVideo(request.POST, request.FILES, {'course': course})
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' has been uploaded.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormVideo()
    return render(request, 'upload/upload_video_form.html', {
        'title': "Video Upload | DjangoSMS",
        'form': form, 'course': course
    })


@login_required
def handle_video_single(request, slug, video_slug):
    course = get_object_or_404(Course, slug=slug)
    video = get_object_or_404(UploadVideo, slug=video_slug)
    return render(request, 'upload/video_single.html', {'video': video})


@login_required
@lecturer_required
def handle_video_edit(request, slug, video_slug):
    course = Course.objects.get(slug=slug)
    instance = UploadVideo.objects.get(slug=video_slug)
    if request.method == 'POST':
        form = UploadFormVideo(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' has been updated.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormVideo(instance=instance)

    return render(request, 'upload/upload_video_form.html', {
        'title': instance.title,
        'form': form, 'course': course})


def handle_video_delete(request, slug, video_slug):
    video = get_object_or_404(UploadVideo, slug=video_slug)
    # video = UploadVideo.objects.get(slug=video_slug)
    video.delete()

    messages.success(request, (video.title + ' has been deleted.'))
    return redirect('course_detail', slug=slug)

# ########################################################


# ########################################################
# Course Registration
# ########################################################


# ########################################################
