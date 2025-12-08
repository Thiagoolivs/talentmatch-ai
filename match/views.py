from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from jobs.models import Job
from .utils import (get_recommended_jobs_for_candidate, 
                    get_recommended_candidates_for_job,
                    get_skill_gaps)


@login_required
def recommended_jobs(request):
    if not request.user.is_candidate():
        return render(request, 'match/access_denied.html')
    
    recommendations = get_recommended_jobs_for_candidate(request.user, limit=20)
    skill_gaps = get_skill_gaps(request.user)
    
    return render(request, 'match/recommended_jobs.html', {
        'recommendations': recommendations,
        'skill_gaps': skill_gaps[:10]
    })


@login_required
def recommended_candidates(request, job_id):
    if not request.user.is_company():
        return render(request, 'match/access_denied.html')
    
    job = get_object_or_404(Job, pk=job_id, company=request.user)
    recommendations = get_recommended_candidates_for_job(job, limit=20)
    
    return render(request, 'match/recommended_candidates.html', {
        'job': job,
        'recommendations': recommendations
    })


@login_required
def match_overview(request):
    context = {}
    
    if request.user.is_candidate():
        recommendations = get_recommended_jobs_for_candidate(request.user, limit=5)
        skill_gaps = get_skill_gaps(request.user)
        context['recommendations'] = recommendations
        context['skill_gaps'] = skill_gaps[:5]
    
    elif request.user.is_company():
        jobs = Job.objects.filter(company=request.user, is_active=True)
        job_recommendations = []
        for job in jobs[:5]:
            candidates = get_recommended_candidates_for_job(job, limit=3)
            job_recommendations.append({
                'job': job,
                'candidates': candidates
            })
        context['job_recommendations'] = job_recommendations
    
    return render(request, 'match/overview.html', context)
