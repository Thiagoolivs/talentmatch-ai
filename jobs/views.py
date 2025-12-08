from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Job, Application
from .forms import JobForm, ApplicationForm, ApplicationStatusForm
from .filters import JobFilter
from match.utils import calculate_match_score


def job_list(request):
    jobs = Job.objects.filter(is_active=True).select_related('company__company_profile')
    job_filter = JobFilter(request.GET, queryset=jobs)
    
    paginator = Paginator(job_filter.qs, 10)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'filter': job_filter
    })


def job_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related('company__company_profile'), pk=pk)
    has_applied = False
    match_score = None
    
    if request.user.is_authenticated and request.user.is_candidate():
        has_applied = Application.objects.filter(job=job, candidate=request.user).exists()
        if hasattr(request.user, 'candidate_profile'):
            match_score = calculate_match_score(request.user, job)
    
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'has_applied': has_applied,
        'match_score': match_score
    })


@login_required
def job_create(request):
    if not request.user.is_company():
        messages.error(request, 'Apenas empresas podem criar vagas.')
        return redirect('jobs:list')
    
    if hasattr(request.user, 'company_profile') and not request.user.company_profile.is_verified():
        messages.error(request, 'Sua empresa precisa ser aprovada antes de publicar vagas.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user
            job.save()
            messages.success(request, 'Vaga criada com sucesso!')
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobForm()
    
    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'Criar Vaga'})


@login_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk, company=request.user)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vaga atualizada com sucesso!')
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobForm(instance=job)
    
    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'Editar Vaga', 'job': job})


@login_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk, company=request.user)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Vaga excluída com sucesso!')
        return redirect('dashboard:index')
    
    return render(request, 'jobs/job_confirm_delete.html', {'job': job})


@login_required
def job_apply(request, pk):
    if not request.user.is_candidate():
        messages.error(request, 'Apenas candidatos podem se candidatar a vagas.')
        return redirect('jobs:detail', pk=pk)
    
    job = get_object_or_404(Job, pk=pk, is_active=True)
    
    if Application.objects.filter(job=job, candidate=request.user).exists():
        messages.warning(request, 'Você já se candidatou a esta vaga.')
        return redirect('jobs:detail', pk=pk)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.candidate = request.user
            application.match_score = calculate_match_score(request.user, job)
            application.save()
            messages.success(request, 'Candidatura enviada com sucesso!')
            return redirect('dashboard:index')
    else:
        form = ApplicationForm()
    
    return render(request, 'jobs/job_apply.html', {'form': form, 'job': job})


@login_required
def my_applications(request):
    if not request.user.is_candidate():
        return redirect('dashboard:index')
    
    applications = Application.objects.filter(candidate=request.user).select_related('job__company__company_profile')
    return render(request, 'jobs/my_applications.html', {'applications': applications})


@login_required
def job_applications(request, pk):
    job = get_object_or_404(Job, pk=pk, company=request.user)
    
    if hasattr(request.user, 'company_profile') and not request.user.company_profile.is_verified():
        messages.error(request, 'Sua empresa precisa ser aprovada para visualizar candidaturas.')
        return redirect('dashboard:index')
    
    applications = job.applications.select_related('candidate__candidate_profile').order_by('-match_score')
    
    return render(request, 'jobs/job_applications.html', {'job': job, 'applications': applications})


@login_required
def application_detail(request, pk):
    from jobs.models import ApplicationStatusHistory
    from accounts.models import Notification
    
    application = get_object_or_404(Application.objects.select_related('job', 'candidate__candidate_profile'), pk=pk)
    
    if application.job.company != request.user and application.candidate != request.user:
        messages.error(request, 'Você não tem permissão para ver esta candidatura.')
        return redirect('dashboard:index')
    
    if request.method == 'POST' and request.user.is_company():
        if hasattr(request.user, 'company_profile') and not request.user.company_profile.is_verified():
            messages.error(request, 'Sua empresa precisa ser aprovada para gerenciar candidaturas.')
            return redirect('dashboard:index')
        
        old_status = application.status
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save()
            
            if old_status != application.status:
                ApplicationStatusHistory.objects.create(
                    application=application,
                    old_status=old_status,
                    new_status=application.status,
                    changed_by=request.user,
                    notes=application.notes
                )
                
                Notification.notify_user(
                    user=application.candidate,
                    notification_type='application_status',
                    title='Status da candidatura atualizado',
                    message=f'O status da sua candidatura para "{application.job.title}" foi alterado para "{application.get_status_display()}".',
                    link=f'/jobs/application/{application.pk}/'
                )
            
            messages.success(request, 'Status da candidatura atualizado!')
            return redirect('jobs:application_detail', pk=pk)
    else:
        form = ApplicationStatusForm(instance=application)
    
    status_history = application.status_history.select_related('changed_by').order_by('-created_at')
    
    return render(request, 'jobs/application_detail.html', {
        'application': application,
        'form': form,
        'is_company': request.user.is_company(),
        'status_history': status_history
    })
