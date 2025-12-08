from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='list'),
    path('<int:pk>/', views.job_detail, name='detail'),
    path('create/', views.job_create, name='create'),
    path('<int:pk>/edit/', views.job_edit, name='edit'),
    path('<int:pk>/delete/', views.job_delete, name='delete'),
    path('<int:pk>/apply/', views.job_apply, name='apply'),
    path('<int:pk>/applications/', views.job_applications, name='applications'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<int:pk>/', views.application_detail, name='application_detail'),
]
