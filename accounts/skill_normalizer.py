import unicodedata
import re
import logging
from difflib import SequenceMatcher
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.8


def remove_accents(text: str) -> str:
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd_form if not unicodedata.combining(c))


def normalize_text(text: str) -> str:
    text = remove_accents(text)
    text = text.strip().lower()
    text = re.sub(r'[^\w\s\-\+\#\.\/]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def calculate_similarity(s1: str, s2: str) -> float:
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()


def find_canonical_skill(skill_term: str, user=None) -> Tuple[str, float, bool]:
    from accounts.models import CanonicalSkill, SkillCorrectionLog
    
    normalized = normalize_text(skill_term)
    
    if not normalized:
        return skill_term, 0.0, False
    
    try:
        exact_match = CanonicalSkill.objects.filter(
            name__iexact=normalized,
            is_active=True
        ).first()
        
        if exact_match:
            return exact_match.name, 1.0, True
    except Exception as e:
        logger.error(f"Error checking exact match for skill '{skill_term}': {e}")
    
    best_match = None
    best_score = 0.0
    
    try:
        canonical_skills = CanonicalSkill.objects.filter(is_active=True)
        
        for skill in canonical_skills:
            score = calculate_similarity(normalized, skill.name)
            if score > best_score:
                best_score = score
                best_match = skill.name
            
            for alias in skill.get_aliases_list():
                alias_score = calculate_similarity(normalized, alias)
                if alias_score > best_score:
                    best_score = alias_score
                    best_match = skill.name
    except Exception as e:
        logger.error(f"Error finding canonical skill for '{skill_term}': {e}")
        return skill_term, 0.0, False
    
    was_corrected = False
    if best_score >= SIMILARITY_THRESHOLD and best_match:
        corrected_term = best_match
        was_corrected = True
    else:
        corrected_term = normalized
        was_corrected = False
    
    try:
        SkillCorrectionLog.objects.create(
            original_term=skill_term[:100],
            corrected_term=corrected_term[:100] if was_corrected else '',
            similarity_score=best_score,
            was_auto_corrected=was_corrected,
            needs_review=not was_corrected and best_score > 0.5,
            user=user
        )
    except Exception as e:
        logger.error(f"Error logging skill correction for '{skill_term}': {e}")
    
    return corrected_term, best_score, was_corrected


def normalize_skills_string(skills_string: str, user=None) -> str:
    if not skills_string:
        return ''
    
    skills = [s.strip() for s in skills_string.split(',') if s.strip()]
    normalized_skills = []
    correction_count = 0
    
    for skill in skills:
        canonical, score, was_corrected = find_canonical_skill(skill, user)
        normalized_skills.append(canonical)
        if was_corrected:
            correction_count += 1
    
    if correction_count > 0:
        logger.info(f"Auto-corrected {correction_count} skills for user {user}")
    
    unique_skills = list(dict.fromkeys(normalized_skills))
    return ', '.join(unique_skills)


def get_correction_stats() -> dict:
    from accounts.models import SkillCorrectionLog
    from django.db.models import Count, Avg
    
    try:
        stats = {
            'total_corrections': SkillCorrectionLog.objects.count(),
            'auto_corrected': SkillCorrectionLog.objects.filter(was_auto_corrected=True).count(),
            'needs_review': SkillCorrectionLog.objects.filter(needs_review=True).count(),
            'avg_similarity': SkillCorrectionLog.objects.aggregate(Avg('similarity_score'))['similarity_score__avg'] or 0,
            'recent_corrections': list(
                SkillCorrectionLog.objects.order_by('-created_at')[:10].values(
                    'original_term', 'corrected_term', 'was_auto_corrected', 'created_at'
                )
            )
        }
        return stats
    except Exception as e:
        logger.error(f"Error getting correction stats: {e}")
        return {}
