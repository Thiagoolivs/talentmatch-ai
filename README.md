# TalentMatch AI

Sistema Inteligente de Matching de Talentos com Vagas

## Sobre

Plataforma de recrutamento que usa IA para conectar candidatos às melhores vagas.
Analisa habilidades, experiência, localização e salário para encontrar matches perfeitos

## Funcionalidades

- Matching Inteligente: 50% habilidades, 25% experiência, 15% localização, 10% salário
- Chatbot com IA: Análise de currículos e orientação de carreira (Groq API)
- Três tipos de usuário: Candidatos, Empresas, Administradores
- Recomendação de cursos para gaps de habilidades
- Dashboard administrativo com métricas
- Sistema de verificação de empresas

## Tecnologias

- Backend: Django 5.2, Django REST Framework
- Database: SQLite (dev) / PostgreSQL (prod)
- IA/ML: Scikit-learn, Groq API
- Frontend: Tailwind CSS, Chart.js

## Instalação

1. Clone: git clone https://github.com/Thiagoolivs/talentmatch-ai.git
2. Entre na pasta: cd talentmatch-ai
3. Crie ambiente virtual: python -m venv venv
4. Ative: source venv/bin/activate (Linux/Mac) ou venv\Scripts\activate (Windows)
5. Instale: pip install -r requirements.txt
6. Migrações: python manage.py migrate
7. Execute: python manage.py runserver 0.0.0.0:5000

## API Endpoints

- /api/users/ - Usuários
- /api/vagas/ - Vagas
- /api/candidaturas/ - Candidaturas
- /api/courses/ - Cursos
- /api/match/ - Matching
- /api/chat/ - Chat IA

## Estrutura do Projeto

- accounts/ - Autenticação e perfis
- jobs/ - Sistema de vagas
- match/ - Algoritmo de matching
- courses/ - Catálogo de cursos
- chatbot/ - Chatbot com Groq
- dashboard/ - Dashboards
- api/ - REST API
- templates/ - Templates HTML

## Variáveis de Ambiente

- SESSION_SECRET - Chave secreta Django (obrigatório em produção)
- GROQ_API_KEY - Chave da API Groq (opcional, para chatbot IA)


