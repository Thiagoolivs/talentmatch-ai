from django.urls import path
from . import views

app_name = 'match'

urlpatterns = [
    path('', views.match_overview, name='overview'),
    path('jobs/', views.recommended_jobs, name='recommended_jobs'),
    path('candidates/<int:job_id>/', views.recommended_candidates, name='recommended_candidates'),
]
