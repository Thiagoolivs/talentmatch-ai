from django.core.management.base import BaseCommand
from accounts.models import CanonicalSkill
import logging

logger = logging.getLogger(__name__)

CANONICAL_SKILLS = [
    {'name': 'python', 'aliases': 'py, python3', 'category': 'Linguagem de Programacao'},
    {'name': 'javascript', 'aliases': 'js, ecmascript', 'category': 'Linguagem de Programacao'},
    {'name': 'typescript', 'aliases': 'ts', 'category': 'Linguagem de Programacao'},
    {'name': 'java', 'aliases': '', 'category': 'Linguagem de Programacao'},
    {'name': 'c#', 'aliases': 'csharp, c sharp', 'category': 'Linguagem de Programacao'},
    {'name': 'c++', 'aliases': 'cpp', 'category': 'Linguagem de Programacao'},
    {'name': 'ruby', 'aliases': 'rb', 'category': 'Linguagem de Programacao'},
    {'name': 'php', 'aliases': '', 'category': 'Linguagem de Programacao'},
    {'name': 'go', 'aliases': 'golang', 'category': 'Linguagem de Programacao'},
    {'name': 'rust', 'aliases': '', 'category': 'Linguagem de Programacao'},
    {'name': 'swift', 'aliases': '', 'category': 'Linguagem de Programacao'},
    {'name': 'kotlin', 'aliases': '', 'category': 'Linguagem de Programacao'},
    {'name': 'react', 'aliases': 'reactjs, react.js', 'category': 'Framework Frontend'},
    {'name': 'angular', 'aliases': 'angularjs, angular.js', 'category': 'Framework Frontend'},
    {'name': 'vue', 'aliases': 'vuejs, vue.js', 'category': 'Framework Frontend'},
    {'name': 'django', 'aliases': '', 'category': 'Framework Backend'},
    {'name': 'flask', 'aliases': '', 'category': 'Framework Backend'},
    {'name': 'fastapi', 'aliases': 'fast-api', 'category': 'Framework Backend'},
    {'name': 'spring', 'aliases': 'spring boot, springboot', 'category': 'Framework Backend'},
    {'name': 'nodejs', 'aliases': 'node.js, node', 'category': 'Runtime'},
    {'name': 'express', 'aliases': 'expressjs, express.js', 'category': 'Framework Backend'},
    {'name': 'sql', 'aliases': '', 'category': 'Banco de Dados'},
    {'name': 'mysql', 'aliases': 'my-sql', 'category': 'Banco de Dados'},
    {'name': 'postgresql', 'aliases': 'postgres, pgsql', 'category': 'Banco de Dados'},
    {'name': 'mongodb', 'aliases': 'mongo', 'category': 'Banco de Dados'},
    {'name': 'redis', 'aliases': '', 'category': 'Banco de Dados'},
    {'name': 'docker', 'aliases': '', 'category': 'DevOps'},
    {'name': 'kubernetes', 'aliases': 'k8s', 'category': 'DevOps'},
    {'name': 'aws', 'aliases': 'amazon web services', 'category': 'Cloud'},
    {'name': 'azure', 'aliases': 'microsoft azure', 'category': 'Cloud'},
    {'name': 'gcp', 'aliases': 'google cloud, google cloud platform', 'category': 'Cloud'},
    {'name': 'git', 'aliases': '', 'category': 'Controle de Versao'},
    {'name': 'github', 'aliases': '', 'category': 'Controle de Versao'},
    {'name': 'gitlab', 'aliases': '', 'category': 'Controle de Versao'},
    {'name': 'html', 'aliases': 'html5', 'category': 'Frontend'},
    {'name': 'css', 'aliases': 'css3', 'category': 'Frontend'},
    {'name': 'sass', 'aliases': 'scss', 'category': 'Frontend'},
    {'name': 'tailwind', 'aliases': 'tailwindcss, tailwind css', 'category': 'Frontend'},
    {'name': 'bootstrap', 'aliases': '', 'category': 'Frontend'},
    {'name': 'linux', 'aliases': '', 'category': 'Sistema Operacional'},
    {'name': 'excel', 'aliases': 'microsoft excel, ms excel', 'category': 'Ferramentas'},
    {'name': 'power bi', 'aliases': 'powerbi', 'category': 'BI'},
    {'name': 'tableau', 'aliases': '', 'category': 'BI'},
    {'name': 'machine learning', 'aliases': 'ml, aprendizado de maquina', 'category': 'IA'},
    {'name': 'deep learning', 'aliases': 'dl, aprendizado profundo', 'category': 'IA'},
    {'name': 'tensorflow', 'aliases': 'tf', 'category': 'IA'},
    {'name': 'pytorch', 'aliases': '', 'category': 'IA'},
    {'name': 'scikit-learn', 'aliases': 'sklearn', 'category': 'IA'},
    {'name': 'pandas', 'aliases': '', 'category': 'Ciencia de Dados'},
    {'name': 'numpy', 'aliases': '', 'category': 'Ciencia de Dados'},
    {'name': 'agile', 'aliases': 'metodologia agil', 'category': 'Metodologia'},
    {'name': 'scrum', 'aliases': '', 'category': 'Metodologia'},
    {'name': 'kanban', 'aliases': '', 'category': 'Metodologia'},
    {'name': 'jira', 'aliases': '', 'category': 'Ferramentas'},
    {'name': 'rest api', 'aliases': 'restful, rest', 'category': 'API'},
    {'name': 'graphql', 'aliases': '', 'category': 'API'},
    {'name': 'api', 'aliases': '', 'category': 'API'},
    {'name': 'vba', 'aliases': 'visual basic for applications', 'category': 'Automacao'},
    {'name': 'power automate', 'aliases': 'microsoft power automate', 'category': 'Automacao'},
    {'name': 'selenium', 'aliases': '', 'category': 'Testes'},
    {'name': 'jest', 'aliases': '', 'category': 'Testes'},
    {'name': 'pytest', 'aliases': '', 'category': 'Testes'},
    {'name': 'ci/cd', 'aliases': 'cicd, ci cd', 'category': 'DevOps'},
    {'name': 'jenkins', 'aliases': '', 'category': 'DevOps'},
    {'name': 'terraform', 'aliases': '', 'category': 'DevOps'},
    {'name': 'ansible', 'aliases': '', 'category': 'DevOps'},
]


class Command(BaseCommand):
    help = 'Seeds the canonical skills database'

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for skill_data in CANONICAL_SKILLS:
            skill, created = CanonicalSkill.objects.update_or_create(
                name=skill_data['name'],
                defaults={
                    'aliases': skill_data['aliases'],
                    'category': skill_data['category'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Skills seeded: {created_count} created, {updated_count} updated'
            )
        )
        logger.info(f'Canonical skills seeded: {created_count} created, {updated_count} updated')
