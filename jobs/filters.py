import django_filters
from .models import Job


class JobFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Título')
    location = django_filters.CharFilter(lookup_expr='icontains', label='Localização')
    requirements = django_filters.CharFilter(lookup_expr='icontains', label='Habilidades')
    salary_min = django_filters.NumberFilter(field_name='salary_min', lookup_expr='gte', label='Salário mínimo')
    
    class Meta:
        model = Job
        fields = ['job_type', 'work_mode', 'title', 'location', 'requirements']
