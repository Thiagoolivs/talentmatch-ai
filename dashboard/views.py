from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Sum, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from jobs.models import Job, Application
from courses.models import Course, UserCourse
from accounts.models import (
    User, CandidateProfile, CompanyProfile, 
    ProblemReport, SiteSettings, SiteMetrics,
    AuditLog, Notification
)
from match.utils import get_recommended_jobs_for_candidate, get_skill_gaps
from chatbot.models import ChatSession, ChatMessage
from messaging.models import Message


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
    
    company_verified = False
    if hasattr(user, 'company_profile'):
        company_verified = user.company_profile.is_verified()
    
    return render(request, 'dashboard/company.html', {
        'total_jobs': jobs.count(),
        'active_jobs': active_jobs.count(),
        'total_applications': total_applications,
        'jobs_with_stats': jobs_with_stats,
        'recent_applications': recent_applications,
        'status_distribution': status_distribution,
        'company_verified': company_verified,
    })


def admin_dashboard(request):
    """Dashboard administrativo completo."""
    if not request.user.is_admin_user():
        messages.error(request, 'Acesso negado.')
        return redirect('core:home')
    
    total_users = User.objects.count()
    total_candidates = User.objects.filter(user_type='candidate').count()
    total_companies = User.objects.filter(user_type='company').count()
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(is_active=True).count()
    total_applications = Application.objects.count()
    total_courses = Course.objects.count()
    
    pending_companies = CompanyProfile.objects.filter(verification_status='pending').count()
    open_problems = ProblemReport.objects.filter(status__in=['open', 'in_progress']).count()
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    new_users_week = User.objects.filter(created_at__date__gte=week_ago).count()
    new_jobs_week = Job.objects.filter(created_at__date__gte=week_ago).count()
    new_applications_week = Application.objects.filter(applied_at__date__gte=week_ago).count()
    
    chat_messages_count = ChatMessage.objects.count()
    total_messages = Message.objects.count()
    
    recent_users = User.objects.order_by('-created_at')[:10]
    recent_jobs = Job.objects.select_related('company__company_profile').order_by('-created_at')[:10]
    recent_applications = Application.objects.select_related(
        'candidate', 'job__company__company_profile'
    ).order_by('-applied_at')[:10]
    
    applications_by_status = {
        'submitted': Application.objects.filter(status='submitted').count(),
        'analyzing': Application.objects.filter(status='analyzing').count(),
        'preselected': Application.objects.filter(status='preselected').count(),
        'rejected': Application.objects.filter(status='rejected').count(),
        'hired': Application.objects.filter(status='hired').count(),
    }
    
    recent_problems = ProblemReport.objects.select_related('user').order_by('-created_at')[:5]
    pending_companies_list = CompanyProfile.objects.filter(
        verification_status='pending'
    ).select_related('user')[:5]
    
    site_settings = SiteSettings.get_settings()
    
    metrics_7_days = SiteMetrics.objects.filter(date__gte=week_ago).order_by('date')
    
    return render(request, 'dashboard/admin.html', {
        'total_users': total_users,
        'total_candidates': total_candidates,
        'total_companies': total_companies,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'total_courses': total_courses,
        'pending_companies': pending_companies,
        'open_problems': open_problems,
        'new_users_week': new_users_week,
        'new_jobs_week': new_jobs_week,
        'new_applications_week': new_applications_week,
        'chat_messages_count': chat_messages_count,
        'total_messages': total_messages,
        'recent_users': recent_users,
        'recent_jobs': recent_jobs,
        'recent_applications': recent_applications,
        'applications_by_status': applications_by_status,
        'recent_problems': recent_problems,
        'pending_companies_list': pending_companies_list,
        'site_settings': site_settings,
        'metrics_7_days': metrics_7_days,
    })


@login_required
def admin_companies(request):
    """Gerenciamento de empresas pendentes de verificacao."""
    if not request.user.is_admin_user():
        messages.error(request, 'Acesso negado.')
        return redirect('core:home')
    
    status_filter = request.GET.get('status', 'pending')
    
    companies = CompanyProfile.objects.select_related('user')
    if status_filter != 'all':
        companies = companies.filter(verification_status=status_filter)
    
    companies = companies.order_by('-user__created_at')
    
    return render(request, 'dashboard/admin_companies.html', {
        'companies': companies,
        'status_filter': status_filter,
    })


