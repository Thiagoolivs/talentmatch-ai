import re
from courses.models import Course
from jobs.models import Job
from match.utils import get_skill_gaps, get_recommended_jobs_for_candidate


def get_ai_response(user, message, session):
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['currículo', 'curriculo', 'cv', 'resume']):
        return analyze_resume(user, message)
    
    if any(word in message_lower for word in ['curso', 'estudar', 'aprender', 'treinamento']):
        return recommend_courses(user, message)
    
    if any(word in message_lower for word in ['vaga', 'emprego', 'trabalho', 'job', 'oportunidade']):
        return recommend_jobs(user, message)
    
    if any(word in message_lower for word in ['habilidade', 'skill', 'competência', 'falta', 'melhorar']):
        return analyze_skills(user, message)
    
    if any(word in message_lower for word in ['olá', 'oi', 'bom dia', 'boa tarde', 'boa noite', 'hello', 'hi']):
        return get_greeting(user)
    
    if any(word in message_lower for word in ['ajuda', 'help', 'como', 'o que', 'pode']):
        return get_help_message()
    
    if any(word in message_lower for word in ['perfil', 'sobre mim', 'meu', 'minhas']):
        return get_profile_summary(user)
    
    return get_default_response(user)


def get_greeting(user):
    name = user.first_name or user.username
    return f"""Olá, {name}! 👋

Sou o assistente virtual do TalentMatch e estou aqui para ajudar você!

Posso te ajudar com:
• 📄 **Análise de currículo** - Avalio seu perfil e dou dicas de melhoria
• 🎯 **Vagas recomendadas** - Encontro oportunidades que combinam com você
• 📚 **Cursos sugeridos** - Identifico habilidades para desenvolver
• 💡 **Dicas de carreira** - Oriento sobre sua jornada profissional

Como posso ajudar você hoje?"""


def get_help_message():
    return """Posso te ajudar de várias formas! Experimente perguntar:

📄 **Sobre currículo:**
- "Analise meu currículo"
- "Como posso melhorar meu CV?"
- "O que está faltando no meu perfil?"

🎯 **Sobre vagas:**
- "Quais vagas combinam comigo?"
- "Me mostre oportunidades de emprego"
- "Busco uma vaga de desenvolvedor"

📚 **Sobre cursos:**
- "Que cursos devo fazer?"
- "Quero aprender programação"
- "Recomende treinamentos para mim"

💡 **Sobre habilidades:**
- "Quais habilidades estão em falta?"
- "Como desenvolver minha carreira?"

É só digitar sua pergunta!"""


def analyze_resume(user, message):
    if not user.is_candidate():
        return "Este recurso está disponível apenas para candidatos. Complete seu cadastro como candidato para utilizar."
    
    if not hasattr(user, 'candidate_profile'):
        return "Você ainda não completou seu perfil. Acesse a página de perfil e preencha suas informações!"
    
    profile = user.candidate_profile
    suggestions = []
    score = 0
    
    if profile.bio and len(profile.bio) > 50:
        score += 15
    else:
        suggestions.append("📝 Adicione uma biografia mais completa (mínimo 50 caracteres)")
    
    skills_list = profile.get_skills_list()
    if len(skills_list) >= 5:
        score += 25
    elif len(skills_list) >= 3:
        score += 15
        suggestions.append("💼 Adicione mais habilidades (recomendamos pelo menos 5)")
    else:
        suggestions.append("💼 Seu perfil precisa de mais habilidades técnicas")
    
    if profile.experience and len(profile.experience) > 100:
        score += 20
    else:
        suggestions.append("🏢 Detalhe mais sua experiência profissional")
    
    if profile.education and len(profile.education) > 50:
        score += 15
    else:
        suggestions.append("🎓 Adicione informações sobre sua formação acadêmica")
    
    if profile.resume:
        score += 15
    else:
        suggestions.append("📎 Faça upload do seu currículo em PDF")
    
    if profile.linkedin_url or profile.github_url:
        score += 10
    else:
        suggestions.append("🔗 Adicione links para LinkedIn ou GitHub")
    
    response = f"""**Análise do seu Currículo** 📊

**Pontuação geral:** {score}/100

**Habilidades cadastradas:** {', '.join(skills_list) if skills_list else 'Nenhuma'}

"""
    
    if suggestions:
        response += "**Sugestões de melhoria:**\n"
        for s in suggestions:
            response += f"• {s}\n"
    else:
        response += "✅ Seu perfil está muito completo! Continue assim!"
    
    skill_gaps = get_skill_gaps(user)
    if skill_gaps[:5]:
        response += f"\n**Habilidades em alta no mercado que você pode desenvolver:**\n"
        for skill in skill_gaps[:5]:
            response += f"• {skill}\n"
    
    return response


