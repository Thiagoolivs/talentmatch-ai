from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from django.template import loader


class ProfileRedirectMiddleware:
    """Redireciona usuarios sem perfil completo."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.is_candidate() and not hasattr(request.user, 'candidate_profile'):
                from accounts.models import CandidateProfile
                CandidateProfile.objects.get_or_create(user=request.user)
            elif request.user.is_company() and not hasattr(request.user, 'company_profile'):
                from accounts.models import CompanyProfile
                CompanyProfile.objects.get_or_create(user=request.user, defaults={'company_name': 'Minha Empresa'})
        
        response = self.get_response(request)
        return response


class MaintenanceModeMiddleware:
    """Ativa modo de manutencao para usuarios nao-admin."""
    EXEMPT_URLS = [
        '/admin/',
        '/accounts/login/',
        '/accounts/logout/',
        '/accounts/forgot-password/',
        '/accounts/reset/',
        '/static/',
        '/media/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        from accounts.models import SiteSettings
        
        is_exempt = any(request.path.startswith(url) for url in self.EXEMPT_URLS)
        
        if not is_exempt:
            try:
                settings = SiteSettings.get_settings()
                
                if settings.maintenance_mode:
                    is_admin = request.user.is_authenticated and request.user.is_admin_user()
                    
                    if not is_admin:
                        template = loader.get_template('maintenance.html')
                        context = {
                            'message': settings.maintenance_message,
                            'end_time': settings.maintenance_end_time,
                        }
                        return HttpResponse(template.render(context, request), status=503)
            except Exception:
                pass
        
        response = self.get_response(request)
        return response


class MetricsMiddleware:
    """Coleta metricas de uso do site."""
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        if response.status_code == 200 and not request.path.startswith('/static/'):
            try:
                from accounts.models import SiteMetrics
                SiteMetrics.increment('page_views')
            except Exception:
                pass
        
        return response
