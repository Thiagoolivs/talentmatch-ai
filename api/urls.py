from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'vagas', views.JobViewSet)
router.register(r'candidaturas', views.ApplicationViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'user-courses', views.UserCourseViewSet)
router.register(r'match', views.MatchViewSet)
router.register(r'chat', views.ChatViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
]