def recommend_courses(user, message):
    if not user.is_candidate():
        courses = Course.objects.filter(is_active=True)[:5]
        response = "**Cursos disponíveis:**\n\n"
        for course in courses:
            response += f"• **{course.title}** - {course.get_level_display()} ({course.duration_hours}h)\n"
        return response
    
    skill_gaps = get_skill_gaps(user)
    recommended = []
    
    for course in Course.objects.filter(is_active=True):
        course_skills = course.get_skills_list()
        matching = [s for s in skill_gaps if s in course_skills]
        if matching:
            recommended.append({
                'course': course,
                'skills': matching
            })
    
    recommended.sort(key=lambda x: len(x['skills']), reverse=True)
    
    if recommended:
        response = "**Cursos recomendados para você:** 📚\n\n"
        for item in recommended[:5]:
            course = item['course']
            skills = ', '.join(item['skills'][:3])
            response += f"• **{course.title}**\n"
            response += f"  Nível: {course.get_level_display()} | {course.duration_hours}h\n"
            response += f"  Desenvolve: {skills}\n\n"
    else:
        response = "Não encontrei cursos específicos para suas necessidades no momento.\n\n"
        response += "Visite nossa página de cursos para ver todas as opções disponíveis!"
    
    return response


def recommend_jobs(user, message):
    if not user.is_candidate():
        jobs = Job.objects.filter(is_active=True)[:5]
        response = "**Vagas disponíveis:**\n\n"
        for job in jobs:
            company = job.company.company_profile.company_name if hasattr(job.company, 'company_profile') else 'Empresa'
            response += f"• **{job.title}** - {company}\n  {job.location} | {job.get_job_type_display()}\n\n"
        return response
    
    recommendations = get_recommended_jobs_for_candidate(user, limit=5)
    
    if recommendations:
        response = "**Vagas que combinam com seu perfil:** 🎯\n\n"
        for rec in recommendations:
            job = rec['job']
            score = rec['score']
            company = job.company.company_profile.company_name if hasattr(job.company, 'company_profile') else 'Empresa'
            response += f"• **{job.title}** - {company}\n"
            response += f"  Match: {int(score * 100)}% | {job.location} | {job.get_job_type_display()}\n"
            if rec['matched_skills'][:3]:
                response += f"  Skills em comum: {', '.join(rec['matched_skills'][:3])}\n"
            response += "\n"
    else:
        response = "Ainda não encontrei vagas que combinem com seu perfil.\n\n"
        response += "Dicas:\n• Complete seu perfil com mais habilidades\n• Adicione sua experiência profissional"
    
    return response


def analyze_skills(user, message):
    if not user.is_candidate():
        return "Este recurso está disponível apenas para candidatos."
    
    if not hasattr(user, 'candidate_profile'):
        return "Complete seu perfil primeiro para receber análise de habilidades."
    
    profile = user.candidate_profile
    current_skills = profile.get_skills_list()
    skill_gaps = get_skill_gaps(user)
    
    response = "**Análise de Habilidades** 💡\n\n"
    
    if current_skills:
        response += "**Suas habilidades atuais:**\n"
        response += ", ".join(current_skills) + "\n\n"
    else:
        response += "⚠️ Você ainda não cadastrou habilidades no seu perfil.\n\n"
    
    if skill_gaps[:8]:
        response += "**Habilidades em demanda que você pode desenvolver:**\n"
        for skill in skill_gaps[:8]:
            response += f"• {skill}\n"
        response += "\nEssas são as habilidades mais requisitadas nas vagas atuais!"
    
    return response


def get_profile_summary(user):
    if not user.is_candidate():
        if user.is_company():
            if hasattr(user, 'company_profile'):
                company = user.company_profile
                return f"""**Perfil da Empresa** 🏢

**Nome:** {company.company_name}
**Setor:** {company.industry or 'Não informado'}
**Localização:** {company.location or 'Não informado'}
**Tamanho:** {company.get_size_display() if company.size else 'Não informado'}

Acesse seu painel para gerenciar suas vagas e ver candidatos!"""
        return "Acesse seu perfil para ver e editar suas informações."
    
    if not hasattr(user, 'candidate_profile'):
        return "Complete seu perfil para ver um resumo das suas informações!"
    
    profile = user.candidate_profile
    skills = profile.get_skills_list()
    
    return f"""**Seu Perfil** 👤

**Nome:** {user.get_full_name() or user.username}
**Email:** {user.email}
**Localização:** {profile.location or 'Não informado'}
**Disponível:** {'Sim' if profile.available else 'Não'}

**Habilidades:** {', '.join(skills) if skills else 'Nenhuma cadastrada'}

**Currículo:** {'✅ Enviado' if profile.resume else '❌ Não enviado'}
**LinkedIn:** {'✅' if profile.linkedin_url else '❌'}
**GitHub:** {'✅' if profile.github_url else '❌'}

Acesse seu perfil para atualizar suas informações!"""


def get_default_response(user):
    return """Desculpe, não entendi bem sua pergunta. 🤔

Posso te ajudar com:
• **Análise de currículo** - Digite "analise meu currículo"
• **Vagas recomendadas** - Digite "me mostre vagas"
• **Cursos sugeridos** - Digite "recomende cursos"
• **Análise de habilidades** - Digite "quais habilidades preciso?"

Ou simplesmente me pergunte o que você gostaria de saber!"""
