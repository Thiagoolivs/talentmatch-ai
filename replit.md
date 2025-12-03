# TalentMatch - Django Talent Matching Platform

## Overview
TalentMatch is a comprehensive talent matching platform built with Django. It connects candidates with job opportunities using AI-powered skill matching algorithms. The platform includes job postings, candidate and company profiles, course recommendations for skill gaps, an AI chatbot for resume analysis, and interactive dashboards.

## Project Structure
```
talentmatch/
├── accounts/          # User authentication, profiles (candidate, company, admin)
│   ├── models.py      # User, CandidateProfile, CompanyProfile, ProblemReport, SiteSettings, SiteMetrics
│   ├── middleware.py  # ProfileRedirect, MaintenanceMode, Metrics
│   └── admin.py       # Django admin configuration
├── jobs/             # Job postings, applications, filtering
├── match/            # Advanced weighted skill matching algorithm
│   └── utils.py      # 50% skills, 25% experience, 15% location, 10% salary matching
├── courses/          # Course catalog and progress tracking
├── chatbot/          # AI chatbot with Groq integration
│   └── ai_engine.py  # Groq API integration with local fallback
├── dashboard/        # Interactive dashboards with Chart.js
│   └── views.py      # Admin dashboard, company verification, problem management
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
- **AI/ML**: scikit-learn (TF-IDF vectorization), Groq API (LLM chatbot)
- **Frontend**: Tailwind CSS (CDN), Chart.js for dashboards
- **Static Files**: WhiteNoise for serving

## Key Features
1. **Three User Types**: Candidate, Company, Admin with different permissions
2. **Job System**: Create, edit, filter jobs; track applications with status
3. **AI Matching**: Advanced weighted algorithm (skills 50%, experience 25%, location 15%, salary 10%)
4. **Course Recommendations**: Identifies skill gaps and recommends courses
5. **AI Chatbot**: Groq-powered assistant for resume analysis and career guidance
6. **Company Verification**: Admin approval system for registered companies
7. **Problem Reporting**: Users can report issues; admins can manage and resolve
8. **Maintenance Mode**: Admin-toggleable maintenance mode for the site
9. **Site Metrics**: Automatic tracking of page views, users, applications, etc.
10. **REST API**: Complete CRUD for all resources

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

## Environment Variables
- `SESSION_SECRET` - Django secret key (required for production)
- `GROQ_API_KEY` - Groq API key for AI chatbot (optional, falls back to local rules)

## Recent Changes (December 2025)
1. **Database Schema Enhancements**
   - Added CompanyProfile verification system (pending/approved/rejected)
   - Created ProblemReport model for user-submitted issues
   - Created SiteSettings model for maintenance mode
   - Created SiteMetrics model for usage tracking
   - Added experience_years to CandidateProfile

2. **Groq AI Integration**
   - Integrated Groq API (llama-3.3-70b-versatile) for intelligent chat responses
   - Maintains conversation history for context
   - Falls back to local rule-based system when API unavailable

3. **Improved Match Algorithm**
   - Weighted scoring: Skills (50%), Experience (25%), Location (15%), Salary (10%)
   - Exact skill matching combined with TF-IDF similarity
   - Location scoring considers remote work and city matching
   - Salary compatibility scoring

4. **Admin Dashboard**
   - Complete metrics dashboard with weekly statistics
   - Company verification management
   - Problem/issue management system
   - Maintenance mode toggle
   - Quick access to pending items

5. **Maintenance Mode**
   - Admin-toggleable maintenance page
   - Exempt URLs for admin access
   - Customizable maintenance message

6. **Form Improvements**
   - Enhanced validation with clear error messages
   - CNPJ validation for companies
   - File size and type validation for uploads

7. **CSRF Improvements**
   - Proper CSRF token handling in AJAX requests
   - Cookie-based CSRF token retrieval in JavaScript

## Configuration Notes
- ALLOWED_HOSTS set to ['*'] for development
- CSRF_TRUSTED_ORIGINS includes Replit domains
- Media files stored in /media/
- Static files collected to /staticfiles/
