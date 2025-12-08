import os
import re
import logging
from courses.models import Course
from jobs.models import Job
from match.utils import get_skill_gaps, get_recommended_jobs_for_candidate

logger = logging.getLogger(__name__)

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("Biblioteca Groq nao disponivel. Usando sistema de regras local.")


def get_groq_client():
    """Retorna cliente Groq se a API key estiver configurada."""
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        logger.debug("GROQ_API_KEY nao configurada")
        return None
    if not GROQ_AVAILABLE:
        logger.warning("Biblioteca Groq nao instalada")
        return None
    try:
        client = Groq(api_key=api_key)
        return client
    except Exception as e:
        logger.error(f"Erro ao criar cliente Groq: {e}")
        return None


def get_ai_response(user, message, session):
    """
    Gera resposta usando Groq AI quando disponivel,
    caso contrario usa o sistema de regras local.
    """
    groq_client = get_groq_client()
    
    if groq_client:
        response = get_groq_response(groq_client, user, message, session)
        if response:
            return response
    
    logger.info(f"Usando sistema de regras local para usuario {user.username}")
    return get_local_response(user, message)


def get_groq_response(client, user, message, session):
    """Gera resposta usando a API Groq."""
    try:
        context = build_user_context(user)
        
        history = session.messages.order_by('-created_at')[:10]
        messages = []
        
        system_prompt = f"""Voce e o assistente virtual do TalentMatch, uma plataforma de empregos com IA.
Seu objetivo e ajudar usuarios a encontrar vagas, melhorar seus curriculos e desenvolver suas carreiras.

Contexto do usuario:
{context}

Diretrizes:
- Responda sempre em portugues brasileiro
- Seja amigavel, profissional e objetivo
- Forneca dicas praticas e acionaveis
- Use emojis moderadamente para tornar a conversa mais amigavel
- Se o usuario perguntar sobre vagas ou cursos, baseie-se no contexto fornecido
- Para analise de curriculo, use as informacoes do perfil do usuario"""

        messages.append({"role": "system", "content": system_prompt})
        
        for msg in reversed(list(history)):
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        messages.append({"role": "user", "content": message})
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        
        try:
            from accounts.models import SiteMetrics
            SiteMetrics.increment('chat_messages')
        except Exception:
            pass
        
        logger.info(f"Resposta Groq gerada com sucesso para usuario {user.username}")
        return completion.choices[0].message.content
        
    except Exception as e:
        error_message = str(e).lower()
        
        if 'invalid_api_key' in error_message or 'authentication' in error_message:
            logger.error(f"Chave API Groq invalida: {e}")
            return "Desculpe, estou com problemas de configuracao. Por favor, tente novamente mais tarde ou entre em contato com o suporte."
        
        elif 'rate_limit' in error_message or 'too many requests' in error_message:
            logger.warning(f"Limite de requisicoes Groq atingido: {e}")
            return "Estou recebendo muitas mensagens no momento. Por favor, aguarde alguns segundos e tente novamente."
        
        elif 'connection' in error_message or 'network' in error_message or 'timeout' in error_message:
            logger.error(f"Erro de conexao com Groq: {e}")
            return get_local_response(user, message)
        
        else:
            logger.error(f"Erro inesperado na API Groq: {e}", exc_info=True)
            return get_local_response(user, message)


def build_user_context(user):
    """Constroi contexto do usuario para a IA."""
    context_parts = []
    
    context_parts.append(f"Nome: {user.get_full_name() or user.username}")
    context_parts.append(f"Tipo: {user.get_user_type_display()}")
    
    if user.is_candidate() and hasattr(user, 'candidate_profile'):
        profile = user.candidate_profile
        skills = profile.get_skills_list()
        context_parts.append(f"Habilidades: {', '.join(skills) if skills else 'Nenhuma cadastrada'}")
        context_parts.append(f"Experiencia: {profile.experience_years or 0} anos")
        location = profile.get_full_location() if hasattr(profile, 'get_full_location') else (profile.location or 'Nao informada')
        context_parts.append(f"Localizacao: {location}")
        if hasattr(profile, 'interest_area') and profile.interest_area:
            context_parts.append(f"Area de Interesse: {profile.interest_area}")
        context_parts.append(f"Disponivel: {'Sim' if profile.available else 'Nao'}")
        
        skill_gaps = get_skill_gaps(user)[:5]
        if skill_gaps:
            context_parts.append(f"Habilidades em demanda que faltam: {', '.join(skill_gaps)}")
        
        recommendations = get_recommended_jobs_for_candidate(user, limit=3)
        if recommendations:
            jobs_text = []
            for rec in recommendations:
                job = rec['job']
                company_name = job.company.company_profile.company_name if hasattr(job.company, 'company_profile') else 'Empresa'
                jobs_text.append(f"- {job.title} ({company_name}) - {rec['percentage']}% match")
            context_parts.append(f"Vagas recomendadas:\n" + "\n".join(jobs_text))
    
    elif user.is_company() and hasattr(user, 'company_profile'):
        company = user.company_profile
        context_parts.append(f"Empresa: {company.company_name}")
        context_parts.append(f"Setor: {company.industry or 'Nao informado'}")
        
        jobs_count = Job.objects.filter(company=user, is_active=True).count()
        context_parts.append(f"Vagas ativas: {jobs_count}")
    
    return "\n".join(context_parts)


