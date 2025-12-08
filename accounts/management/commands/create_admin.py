from django.core.management.base import BaseCommand
from accounts.models import User
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Creates the default admin user (administrador) if it does not exist'

    def handle(self, *args, **options):
        admin_username = 'administrador'
        admin_password = 'TalentMatch2025'
        admin_email = 'admin@talentmatch.com'

        if User.objects.filter(username=admin_username).exists():
            self.stdout.write(self.style.WARNING(f'Admin user "{admin_username}" already exists.'))
            logger.info(f'Admin user "{admin_username}" already exists. Skipping creation.')
            return

        user = User.objects.create_user(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            first_name='Administrador',
            last_name='TalentMatch',
            user_type='admin',
            is_staff=True,
            is_superuser=True
        )
        
        self.stdout.write(self.style.SUCCESS(f'Admin user "{admin_username}" created successfully.'))
        logger.info(f'Admin user "{admin_username}" created successfully.')
