from django.shortcuts import redirect
from django.urls import reverse


class ProfileRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        if (request.user.is_authenticated and 
            request.path == reverse('accounts:login') and 
            response.status_code == 302):
            return redirect('dashboard:index')
        
        return response