def get_local_response(user, message):
    """Sistema de regras local quando Groq nao esta disponivel."""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['curriculo', 'cv', 'resume', 'perfil']):
        return analyze_resume(user, message)
    
    if any(word in message_lower for word in ['curso', 'estudar', 'aprender', 'treinamento']):
        return recommend_courses(user, message)
    
    if any(word in message_lower for word in ['vaga', 'emprego', 'trabalho', 'job', 'oportunidade']):
        return recommend_jobs(user, message)
    
    if any(word in message_lower for word in ['habilidade', 'skill', 'competencia', 'falta', 'melhorar']):
        return analyze_skills(user, message)
    
    if any(word in message_lower for word in ['ola', 'oi', 'bom dia', 'boa tarde', 'boa noite', 'hello', 'hi']):
        return get_greeting(user)
    
    if any(word in message_lower for word in ['ajuda', 'help', 'como', 'o que', 'pode']):
        return get_help_message()
    
    if any(word in message_lower for word in ['perfil', 'sobre mim', 'meu', 'minhas']):
        return get_profile_summary(user)
    
    return get_default_response(user)


def get_greeting(user):
    name = user.first_name or user.username
    return f"""Ola, {name}! 

Sou o assistente virtual do TalentMatch e estou aqui para ajudar voce!

Posso te ajudar com:
- **Analise de curriculo** - Avalio seu perfil e dou dicas de melhoria
- **Vagas recomendadas** - Encontro oportunidades que combinam com voce
- **Cursos sugeridos** - Identifico habilidades para desenvolver
- **Dicas de carreira** - Oriento sobre sua jornada profissional

Como posso ajudar voce hoje?"""


def get_help_message():
    return """Posso te ajudar de varias formas! Experimente perguntar:

**Sobre curriculo:**
- "Analise meu curriculo"
- "Como posso melhorar meu CV?"
- "O que esta faltando no meu perfil?"

**Sobre vagas:**
- "Quais vagas combinam comigo?"
- "Me mostre oportunidades de emprego"
- "Busco uma vaga de desenvolvedor"

**Sobre cursos:**
- "Que cursos devo fazer?"
- "Quero aprender programacao"
- "Recomende treinamentos para mim"

**Sobre habilidades:**
- "Quais habilidades estao em falta?"
- "Como desenvolver minha carreira?"

E so digitar sua pergunta!"""


def analyze_resume(user, message):
    if not user.is_candidate():
        return "Este recurso esta disponivel apenas para candidatos. Complete seu cadastro como candidato para utilizar."
    
    if not hasattr(user, 'candidate_profile'):
        return "Voce ainda nao completou seu perfil. Acesse a pagina de perfil e preencha suas informacoes!"
    
    profile = user.candidate_profile
    suggestions = []
    score = 0
    
    if profile.bio and len(profile.bio) > 50:
        score += 15
    else:
        suggestions.append("Adicione uma biografia mais completa (minimo 50 caracteres)")
    
    skills_list = profile.get_skills_list()
    if len(skills_list) >= 5:
        score += 25
    elif len(skills_list) >= 3:
        score += 15
        suggestions.append("Adicione mais habilidades (recomendamos pelo menos 5)")
    else:
        suggestions.append("Seu perfil precisa de mais habilidades tecnicas")
    
    if profile.experience and len(profile.experience) > 100:
        score += 20
    else:
        suggestions.append("Detalhe mais sua experiencia profissional")
    
    if profile.education and len(profile.education) > 50:
        score += 15
    else:
        suggestions.append("Adicione informacoes sobre sua formacao academica")
    
    if profile.resume:
        score += 15
    else:
        suggestions.append("Faca upload do seu curriculo em PDF")
    
    if profile.linkedin_url or profile.github_url:
        score += 10
    else:
        suggestions.append("Adicione links para LinkedIn ou GitHub")
    
    response = f"""**Analise do seu Curriculo**

**Pontuacao geral:** {score}/100

**Habilidades cadastradas:** {', '.join(skills_list) if skills_list else 'Nenhuma'}

"""
    
    if suggestions:
        response += "**Sugestoes de melhoria:**\n"
        for s in suggestions:
            response += f"- {s}\n"
    else:
        response += "Seu perfil esta muito completo! Continue assim!"
    
    skill_gaps = get_skill_gaps(user)
    if skill_gaps[:5]:
        response += f"\n**Habilidades em alta no mercado que voce pode desenvolver:**\n"
        for skill in skill_gaps[:5]:
            response += f"- {skill}\n"
    
    return response


