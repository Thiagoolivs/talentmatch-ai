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
├── courses/          # Course catalog, lessons, and progress tracking
│   ├── models.py      # Course, Lesson, UserCourse models
│   └── management/    # seed_courses command for initial data
├── messaging/        # Candidate-Company messaging system
│   ├── models.py      # Conversation, Message models
│   └── views.py       # AJAX chat interface, conversation list
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
- **Database**: PostgreSQL (Neon-backed via Replit)
- **AI/ML**: scikit-learn (TF-IDF vectorization), Groq API (LLM chatbot)
- **Frontend**: Tailwind CSS (CDN), Chart.js for dashboards
- **Static Files**: WhiteNoise for serving
- **Database Connector**: dj-database-url, psycopg2-binary

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
11. **Messaging System**: Chat-style messaging between candidates and companies with shared applications
12. **Structured Lessons**: Courses with ordered lessons, progress tracking, and video support

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
   - Added city, state, age, interest_area fields to CandidateProfile (migration 0003)
   - Location now split into separate city/state with get_full_location() method

2. **Groq AI Integration**
   - Integrated Groq API (llama-3.3-70b-versatile) for intelligent chat responses
   - Maintains conversation history for context
   - Falls back to local rule-based system when API unavailable
   - Enhanced error handling with specific responses for API key, rate limit, and connection issues
   - Comprehensive logging for debugging and monitoring

3. **Improved Match Algorithm**
   - Weighted scoring: Skills (50%), Experience (25%), Location (15%), Salary (10%)
   - Exact skill matching combined with TF-IDF similarity
   - Location scoring uses get_full_location() for city/state combinations
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
   - Age validation (must be >= 16 years)
   - Brazilian phone format validation: (XX) XXXXX-XXXX
   - Bio validation: 20-500 characters
   - Required city and state fields for candidates
   - CNPJ validation for companies
   - File size and type validation for uploads
   - Incomplete profile detection with user guidance

7. **Password Reset Flow**
   - Complete password reset with email (console backend for dev)
   - Custom styled templates matching platform design
   - Link on login page: "Esqueceu sua senha?"

8. **CSRF Improvements**
   - Proper CSRF token handling in AJAX requests
   - Cookie-based CSRF token retrieval in JavaScript

9. **Messaging System**
   - Conversation model with ManyToMany participants
   - Message model with sender, content, timestamps
   - AJAX-based chat interface for real-time messaging
   - Access control: only users with shared job applications can message
   - Chat-style bubble UI with automatic message polling
   - Unread message indicators
   - "Enviar Mensagem" button on application detail page

10. **Courses with Lessons**
    - Lesson model with order, content, video_url, duration
    - Ordered lesson navigation with previous/next buttons
    - Automatic progress advancement when lessons are opened
    - Seed command with 5 production-ready courses:
      - Logica de Programacao (6 lessons)
      - Banco de Dados e SQL (6 lessons)
      - Desenvolvimento Web com Django (6 lessons)
      - Excel e VBA para Negocios (5 lessons)
      - Python para Ciencia de Dados (5 lessons)

11. **Navigation Updates**
    - "Mensagens" link for authenticated users
    - "Admin" link for staff users
    - Enhanced mobile menu support

12. **Canonical Skills & Normalization System**
    - CanonicalSkill model with 66 pre-defined skills (accounts/models.py)
    - SkillCorrectionLog model for tracking skill corrections
    - Similarity matching using difflib for auto-correction
    - Integrated in CandidateProfileForm.clean_skills()
    - Seed command: `python manage.py seed_skills`

13. **Application Status History**
    - New statuses: 'viewed' and 'interview_scheduled'
    - ApplicationStatusHistory model tracks who/when/old->new changes
    - Status history display on application detail page
    - Notification sent on status changes

14. **Admin Account Management**
    - Idempotent admin creation: `python manage.py create_admin`
    - Default admin: administrador / TalentMatch2025

15. **Unapproved Company Restrictions**
    - Block job creation for unapproved companies
    - Block viewing applications for unapproved companies
    - Block managing application status for unapproved companies

16. **Audit Log System**
    - AuditLog model tracks admin actions (accounts/models.py)
    - Logs: company approvals/rejections, maintenance mode changes, user deletions
    - Includes IP address tracking

17. **Notification System**
    - Notification model (accounts/models.py)
    - In-app notifications for:
      - Application status changes
      - Company approval/rejection
    - notify_user() class method for easy notification creation

18. **Admin User Management**
    - Full user management interface at /dashboard/admin/users/
    - Search by username, email, name, or ID
    - Filter by user type (candidate/company/admin) and status (active/inactive)
    - Soft delete (deactivate) or hard delete users
    - Toggle user active status
    - Pagination support
    - Audit logging for all user management actions

## Configuration Notes
- ALLOWED_HOSTS set to ['*'] for development
- CSRF_TRUSTED_ORIGINS includes Replit domains and localhost
- Media files stored in /media/
- Static files collected to /staticfiles/

## Admin Access
- Primary login: /accounts/login/ with username `administrador` and password `admin123`
- Alternative access: /accounts/support/ with code `tm2025admin` (configurable via ADMIN_ACCESS_CODE env var)
- The alternative access link is available as "Suporte Tecnico" at the bottom of the login page