@login_required
@require_POST
def verify_company(request, company_id):
    """Aprova ou rejeita uma empresa."""
    if not request.user.is_admin_user():
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    company = get_object_or_404(CompanyProfile, id=company_id)
    action = request.POST.get('action')
    notes = request.POST.get('notes', '')
    old_status = company.verification_status
    
    ip_address = request.META.get('REMOTE_ADDR')
    
    if action == 'approve':
        company.verification_status = 'approved'
        company.verification_date = timezone.now()
        company.verification_notes = notes
        company.save()
        
        AuditLog.log_action(
            user=request.user,
            action='approve',
            model_name='CompanyProfile',
            object_id=company.id,
            object_repr=company.company_name,
            details={'old_status': old_status, 'notes': notes},
            ip_address=ip_address
        )
        
        Notification.notify_user(
            user=company.user,
            notification_type='company_approved',
            title='Empresa Aprovada!',
            message=f'Parabens! Sua empresa "{company.company_name}" foi aprovada. Agora voce pode publicar vagas e ver candidaturas.',
            link='/dashboard/'
        )
        
        messages.success(request, f'Empresa {company.company_name} aprovada com sucesso.')
    elif action == 'reject':
        company.verification_status = 'rejected'
        company.verification_date = timezone.now()
        company.verification_notes = notes
        company.save()
        
        AuditLog.log_action(
            user=request.user,
            action='reject',
            model_name='CompanyProfile',
            object_id=company.id,
            object_repr=company.company_name,
            details={'old_status': old_status, 'notes': notes},
            ip_address=ip_address
        )
        
        Notification.notify_user(
            user=company.user,
            notification_type='company_rejected',
            title='Empresa Rejeitada',
            message=f'Infelizmente sua empresa "{company.company_name}" foi rejeitada. Motivo: {notes or "Nao informado"}',
            link='/accounts/profile/'
        )
        
        messages.warning(request, f'Empresa {company.company_name} foi rejeitada.')
    
    return redirect('dashboard:admin_companies')


@login_required
def admin_problems(request):
    """Gerenciamento de problemas reportados."""
    if not request.user.is_admin_user():
        messages.error(request, 'Acesso negado.')
        return redirect('core:home')
    
    status_filter = request.GET.get('status', 'open')
    category_filter = request.GET.get('category', '')
    
    problems = ProblemReport.objects.select_related('user', 'resolved_by')
    
    if status_filter != 'all':
        problems = problems.filter(status=status_filter)
    if category_filter:
        problems = problems.filter(category=category_filter)
    
    problems = problems.order_by('-created_at')
    
    return render(request, 'dashboard/admin_problems.html', {
        'problems': problems,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'categories': ProblemReport.CATEGORY_CHOICES,
    })


@login_required
@require_POST
def update_problem(request, problem_id):
    """Atualiza status de um problema."""
    if not request.user.is_admin_user():
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    problem = get_object_or_404(ProblemReport, id=problem_id)
    new_status = request.POST.get('status')
    notes = request.POST.get('notes', '')
    
    if new_status in dict(ProblemReport.STATUS_CHOICES):
        problem.status = new_status
        problem.admin_notes = notes
        
        if new_status in ['resolved', 'closed']:
            problem.resolved_at = timezone.now()
            problem.resolved_by = request.user
        
        problem.save()
        messages.success(request, 'Problema atualizado com sucesso.')
    
    return redirect('dashboard:admin_problems')


@login_required
@require_POST
def toggle_maintenance(request):
    """Ativa/desativa modo de manutencao."""
    if not request.user.is_admin_user():
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    settings = SiteSettings.get_settings()
    settings.maintenance_mode = not settings.maintenance_mode
    settings.updated_by = request.user
    
    if settings.maintenance_mode:
        message = request.POST.get('message', '')
        if message:
            settings.maintenance_message = message
    
    settings.save()
    
    ip_address = request.META.get('REMOTE_ADDR')
    action = 'maintenance_on' if settings.maintenance_mode else 'maintenance_off'
    AuditLog.log_action(
        user=request.user,
        action=action,
        model_name='SiteSettings',
        object_id=1,
        object_repr='Modo Manutencao',
        details={'message': settings.maintenance_message if settings.maintenance_mode else ''},
        ip_address=ip_address
    )
    
    status = 'ativado' if settings.maintenance_mode else 'desativado'
    messages.success(request, f'Modo de manutencao {status}.')
    
    return redirect('dashboard:index')


