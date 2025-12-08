from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='list'),
    path('<int:pk>/', views.course_detail, name='detail'),
    path('<int:pk>/start/', views.start_course, name='start'),
    path('<int:pk>/progress/', views.update_progress, name='update_progress'),
    path('<int:pk>/complete/', views.complete_course, name='complete'),
    path('<int:course_pk>/lesson/<int:lesson_pk>/', views.lesson_detail, name='lesson_detail'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('recommended/', views.recommended_courses, name='recommended'),
]