def recommend_courses(user, message):
    if not user.is_candidate():
        courses = Course.objects.filter(is_active=True)[:5]
        response = "**Cursos disponiveis:**\n\n"
        for course in courses:
            response += f"- **{course.title}** - {course.get_level_display()} ({course.duration_hours}h)\n"
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
        response = "**Cursos recomendados para voce:**\n\n"
        for item in recommended[:5]:
            course = item['course']
            skills = ', '.join(item['skills'][:3])
            response += f"- **{course.title}**\n"
            response += f"  Nivel: {course.get_level_display()} | {course.duration_hours}h\n"
            response += f"  Desenvolve: {skills}\n\n"
    else:
        response = "Nao encontrei cursos especificos para suas necessidades no momento.\n\n"
        response += "Visite nossa pagina de cursos para ver todas as opcoes disponiveis!"
    
    return response


def recommend_jobs(user, message):
    if not user.is_candidate():
        jobs = Job.objects.filter(is_active=True)[:5]
        response = "**Vagas disponiveis:**\n\n"
        for job in jobs:
            company = job.company.company_profile.company_name if hasattr(job.company, 'company_profile') else 'Empresa'
            response += f"- **{job.title}** - {company}\n  {job.location} | {job.get_job_type_display()}\n\n"
        return response
    
    recommendations = get_recommended_jobs_for_candidate(user, limit=5)
    
    if recommendations:
        response = "**Vagas que combinam com seu perfil:**\n\n"
        for rec in recommendations:
            job = rec['job']
            score = rec['score']
            company = job.company.company_profile.company_name if hasattr(job.company, 'company_profile') else 'Empresa'
            response += f"- **{job.title}** - {company}\n"
            response += f"  Match: {int(score * 100)}% | {job.location} | {job.get_job_type_display()}\n"
            if rec['matched_skills'][:3]:
                response += f"  Skills em comum: {', '.join(rec['matched_skills'][:3])}\n"
            response += "\n"
    else:
        response = "Ainda nao encontrei vagas que combinem com seu perfil.\n\n"
        response += "Dicas:\n- Complete seu perfil com mais habilidades\n- Adicione sua experiencia profissional"
    
    return response


def analyze_skills(user, message):
    if not user.is_candidate():
        return "Este recurso esta disponivel apenas para candidatos."
    
    if not hasattr(user, 'candidate_profile'):
        return "Complete seu perfil primeiro para receber analise de habilidades."
    
    profile = user.candidate_profile
    current_skills = profile.get_skills_list()
    skill_gaps = get_skill_gaps(user)
    
    response = "**Analise de Habilidades**\n\n"
    
    if current_skills:
        response += "**Suas habilidades atuais:**\n"
        response += ", ".join(current_skills) + "\n\n"
    else:
        response += "Voce ainda nao cadastrou habilidades no seu perfil.\n\n"
    
    if skill_gaps[:8]:
        response += "**Habilidades em demanda que voce pode desenvolver:**\n"
        for skill in skill_gaps[:8]:
            response += f"- {skill}\n"
        response += "\nEssas sao as habilidades mais requisitadas nas vagas atuais!"
    
    return response


def get_profile_summary(user):
    if not user.is_candidate():
        if user.is_company():
            if hasattr(user, 'company_profile'):
                company = user.company_profile
                return f"""**Perfil da Empresa**

**Nome:** {company.company_name}
**Setor:** {company.industry or 'Nao informado'}
**Localizacao:** {company.location or 'Nao informado'}
**Tamanho:** {company.get_size_display() if company.size else 'Nao informado'}
**Status:** {company.get_verification_status_display()}

Acesse seu painel para gerenciar suas vagas e ver candidatos!"""
        return "Acesse seu perfil para ver e editar suas informacoes."
    
    if not hasattr(user, 'candidate_profile'):
        return "Complete seu perfil para ver um resumo das suas informacoes!"
    
    profile = user.candidate_profile
    skills = profile.get_skills_list()
    
    return f"""**Seu Perfil**

**Nome:** {user.get_full_name() or user.username}
**Email:** {user.email}
**Localizacao:** {profile.location or 'Nao informado'}
**Disponivel:** {'Sim' if profile.available else 'Nao'}

**Habilidades:** {', '.join(skills) if skills else 'Nenhuma cadastrada'}

**Curriculo:** {'Enviado' if profile.resume else 'Nao enviado'}
**LinkedIn:** {'Configurado' if profile.linkedin_url else 'Nao configurado'}
**GitHub:** {'Configurado' if profile.github_url else 'Nao configurado'}

Acesse seu perfil para atualizar suas informacoes!"""


def get_default_response(user):
    return """Desculpe, nao entendi bem sua pergunta.

Posso te ajudar com:
- **Analise de curriculo** - Digite "analise meu curriculo"
- **Vagas recomendadas** - Digite "me mostre vagas"
- **Cursos sugeridos** - Digite "recomende cursos"
- **Analise de habilidades** - Digite "quais habilidades preciso?"

Ou simplesmente me pergunte o que voce gostaria de saber!"""