@login_required
def report_problem(request):
    """Pagina para reportar um problema."""
    if request.method == 'POST':
        category = request.POST.get('category')
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        if category and title and description:
            ProblemReport.objects.create(
                user=request.user,
                category=category,
                title=title,
                description=description
            )
            messages.success(request, 'Problema reportado com sucesso. Nossa equipe ira analisar.')
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Preencha todos os campos.')
    
    return render(request, 'dashboard/report_problem.html', {
        'categories': ProblemReport.CATEGORY_CHOICES,
    })


@login_required
def my_problems(request):
    """Lista problemas reportados pelo usuario."""
    problems = ProblemReport.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'dashboard/my_problems.html', {
        'problems': problems,
    })


@login_required
def admin_users(request):
    """Gerenciamento de usuarios para administradores."""
    if not request.user.is_admin_user():
        messages.error(request, 'Acesso negado.')
        return redirect('core:home')
    
    users = User.objects.all().order_by('-created_at')
    
    search = request.GET.get('search', '').strip()
    if search:
        search_query = (
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
        if search.isdigit():
            search_query = search_query | Q(id=int(search))
        users = users.filter(search_query)
    
    user_type_filter = request.GET.get('user_type', '')
    if user_type_filter:
        users = users.filter(user_type=user_type_filter)
    
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    from django.core.paginator import Paginator
    paginator = Paginator(users, 20)
    page = request.GET.get('page', 1)
    users_page = paginator.get_page(page)
    
    return render(request, 'dashboard/admin_users.html', {
        'users': users_page,
        'search': search,
        'user_type_filter': user_type_filter,
        'status_filter': status_filter,
        'user_types': User.USER_TYPE_CHOICES,
    })


@login_required
@require_POST
def delete_user(request, user_id):
    """Exclui um usuario (soft delete - desativa a conta)."""
    if not request.user.is_admin_user():
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        messages.error(request, 'Voce nao pode excluir sua propria conta.')
        return redirect('dashboard:admin_users')
    
    if user.is_superuser:
        messages.error(request, 'Nao e possivel excluir um superusuario.')
        return redirect('dashboard:admin_users')
    
    action = request.POST.get('action', 'soft')
    ip_address = request.META.get('REMOTE_ADDR')
    
    if action == 'hard':
        username = user.username
        user_id_deleted = user.id
        
        AuditLog.log_action(
            user=request.user,
            action='delete',
            model_name='User',
            object_id=user_id_deleted,
            object_repr=username,
            details={'action': 'hard_delete', 'user_type': user.user_type},
            ip_address=ip_address
        )
        
        user.delete()
        messages.success(request, f'Usuario {username} excluido permanentemente.')
    else:
        user.is_active = False
        user.save()
        
        AuditLog.log_action(
            user=request.user,
            action='update',
            model_name='User',
            object_id=user.id,
            object_repr=user.username,
            details={'action': 'soft_delete', 'is_active': False},
            ip_address=ip_address
        )
        
        messages.success(request, f'Usuario {user.username} desativado.')
    
    return redirect('dashboard:admin_users')


@login_required
@require_POST
def toggle_user_active(request, user_id):
    """Ativa/desativa um usuario."""
    if not request.user.is_admin_user():
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        messages.error(request, 'Voce nao pode desativar sua propria conta.')
        return redirect('dashboard:admin_users')
    
    user.is_active = not user.is_active
    user.save()
    
    ip_address = request.META.get('REMOTE_ADDR')
    AuditLog.log_action(
        user=request.user,
        action='update',
        model_name='User',
        object_id=user.id,
        object_repr=user.username,
        details={'is_active': user.is_active},
        ip_address=ip_address
    )
    
    status = 'ativado' if user.is_active else 'desativado'
    messages.success(request, f'Usuario {user.username} {status}.')
    
    return redirect('dashboard:admin_users')
