from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_choice, name='register'),
    path('register/candidate/', views.register_candidate, name='register_candidate'),
    path('register/company/', views.register_company, name='register_company'),
    path('profile/', views.profile, name='profile'),
    
    path('forgot-password/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('forgot-password/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
