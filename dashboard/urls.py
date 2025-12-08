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
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('admin/users/<int:user_id>/toggle-active/', views.toggle_user_active, name='toggle_user_active'),
]
