from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('report-problem/', views.report_problem, name='report_problem'),
    path('my-problems/', views.my_problems, name='my_problems'),
    path('admin/companies/', views.admin_companies, name='admin_companies'),
    path('admin/companies/<int:company_id>/verify/', views.verify_company, name='verify_company'),
    path('admin/problems/', views.admin_problems, name='admin_problems'),
    path('admin/problems/<int:problem_id>/update/', views.update_problem, name='update_problem'),
    path('admin/maintenance/toggle/', views.toggle_maintenance, name='toggle_maintenance'),
]
