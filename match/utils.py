from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def calculate_match_score(candidate, job):
    """
    Calcula o score de match entre candidato e vaga usando multiplos fatores:
    - Skills (50% do peso)
    - Experiencia (25% do peso)
    - Localizacao (15% do peso)
    - Salario (10% do peso)
    """
    if not hasattr(candidate, 'candidate_profile'):
        return 0.0
    
    profile = candidate.candidate_profile
    total_score = 0.0
    weights = {
        'skills': 0.50,
        'experience': 0.25,
        'location': 0.15,
        'salary': 0.10
    }
    
    skills_score = calculate_skills_score(profile, job)
    total_score += skills_score * weights['skills']
    
    experience_score = calculate_experience_score(profile, job)
    total_score += experience_score * weights['experience']
    
    location_score = calculate_location_score(profile, job)
    total_score += location_score * weights['location']
    
    salary_score = calculate_salary_score(profile, job)
    total_score += salary_score * weights['salary']
    
    return round(float(total_score), 4)


def calculate_skills_score(profile, job):
    """Calcula score baseado em habilidades usando TF-IDF e match exato."""
    candidate_skills = profile.skills or ''
    job_requirements = job.requirements or ''
    
    if not candidate_skills or not job_requirements:
        return 0.0
    
    candidate_skills_list = set(profile.get_skills_list())
    job_requirements_list = set(job.get_requirements_list())
    
    if job_requirements_list:
        exact_matches = len(candidate_skills_list & job_requirements_list)
        exact_score = exact_matches / len(job_requirements_list)
    else:
        exact_score = 0.0
    
    try:
        vectorizer = TfidfVectorizer(lowercase=True, stop_words=None)
        texts = [candidate_skills, job_requirements]
        tfidf_matrix = vectorizer.fit_transform(texts)
        tfidf_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except Exception:
        tfidf_score = 0.0
    
    return (exact_score * 0.6) + (tfidf_score * 0.4)


def calculate_experience_score(profile, job):
    """Calcula score baseado em anos de experiencia."""
    candidate_exp = getattr(profile, 'experience_years', 0) or 0
    required_exp = job.experience_years or 0
    
    if required_exp == 0:
        return 1.0
    
    if candidate_exp >= required_exp:
        return 1.0
    elif candidate_exp >= required_exp * 0.7:
        return 0.8
    elif candidate_exp >= required_exp * 0.5:
        return 0.5
    else:
        return candidate_exp / required_exp if required_exp > 0 else 0.0


def calculate_location_score(profile, job):
    """Calcula score baseado em localizacao e modo de trabalho."""
    if job.work_mode == 'remote':
        return 1.0
    
    if hasattr(profile, 'get_full_location'):
        candidate_location = (profile.get_full_location() or '').lower().strip()
    else:
        candidate_location = (profile.location or '').lower().strip()
    job_location = (job.location or '').lower().strip()
    
    if not candidate_location or not job_location:
        return 0.5
    
    if candidate_location == job_location:
        return 1.0
    
    if candidate_location in job_location or job_location in candidate_location:
        return 0.8
    
    candidate_city = candidate_location.split(',')[0].strip()
    job_city = job_location.split(',')[0].strip()
    
    if candidate_city == job_city:
        return 0.9
    
    if job.work_mode == 'hybrid':
        return 0.5
    
    return 0.3


def calculate_salary_score(profile, job):
    """Calcula score baseado em compatibilidade salarial."""
    desired_salary = profile.desired_salary
    
    if not desired_salary:
        return 0.7
    
    if not job.salary_min and not job.salary_max:
        return 0.7
    
    salary_min = float(job.salary_min or 0)
    salary_max = float(job.salary_max or salary_min * 1.5 if salary_min else 0)
    desired = float(desired_salary)
    
    if salary_min <= desired <= salary_max:
        return 1.0
    
    if desired < salary_min:
        return 1.0
    
    if desired <= salary_max * 1.2:
        return 0.7
    elif desired <= salary_max * 1.5:
        return 0.4
    else:
        return 0.1


def get_matched_and_missing_skills(candidate, job):
    """Retorna listas de habilidades que o candidato possui e as que faltam."""
    if not hasattr(candidate, 'candidate_profile'):
        return [], []
    
    candidate_skills = set(candidate.candidate_profile.get_skills_list())
    job_requirements = set(job.get_requirements_list())
    
    matched = list(candidate_skills & job_requirements)
    missing = list(job_requirements - candidate_skills)
    
    return matched, missing


def get_recommended_jobs_for_candidate(candidate, limit=10):
    """Retorna vagas recomendadas para o candidato ordenadas por score."""
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
                'missing_skills': missing,
                'percentage': int(score * 100)
            })
    
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    try:
        from accounts.models import SiteMetrics
        SiteMetrics.increment('matches_created', len(recommendations))
    except Exception:
        pass
    
    return recommendations[:limit]


def get_recommended_candidates_for_job(job, limit=10):
    """Retorna candidatos recomendados para a vaga ordenados por score."""
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
                'missing_skills': missing,
                'percentage': int(score * 100)
            })
    
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations[:limit]


def get_skill_gaps(candidate):
    """Identifica habilidades em demanda que o candidato nao possui."""
    from jobs.models import Job
    
    if not hasattr(candidate, 'candidate_profile'):
        return []
    
    candidate_skills = set(candidate.candidate_profile.get_skills_list())
    skill_demand = {}
    
    popular_jobs = Job.objects.filter(is_active=True)[:100]
    for job in popular_jobs:
        for skill in job.get_requirements_list():
            if skill not in candidate_skills:
                skill_demand[skill] = skill_demand.get(skill, 0) + 1
    
    sorted_gaps = sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)
    
    return [skill for skill, count in sorted_gaps]
