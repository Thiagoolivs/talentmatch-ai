from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction
import logging

from .forms import (CandidateRegistrationForm, CompanyRegistrationForm, 
                    CustomLoginForm, CandidateProfileForm, CompanyProfileForm, UserUpdateForm)
from .models import CandidateProfile, CompanyProfile

logger = logging.getLogger(__name__)


def register_choice(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    return render(request, 'accounts/register_choice.html')


def register_candidate(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = CandidateRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    login(request, user)
                    messages.success(request, 'Conta criada com sucesso! Complete seu perfil.')
                    return redirect('accounts:profile')
            except Exception as e:
                logger.error(f"Erro ao registrar candidato: {e}")
                messages.error(request, 'Ocorreu um erro ao criar sua conta. Tente novamente.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{form.fields.get(field, field).label if hasattr(form.fields.get(field), 'label') else field}: {error}")
    else:
        form = CandidateRegistrationForm()
    return render(request, 'accounts/register_candidate.html', {'form': form})


def register_company(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    login(request, user)
                    messages.success(request, 'Conta da empresa criada com sucesso! Complete seu perfil.')
                    return redirect('accounts:profile')
            except Exception as e:
                logger.error(f"Erro ao registrar empresa: {e}")
                messages.error(request, 'Ocorreu um erro ao criar sua conta. Tente novamente.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{form.fields.get(field, field).label if hasattr(form.fields.get(field), 'label') else field}: {error}")
    else:
        form = CompanyRegistrationForm()
    return render(request, 'accounts/register_company.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard:index')


def logout_view(request):
    logout(request)
    messages.success(request, 'Você saiu com sucesso.')
    return redirect('core:home')


def check_profile_completeness(profile_obj, user):
    missing_fields = []
    if hasattr(profile_obj, 'bio'):
        if not profile_obj.bio or len(profile_obj.bio) < 20:
            missing_fields.append('Resumo Profissional')
        if not profile_obj.skills:
            missing_fields.append('Habilidades')
        if not getattr(profile_obj, 'city', None):
            missing_fields.append('Cidade')
        if not getattr(profile_obj, 'state', None):
            missing_fields.append('Estado')
    elif hasattr(profile_obj, 'company_name'):
        if not profile_obj.company_name:
            missing_fields.append('Nome da Empresa')
        if not profile_obj.description:
            missing_fields.append('Descricao da Empresa')
    return missing_fields


@login_required
def profile(request):
    user = request.user
    
    if user.is_candidate():
        profile_obj, created = CandidateProfile.objects.get_or_create(user=user)
        
        missing_fields = check_profile_completeness(profile_obj, user)
        profile_incomplete = len(missing_fields) > 0
        
        if request.method == 'POST':
            user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
            profile_form = CandidateProfileForm(request.POST, request.FILES, instance=profile_obj)
            if user_form.is_valid() and profile_form.is_valid():
                try:
                    with transaction.atomic():
                        user_form.save()
                        saved_profile = profile_form.save()
                        logger.info(f"Perfil salvo - User: {user.username}, City: {saved_profile.city}, State: {saved_profile.state}, Bio: {len(saved_profile.bio or '')} chars")
                    messages.success(request, 'Perfil atualizado com sucesso!')
                    return redirect('accounts:profile')
                except Exception as e:
                    logger.error(f"Erro ao salvar perfil do candidato {user.username}: {e}", exc_info=True)
                    messages.error(request, 'Ocorreu um erro ao salvar as alterações. Tente novamente.')
            else:
                for form in [user_form, profile_form]:
                    for field, errors in form.errors.items():
                        for error in errors:
                            if field == '__all__':
                                messages.error(request, error)
                            else:
                                field_label = form.fields.get(field).label if field in form.fields and form.fields.get(field).label else field
                                messages.error(request, f"{field_label}: {error}")
                logger.warning(f"Erros de validacao no perfil de {user.username}: {user_form.errors}, {profile_form.errors}")
        else:
            user_form = UserUpdateForm(instance=user)
            profile_form = CandidateProfileForm(instance=profile_obj)
            
            if profile_incomplete and not request.GET.get('saved'):
                messages.warning(request, f'Complete seu perfil para melhorar suas chances. Campos faltando: {", ".join(missing_fields)}')
        
        return render(request, 'accounts/profile_candidate.html', {
            'user_form': user_form,
            'profile_form': profile_form,
            'profile_incomplete': profile_incomplete,
            'missing_fields': missing_fields
        })
    
    elif user.is_company():
        profile_obj, created = CompanyProfile.objects.get_or_create(
            user=user,
            defaults={'company_name': user.username}
        )
        
        missing_fields = check_profile_completeness(profile_obj, user)
        profile_incomplete = len(missing_fields) > 0
        
        if request.method == 'POST':
            user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
            profile_form = CompanyProfileForm(request.POST, request.FILES, instance=profile_obj)
            if user_form.is_valid() and profile_form.is_valid():
                try:
                    with transaction.atomic():
                        user_form.save()
                        profile_form.save()
                        logger.info(f"Perfil da empresa {profile_obj.company_name} salvo com sucesso")
                    messages.success(request, 'Perfil da empresa atualizado com sucesso!')
                    return redirect('accounts:profile')
                except Exception as e:
                    logger.error(f"Erro ao salvar perfil da empresa {user.username}: {e}", exc_info=True)
                    messages.error(request, 'Ocorreu um erro ao salvar as alterações. Tente novamente.')
            else:
                for form in [user_form, profile_form]:
                    for field, errors in form.errors.items():
                        for error in errors:
                            if field == '__all__':
                                messages.error(request, error)
                            else:
                                field_label = form.fields.get(field).label if field in form.fields and form.fields.get(field).label else field
                                messages.error(request, f"{field_label}: {error}")
                logger.warning(f"Erros de validacao no perfil de {user.username}: {user_form.errors}, {profile_form.errors}")
        else:
            user_form = UserUpdateForm(instance=user)
            profile_form = CompanyProfileForm(instance=profile_obj)
            
            if profile_incomplete and not request.GET.get('saved'):
                messages.warning(request, f'Complete o perfil da empresa. Campos faltando: {", ".join(missing_fields)}')
        
        return render(request, 'accounts/profile_company.html', {
            'user_form': user_form,
            'profile_form': profile_form,
            'profile_incomplete': profile_incomplete,
            'missing_fields': missing_fields
        })
    
    return redirect('dashboard:index')


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/forgot_password.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    
    def form_valid(self, form):
        messages.info(self.request, 'Se o email estiver cadastrado, voce recebera instrucoes para redefinir sua senha.')
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/forgot_password_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/reset_password.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
    
    def form_valid(self, form):
        messages.success(self.request, 'Senha redefinida com sucesso!')
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/reset_done.html'
