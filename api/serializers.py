from rest_framework import serializers
from accounts.models import User, CandidateProfile, CompanyProfile
from jobs.models import Job, Application
from courses.models import Course, UserCourse
from match.models import MatchResult
from chatbot.models import ChatSession, ChatMessage


class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields = ['bio', 'skills', 'experience', 'education', 'location', 'available']


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'description', 'industry', 'website', 'location', 'size']


class UserSerializer(serializers.ModelSerializer):
    candidate_profile = CandidateProfileSerializer(read_only=True)
    company_profile = CompanyProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 
                  'candidate_profile', 'company_profile', 'created_at']
        read_only_fields = ['id', 'created_at']


class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    application_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'requirements', 'responsibilities',
                  'benefits', 'job_type', 'work_mode', 'location', 'salary_min',
                  'salary_max', 'experience_years', 'is_active', 'deadline',
                  'company_name', 'application_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_company_name(self, obj):
        if hasattr(obj.company, 'company_profile'):
            return obj.company.company_profile.company_name
        return obj.company.username
    
    def get_application_count(self, obj):
        return obj.applications.count()


class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    candidate_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = ['id', 'job', 'job_title', 'candidate', 'candidate_name',
                  'cover_letter', 'status', 'match_score', 'applied_at', 'updated_at']
        read_only_fields = ['id', 'applied_at', 'updated_at', 'match_score']
    
    def get_candidate_name(self, obj):
        return obj.candidate.get_full_name() or obj.candidate.username


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'level', 'area', 'duration_hours',
                  'external_url', 'skills_taught', 'instructor', 'is_free', 
                  'price', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserCourseSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = UserCourse
        fields = ['id', 'course', 'course_title', 'status', 'progress',
                  'started_at', 'completed_at', 'created_at']
        read_only_fields = ['id', 'created_at']


class MatchResultSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    candidate_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MatchResult
        fields = ['id', 'job', 'job_title', 'candidate', 'candidate_name',
                  'score', 'matched_skills', 'missing_skills', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_candidate_name(self, obj):
        return obj.candidate.get_full_name() or obj.candidate.username


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'created_at', 'updated_at', 'is_active', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']
