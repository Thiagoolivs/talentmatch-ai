from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
import re
import logging
from .models import User, CandidateProfile, CompanyProfile

logger = logging.getLogger(__name__)


class CandidateRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': 'O email e obrigatorio.',
            'invalid': 'Digite um email valido.'
        }
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        label='Nome',
        error_messages={'required': 'O nome e obrigatorio.'}
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        label='Sobrenome',
        error_messages={'required': 'O sobrenome e obrigatorio.'}
    )
    experience_years = forms.IntegerField(
        min_value=0,
        max_value=50,
        required=False,
        label='Anos de Experiência',
        initial=0,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        error_messages = {
            'username': {
                'unique': 'Este nome de usuario ja esta em uso.',
                'required': 'O nome de usuario e obrigatorio.',
            }
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        
        self.fields['password1'].help_text = 'Minimo 8 caracteres, com letras e numeros.'
        self.fields['password2'].help_text = 'Digite a mesma senha novamente.'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ja esta cadastrado.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'candidate'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            experience_years = self.cleaned_data.get('experience_years') or 0
            CandidateProfile.objects.create(user=user, experience_years=experience_years)
        return user


class CompanyRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': 'O email e obrigatorio.',
            'invalid': 'Digite um email valido.'
        }
    )
    company_name = forms.CharField(
        max_length=200, 
        required=True, 
        label='Nome da Empresa',
        error_messages={'required': 'O nome da empresa e obrigatorio.'}
    )
    cnpj = forms.CharField(
        max_length=18,
        required=False,
        label='CNPJ',
        validators=[
            RegexValidator(
                regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$|^\d{14}$',
                message='Digite um CNPJ valido (XX.XXX.XXX/XXXX-XX ou apenas numeros).'
            )
        ]
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'company_name', 'cnpj', 'password1', 'password2']
        error_messages = {
            'username': {
                'unique': 'Este nome de usuario ja esta em uso.',
                'required': 'O nome de usuario e obrigatorio.',
            }
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        
        self.fields['cnpj'].widget.attrs['placeholder'] = 'XX.XXX.XXX/XXXX-XX'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ja esta cadastrado.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'company'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            CompanyProfile.objects.create(
                user=user, 
                company_name=self.cleaned_data['company_name'],
                cnpj=self.cleaned_data.get('cnpj', '')
            )
        return user


class CustomLoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'Usuario ou senha incorretos.',
        'inactive': 'Esta conta esta inativa.',
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        
        self.fields['username'].label = 'Usuario ou Email'
        self.fields['password'].label = 'Senha'


def validate_brazilian_phone(value):
    if not value:
        return value
    cleaned = re.sub(r'[^\d]', '', value)
    if len(cleaned) < 10 or len(cleaned) > 11:
        raise ValidationError('Telefone invalido. Use o formato (XX) XXXXX-XXXX ou (XX) XXXX-XXXX.')
    return value


class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = ['bio', 'skills', 'experience', 'experience_years', 'education', 'resume', 
                  'linkedin_url', 'github_url', 'portfolio_url', 'desired_salary', 
                  'city', 'state', 'age', 'interest_area', 'available']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Conte um pouco sobre voce (minimo 20 caracteres)...'}),
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Python, JavaScript, React, Django...'}),
            'experience': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Descreva sua experiencia profissional...'}),
            'education': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Sua formacao academica...'}),
            'state': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'interest_area': forms.TextInput(attrs={'placeholder': 'Ex: Desenvolvimento Web, Data Science...'}),
        }
        labels = {
            'bio': 'Resumo Profissional',
            'skills': 'Habilidades (separe por virgula)',
            'experience': 'Experiencia Profissional',
            'experience_years': 'Anos de Experiencia',
            'education': 'Formacao Academica',
            'resume': 'Curriculo (PDF)',
            'linkedin_url': 'LinkedIn',
            'github_url': 'GitHub',
            'portfolio_url': 'Portfolio',
            'desired_salary': 'Pretensao Salarial',
            'city': 'Cidade',
            'state': 'Estado',
            'age': 'Idade',
            'interest_area': 'Area de Interesse',
            'available': 'Disponivel para novas oportunidades',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        self.fields['city'].required = True
        self.fields['state'].required = True
        self.fields['bio'].help_text = 'Minimo 20 caracteres, maximo 1000 caracteres.'
    
    def clean_bio(self):
        bio = self.cleaned_data.get('bio', '')
        if bio:
            if len(bio) < 20:
                raise forms.ValidationError('O resumo deve ter no minimo 20 caracteres.')
            if len(bio) > 1000:
                raise forms.ValidationError('O resumo deve ter no maximo 1000 caracteres.')
        return bio
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None:
            if age < 16:
                raise forms.ValidationError('A idade minima e 16 anos.')
            if age > 120:
                raise forms.ValidationError('Idade invalida.')
        return age
    
    def clean_city(self):
        city = self.cleaned_data.get('city', '').strip()
        if not city:
            raise forms.ValidationError('A cidade e obrigatoria.')
        return city
    
    def clean_state(self):
        state = self.cleaned_data.get('state', '').strip()
        if not state:
            raise forms.ValidationError('O estado e obrigatorio.')
        return state
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if hasattr(resume, 'content_type'):
                if resume.content_type != 'application/pdf':
                    raise forms.ValidationError('Apenas arquivos PDF sao aceitos.')
            if hasattr(resume, 'size'):
                if resume.size > 5 * 1024 * 1024:
                    raise forms.ValidationError('O arquivo deve ter no maximo 5MB.')
        return resume
    
    def clean_skills(self):
        skills = self.cleaned_data.get('skills', '')
        if skills:
            try:
                from accounts.skill_normalizer import normalize_skills_string
                user = getattr(self.instance, 'user', None)
                normalized = normalize_skills_string(skills, user)
                return normalized
            except Exception as e:
                logger.warning(f"Error normalizing skills: {e}")
                return skills
        return skills
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.city and instance.state:
            instance.location = f"{instance.city}, {instance.state}"
        if commit:
            instance.save()
            logger.info(f"Perfil do candidato {instance.user.username} salvo com sucesso")
        return instance


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'description', 'industry', 'website', 'location', 
                  'size', 'founded_year', 'logo', 'cnpj']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Descreva sua empresa...'}),
        }
        labels = {
            'company_name': 'Nome da Empresa',
            'description': 'Descricao',
            'industry': 'Setor/Industria',
            'website': 'Site',
            'location': 'Localizacao',
            'size': 'Tamanho da Empresa',
            'founded_year': 'Ano de Fundacao',
            'logo': 'Logo',
            'cnpj': 'CNPJ',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
    
    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            if hasattr(logo, 'size'):
                if logo.size > 2 * 1024 * 1024:
                    raise forms.ValidationError('A imagem deve ter no maximo 2MB.')
        return logo


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'avatar']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'Email',
            'phone': 'Telefone',
            'avatar': 'Foto de Perfil',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        self.fields['phone'].widget.attrs['placeholder'] = '(XX) XXXXX-XXXX'
        self.fields['phone'].help_text = 'Formato: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este email ja esta em uso.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone:
            cleaned = re.sub(r'[^\d]', '', phone)
            if len(cleaned) < 10 or len(cleaned) > 11:
                raise forms.ValidationError('Telefone invalido. Use o formato (XX) XXXXX-XXXX ou (XX) XXXX-XXXX.')
        return phone
