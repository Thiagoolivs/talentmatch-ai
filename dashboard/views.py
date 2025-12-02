from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from jobs.models import Job, Application
from courses.models import Course, UserCourse
from accounts.models import User, CandidateProfile, CompanyProfile
from match.utils import get_recommended_jobs_for_candidate, get_skill_gaps


@login_required
def index(request):
    user = request.user
    
    if user.is_candidate():
        return candidate_dashboard(request)
    elif user.is_company():
        return company_dashboard(request)
    else:
        return admin_dashboard(request)


def candidate_dashboard(request):
    user = request.user
    
    applications = Application.objects.filter(candidate=user).select_related('job__company__company_profile')
    applications_count = applications.count()
    
    status_counts = {
        'submitted': applications.filter(status='submitted').count(),
        'analyzing': applications.filter(status='analyzing').count(),
        'preselected': applications.filter(status='preselected').count(),
        'rejected': applications.filter(status='rejected').count(),
    }
    
    user_courses = UserCourse.objects.filter(user=user).select_related('course')
    in_progress_courses = user_courses.filter(status='in_progress')
    completed_courses = user_courses.filter(status='completed').count()
    
    recommended_jobs = get_recommended_jobs_for_candidate(user, limit=5)
    skill_gaps = get_skill_gaps(user)
    
    recommended_courses = []
    for course in Course.objects.filter(is_active=True)[:10]:
        course_skills = course.get_skills_list()
        matching = [s for s in skill_gaps if s in course_skills]
        if matching:
            recommended_courses.append({
                'course': course,
                'matching_skills': matching
            })
    recommended_courses = sorted(recommended_courses, key=lambda x: len(x['matching_skills']), reverse=True)[:5]
    
    profile_complete = 0
    if hasattr(user, 'candidate_profile'):
        profile = user.candidate_profile
        if profile.bio: profile_complete += 20
        if profile.skills: profile_complete += 25
        if profile.experience: profile_complete += 20
        if profile.education: profile_complete += 15
        if profile.resume: profile_complete += 20
    
    return render(request, 'dashboard/candidate.html', {
        'applications': applications[:5],
        'applications_count': applications_count,
        'status_counts': status_counts,
        'in_progress_courses': in_progress_courses[:4],
        'completed_courses_count': completed_courses,
        'recommended_jobs': recommended_jobs,
        'recommended_courses': recommended_courses,
        'skill_gaps': skill_gaps[:5],
        'profile_complete': profile_complete,
    })


def company_dashboard(request):
    user = request.user
    
    jobs = Job.objects.filter(company=user)
    active_jobs = jobs.filter(is_active=True)
    total_applications = Application.objects.filter(job__company=user).count()
    
    jobs_with_stats = []
    for job in active_jobs[:5]:
        apps = job.applications.all()
        jobs_with_stats.append({
            'job': job,
            'total_applications': apps.count(),
            'new_applications': apps.filter(status='submitted').count(),
            'analyzing': apps.filter(status='analyzing').count(),
        })
    
    recent_applications = Application.objects.filter(
        job__company=user
    ).select_related('candidate__candidate_profile', 'job').order_by('-applied_at')[:10]
    
    status_distribution = {
        'submitted': Application.objects.filter(job__company=user, status='submitted').count(),
        'analyzing': Application.objects.filter(job__company=user, status='analyzing').count(),
        'preselected': Application.objects.filter(job__company=user, status='preselected').count(),
        'rejected': Application.objects.filter(job__company=user, status='rejected').count(),
    }
    
    return render(request, 'dashboard/company.html', {
        'total_jobs': jobs.count(),
        'active_jobs': active_jobs.count(),
        'total_applications': total_applications,
        'jobs_with_stats': jobs_with_stats,
        'recent_applications': recent_applications,
        'status_distribution': status_distribution,
    })


def admin_dashboard(request):
    total_users = User.objects.count()
    total_candidates = User.objects.filter(user_type='candidate').count()
    total_companies = User.objects.filter(user_type='company').count()
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(is_active=True).count()
    total_applications = Application.objects.count()
    total_courses = Course.objects.count()
    
    recent_users = User.objects.order_by('-created_at')[:10]
    recent_jobs = Job.objects.order_by('-created_at')[:10]
    recent_applications = Application.objects.order_by('-applied_at')[:10]
    
    applications_by_status = {
        'submitted': Application.objects.filter(status='submitted').count(),
        'analyzing': Application.objects.filter(status='analyzing').count(),
        'preselected': Application.objects.filter(status='preselected').count(),
        'rejected': Application.objects.filter(status='rejected').count(),
        'hired': Application.objects.filter(status='hired').count(),
    }
    
    return render(request, 'dashboard/admin.html', {
        'total_users': total_users,
        'total_candidates': total_candidates,
        'total_companies': total_companies,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'total_courses': total_courses,
        'recent_users': recent_users,
        'recent_jobs': recent_jobs,
        'recent_applications': recent_applications,
        'applications_by_status': applications_by_status,
    })
