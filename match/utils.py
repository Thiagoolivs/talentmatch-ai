from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def calculate_match_score(candidate, job):
    if not hasattr(candidate, 'candidate_profile'):
        return 0.0
    
    candidate_skills = candidate.candidate_profile.skills or ''
    job_requirements = job.requirements or ''
    
    if not candidate_skills or not job_requirements:
        return 0.0
    
    try:
        vectorizer = TfidfVectorizer(lowercase=True, stop_words=None)
        texts = [candidate_skills, job_requirements]
        tfidf_matrix = vectorizer.fit_transform(texts)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(similarity), 4)
    except Exception:
        return 0.0


def get_matched_and_missing_skills(candidate, job):
    if not hasattr(candidate, 'candidate_profile'):
        return [], []
    
    candidate_skills = set(candidate.candidate_profile.get_skills_list())
    job_requirements = set(job.get_requirements_list())
    
    matched = list(candidate_skills & job_requirements)
    missing = list(job_requirements - candidate_skills)
    
    return matched, missing


def get_recommended_jobs_for_candidate(candidate, limit=10):
    from jobs.models import Job
    from .models import MatchResult
    
    if not hasattr(candidate, 'candidate_profile'):
        return []
    
    active_jobs = Job.objects.filter(is_active=True).select_related('company__company_profile')
    recommendations = []
    
    for job in active_jobs:
        score = calculate_match_score(candidate, job)
        matched, missing = get_matched_and_missing_skills(candidate, job)
        
        match_result, created = MatchResult.objects.update_or_create(
            candidate=candidate,
            job=job,
            defaults={
                'score': score,
                'matched_skills': ', '.join(matched),
                'missing_skills': ', '.join(missing)
            }
        )
        
        if score > 0.1:
            recommendations.append({
                'job': job,
                'score': score,
                'matched_skills': matched,
                'missing_skills': missing
            })
    
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations[:limit]


def get_recommended_candidates_for_job(job, limit=10):
    from accounts.models import User
    from .models import MatchResult
    
    candidates = User.objects.filter(
        user_type='candidate'
    ).select_related('candidate_profile')
    
    recommendations = []
    
    for candidate in candidates:
        if not hasattr(candidate, 'candidate_profile'):
            continue
            
        score = calculate_match_score(candidate, job)
        matched, missing = get_matched_and_missing_skills(candidate, job)
        
        match_result, created = MatchResult.objects.update_or_create(
            candidate=candidate,
            job=job,
            defaults={
                'score': score,
                'matched_skills': ', '.join(matched),
                'missing_skills': ', '.join(missing)
            }
        )
        
        if score > 0.1:
            recommendations.append({
                'candidate': candidate,
                'score': score,
                'matched_skills': matched,
                'missing_skills': missing
            })
    
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations[:limit]


def get_skill_gaps(candidate):
    from jobs.models import Job
    
    if not hasattr(candidate, 'candidate_profile'):
        return []
    
    candidate_skills = set(candidate.candidate_profile.get_skills_list())
    all_requirements = set()
    
    popular_jobs = Job.objects.filter(is_active=True)[:50]
    for job in popular_jobs:
        all_requirements.update(job.get_requirements_list())
    
    missing_skills = list(all_requirements - candidate_skills)
    return missing_skills
