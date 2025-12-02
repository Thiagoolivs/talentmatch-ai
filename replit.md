# TalentMatch - Django Talent Matching Platform

## Overview
TalentMatch is a comprehensive talent matching platform built with Django. It connects candidates with job opportunities using AI-powered skill matching algorithms. The platform includes job postings, candidate and company profiles, course recommendations for skill gaps, an AI chatbot for resume analysis, and interactive dashboards.

## Project Structure
```
talentmatch/
├── accounts/          # User authentication, profiles (candidate, company, admin)
├── jobs/             # Job postings, applications, filtering
├── match/            # TF-IDF skill matching algorithm
├── courses/          # Course catalog and progress tracking
├── chatbot/          # AI chatbot for resume analysis
├── dashboard/        # Interactive dashboards with Chart.js
├── api/              # REST API with Django REST Framework
├── core/             # Home page, about, contact
├── templates/        # HTML templates with Tailwind CSS
├── static/           # Static files
├── media/            # Uploaded files (resumes, logos)
└── talentmatch/      # Django project settings
```

## Technology Stack
- **Backend**: Django 5.2, Django REST Framework
- **Database**: SQLite (development), ready for PostgreSQL (production)
- **AI/ML**: scikit-learn (TF-IDF vectorization for skill matching)
- **Frontend**: Tailwind CSS (CDN), Chart.js for dashboards
- **Static Files**: WhiteNoise for serving

## Key Features
1. **Three User Types**: Candidate, Company, Admin with different permissions
2. **Job System**: Create, edit, filter jobs; track applications with status (submitted, analyzing, pre-selected, rejected)
3. **AI Matching**: TF-IDF algorithm compares candidate skills with job requirements
4. **Course Recommendations**: Identifies skill gaps and recommends courses
5. **AI Chatbot**: Analyzes resumes, recommends jobs/courses (prepared for OpenAI integration)
6. **REST API**: Complete CRUD for all resources

## User Preferences
- Interface language: Portuguese (pt-BR)
- Code language: English
- Color scheme: Blue (#005BBB) and white
- Design: Responsive with Tailwind CSS

## Running the Application
- Development: `python manage.py runserver 0.0.0.0:5000`
- Production: `gunicorn --bind=0.0.0.0:5000 --reuse-port talentmatch.wsgi:application`

## API Endpoints
- `/api/users/` - User management
- `/api/vagas/` - Job listings
- `/api/candidaturas/` - Applications
- `/api/courses/` - Course catalog
- `/api/match/` - Match results
- `/api/chat/` - Chat sessions

## Recent Changes
- Initial project setup with all 8 Django apps
- Database models for users, jobs, applications, courses, matches, chat
- TF-IDF matching algorithm implemented
- AI chatbot with rule-based responses (ready for OpenAI)
- Complete responsive templates with Tailwind CSS
- REST API with Django REST Framework

## Configuration Notes
- ALLOWED_HOSTS set to ['*'] for development
- SESSION_SECRET required for production
- Media files stored in /media/
- Static files collected to /staticfiles/
