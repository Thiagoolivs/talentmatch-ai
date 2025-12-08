from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Course, Lesson, UserCourse
from match.utils import get_skill_gaps


def course_list(request):
    courses = Course.objects.filter(is_active=True)
    
    area = request.GET.get('area')
    level = request.GET.get('level')
    
    if area:
        courses = courses.filter(area=area)
    if level:
        courses = courses.filter(level=level)
    
    paginator = Paginator(courses, 12)
    page = request.GET.get('page')
    courses = paginator.get_page(page)
    
    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'areas': Course.AREA_CHOICES,
        'levels': Course.LEVEL_CHOICES,
        'selected_area': area,
        'selected_level': level
    })


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    user_course = None
    lessons = course.lessons.all().order_by('order')
    
    if request.user.is_authenticated:
        user_course = UserCourse.objects.filter(user=request.user, course=course).first()
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'user_course': user_course,
        'lessons': lessons
    })


def lesson_detail(request, course_pk, lesson_pk):
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=lesson_pk, course=course)
    lessons = course.lessons.all().order_by('order')
    
    prev_lesson = lessons.filter(order__lt=lesson.order).last()
    next_lesson = lessons.filter(order__gt=lesson.order).first()
    
    user_course = None
    if request.user.is_authenticated:
        user_course = UserCourse.objects.filter(user=request.user, course=course).first()
        if not user_course:
            user_course = UserCourse.objects.create(
                user=request.user,
                course=course,
                status='in_progress',
                started_at=timezone.now()
            )
        elif user_course.status == 'not_started':
            user_course.status = 'in_progress'
            user_course.started_at = timezone.now()
            user_course.save()
    
    return render(request, 'courses/lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'lessons': lessons,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'user_course': user_course
    })


@login_required
def start_course(request, pk):
    course = get_object_or_404(Course, pk=pk, is_active=True)
    
    user_course, created = UserCourse.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'status': 'in_progress', 'started_at': timezone.now()}
    )
    
    if not created and user_course.status == 'not_started':
        user_course.status = 'in_progress'
        user_course.started_at = timezone.now()
        user_course.save()
    
    messages.success(request, f'Você iniciou o curso "{course.title}"!')
    
    if course.external_url:
        return redirect(course.external_url)
    
    return redirect('courses:detail', pk=pk)


@login_required
def update_progress(request, pk):
    if request.method != 'POST':
        return redirect('courses:detail', pk=pk)
    
    course = get_object_or_404(Course, pk=pk)
    user_course = get_object_or_404(UserCourse, user=request.user, course=course)
    
    progress = int(request.POST.get('progress', 0))
    progress = max(0, min(100, progress))
    
    user_course.progress = progress
    
    if progress >= 100:
        user_course.status = 'completed'
        user_course.completed_at = timezone.now()
        messages.success(request, f'Parabéns! Você concluiu o curso "{course.title}"!')
    elif progress > 0:
        user_course.status = 'in_progress'
    
    user_course.save()
    
    return redirect('courses:detail', pk=pk)


@login_required
def complete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    user_course = get_object_or_404(UserCourse, user=request.user, course=course)
    
    user_course.status = 'completed'
    user_course.progress = 100
    user_course.completed_at = timezone.now()
    user_course.save()
    
    messages.success(request, f'Parabéns! Você concluiu o curso "{course.title}"!')
    return redirect('courses:my_courses')


@login_required
def my_courses(request):
    user_courses = UserCourse.objects.filter(user=request.user).select_related('course')
    
    in_progress = user_courses.filter(status='in_progress')
    completed = user_courses.filter(status='completed')
    
    return render(request, 'courses/my_courses.html', {
        'in_progress': in_progress,
        'completed': completed
    })


@login_required
def recommended_courses(request):
    if not request.user.is_candidate():
        return redirect('courses:list')
    
    skill_gaps = get_skill_gaps(request.user)
    
    recommended = []
    all_courses = Course.objects.filter(is_active=True)
    
    for course in all_courses:
        course_skills = course.get_skills_list()
        matching_gaps = [gap for gap in skill_gaps if gap in course_skills]
        
        if matching_gaps:
            recommended.append({
                'course': course,
                'matching_skills': matching_gaps,
                'score': len(matching_gaps)
            })
    
    recommended.sort(key=lambda x: x['score'], reverse=True)
    
    return render(request, 'courses/recommended_courses.html', {
        'recommendations': recommended[:20],
        'skill_gaps': skill_gaps[:10]
    })
