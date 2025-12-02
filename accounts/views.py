from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import (CandidateRegistrationForm, CompanyRegistrationForm, 
                    CustomLoginForm, CandidateProfileForm, CompanyProfileForm, UserUpdateForm)
from .models import CandidateProfile, CompanyProfile


def register_choice(request):
    return render(request, 'accounts/register_choice.html')


def register_candidate(request):
    if request.method == 'POST':
        form = CandidateRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Conta criada com sucesso! Complete seu perfil.')
            return redirect('accounts:profile')
    else:
        form = CandidateRegistrationForm()
    return render(request, 'accounts/register_candidate.html', {'form': form})


def register_company(request):
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Conta da empresa criada com sucesso! Complete seu perfil.')
            return redirect('accounts:profile')
    else:
        form = CompanyRegistrationForm()
    return render(request, 'accounts/register_company.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard:index')


def logout_view(request):
    logout(request)
    messages.success(request, 'Você saiu com sucesso.')
    return redirect('core:home')


@login_required
def profile(request):
    user = request.user
    
    if user.is_candidate():
        profile_obj, created = CandidateProfile.objects.get_or_create(user=user)
        if request.method == 'POST':
            user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
            profile_form = CandidateProfileForm(request.POST, request.FILES, instance=profile_obj)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('accounts:profile')
        else:
            user_form = UserUpdateForm(instance=user)
            profile_form = CandidateProfileForm(instance=profile_obj)
        return render(request, 'accounts/profile_candidate.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })
    
    elif user.is_company():
        profile_obj, created = CompanyProfile.objects.get_or_create(user=user)
        if request.method == 'POST':
            user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
            profile_form = CompanyProfileForm(request.POST, request.FILES, instance=profile_obj)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('accounts:profile')
        else:
            user_form = UserUpdateForm(instance=user)
            profile_form = CompanyProfileForm(instance=profile_obj)
        return render(request, 'accounts/profile_company.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })
    
    return redirect('dashboard:index')
