from django.shortcuts import render
from jobs.models import Job
from courses.models import Course


def home(request):
    featured_jobs = Job.objects.filter(is_active=True).select_related('company__company_profile')[:6]
    featured_courses = Course.objects.filter(is_active=True)[:4]
    
    stats = {
        'jobs': Job.objects.filter(is_active=True).count(),
        'courses': Course.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'core/home.html', {
        'featured_jobs': featured_jobs,
        'featured_courses': featured_courses,
        'stats': stats
    })


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    return render(request, 'core/contact.html')
