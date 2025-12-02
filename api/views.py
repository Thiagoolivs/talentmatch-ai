from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import User
from jobs.models import Job, Application
from courses.models import Course, UserCourse
from match.models import MatchResult
from match.utils import calculate_match_score, get_recommended_jobs_for_candidate
from chatbot.models import ChatSession, ChatMessage
from chatbot.ai_engine import get_ai_response

from .serializers import (
    UserSerializer, JobSerializer, ApplicationSerializer,
    CourseSerializer, UserCourseSerializer, MatchResultSerializer,
    ChatSessionSerializer, ChatMessageSerializer
)
from .permissions import IsCompanyOrReadOnly, IsCandidateOrCompanyOwner


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_admin_user():
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsCompanyOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['job_type', 'work_mode', 'is_active', 'location']
    
    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True)
        if self.request.user.is_authenticated and self.request.user.is_company():
            queryset = Job.objects.filter(company=self.request.user)
        return queryset
    
    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_company():
            return Response({'error': 'Apenas empresas podem criar vagas'}, 
                          status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(company=self.request.user)
    
    @action(detail=True, methods=['get'])
    def candidates(self, request, pk=None):
        job = self.get_object()
        if job.company != request.user and not request.user.is_admin_user():
            return Response({'error': 'Acesso nao autorizado'}, 
                          status=status.HTTP_403_FORBIDDEN)
        applications = job.applications.all()
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsCandidateOrCompanyOwner]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_candidate():
            return Application.objects.filter(candidate=user)
        elif user.is_company():
            return Application.objects.filter(job__company=user)
        return Application.objects.all()
    
    def create(self, request, *args, **kwargs):
        if not request.user.is_candidate():
            return Response({'error': 'Apenas candidatos podem se candidatar'}, 
                          status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        job = serializer.validated_data['job']
        score = calculate_match_score(self.request.user, job)
        serializer.save(candidate=self.request.user, match_score=score)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_candidate():
            return Response({'error': 'Apenas empresas podem atualizar candidaturas'}, 
                          status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['level', 'area', 'is_free']


class UserCourseViewSet(viewsets.ModelViewSet):
    queryset = UserCourse.objects.all()
    serializer_class = UserCourseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserCourse.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MatchResult.objects.all()
    serializer_class = MatchResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_candidate():
            return MatchResult.objects.filter(candidate=user)
        elif user.is_company():
            return MatchResult.objects.filter(job__company=user)
        return MatchResult.objects.all()
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        if not request.user.is_candidate():
            return Response({'error': 'Only candidates can get recommendations'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        recommendations = get_recommended_jobs_for_candidate(request.user, limit=10)
        data = []
        for rec in recommendations:
            data.append({
                'job_id': rec['job'].id,
                'job_title': rec['job'].title,
                'score': rec['score'],
                'matched_skills': rec['matched_skills'],
                'missing_skills': rec['missing_skills']
            })
        return Response(data)


class ChatViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        session = self.get_object()
        message = request.data.get('message', '')
        
        if not message:
            return Response({'error': 'Message is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        ChatMessage.objects.create(session=session, role='user', content=message)
        
        ai_response = get_ai_response(request.user, message, session)
        
        ChatMessage.objects.create(session=session, role='assistant', content=ai_response)
        
        return Response({
            'response': ai_response,
            'success': True
        })
