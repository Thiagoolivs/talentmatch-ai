import os
import logging

from django.core.management.base import BaseCommand
from accounts.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Creates the default admin user if it does not exist. Requires ADMIN_PASSWORD env var.'

    def handle(self, *args, **options):
        admin_username = os.environ.get('ADMIN_USERNAME', 'administrador')
        admin_password = os.environ.get('ADMIN_PASSWORD', '')
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@talentmatch.com')

        if User.objects.filter(username=admin_username).exists():
            self.stdout.write(self.style.WARNING(f'Admin user "{admin_username}" already exists.'))
            logger.info(f'Admin user "{admin_username}" already exists. Skipping creation.')
            return

        if not admin_password:
            self.stdout.write(self.style.WARNING(
                'ADMIN_PASSWORD not set; skipping admin creation. '
                'Set the ADMIN_PASSWORD environment variable to create the admin user.'
            ))
            logger.warning('ADMIN_PASSWORD not set. Admin user not created.')
            return

        User.objects.create_user(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            first_name='Administrador',
            last_name='TalentMatch',
            user_type='admin',
            is_staff=True,
            is_superuser=True,
            email_verified=True,
        )

        self.stdout.write(self.style.SUCCESS(f'Admin user "{admin_username}" created successfully.'))
        logger.info(f'Admin user "{admin_username}" created successfully.')
