from django.shortcuts import render, get_object_or_404
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


def company_detail(request, user_id):
    """Página pública da empresa com perfil, vagas ativas e publicações."""
    from django.contrib.auth import get_user_model
    from feed.models import Post

    User = get_user_model()
    company_user = get_object_or_404(User, id=user_id, user_type='company', is_active=True)
    profile = getattr(company_user, 'company_profile', None)

    active_jobs = Job.objects.filter(company=company_user, is_active=True).order_by('-created_at')
    posts = Post.objects.filter(author=company_user).order_by('-created_at')[:5]

    return render(request, 'core/company_detail.html', {
        'company_user': company_user,
        'profile': profile,
        'active_jobs': active_jobs,
        'posts': posts,
    })
