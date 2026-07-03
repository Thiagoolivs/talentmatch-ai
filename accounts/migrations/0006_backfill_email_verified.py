"""Usuários criados antes da verificação por código são considerados verificados."""
from django.db import migrations


def mark_existing_users_verified(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.update(email_verified=True)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_user_email_verified_alter_candidateprofile_bio_and_more'),
    ]

    operations = [
        migrations.RunPython(mark_existing_users_verified, noop),
    ]
