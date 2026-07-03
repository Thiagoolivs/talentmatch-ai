"""
Verificação de email por código OTP.

No cadastro (e na troca de email), um código de 6 dígitos é enviado para o
endereço informado. O usuário precisa digitá-lo para confirmar a conta.
"""
import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import EmailVerificationCode

logger = logging.getLogger(__name__)

CODE_LIFETIME_MINUTES = 15
RESEND_COOLDOWN_SECONDS = 60
MAX_ATTEMPTS = 5


def send_verification_code(user, force=False):
    """
    Gera e envia um novo código de verificação para o email do usuário.

    Retorna (ok, mensagem_de_erro). Respeita um cooldown de reenvio para
    evitar abuso, a menos que force=True.
    """
    latest = user.verification_codes.first()
    if not force and latest and not latest.used:
        elapsed = (timezone.now() - latest.created_at).total_seconds()
        if elapsed < RESEND_COOLDOWN_SECONDS:
            wait = int(RESEND_COOLDOWN_SECONDS - elapsed)
            return False, f'Aguarde {wait} segundos para reenviar o código.'

    user.verification_codes.filter(used=False).update(used=True)

    code = f'{secrets.randbelow(1000000):06d}'
    EmailVerificationCode.objects.create(
        user=user,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=CODE_LIFETIME_MINUTES),
    )

    subject = f'{code} é o seu código de verificação - TalentMatch'
    body = (
        f'Olá, {user.first_name or user.username}!\n\n'
        f'Seu código de verificação do TalentMatch é:\n\n'
        f'    {code}\n\n'
        f'O código expira em {CODE_LIFETIME_MINUTES} minutos.\n\n'
        f'Se você não solicitou este código, ignore este email.\n\n'
        f'Equipe TalentMatch'
    )

    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
        logger.info(f'Código de verificação enviado para {user.email}')
        return True, ''
    except Exception as e:
        logger.error(f'Falha ao enviar código de verificação para {user.email}: {e}')
        return False, 'Não foi possível enviar o email agora. Tente reenviar em instantes.'


def verify_code(user, submitted_code):
    """
    Confere o código digitado. Retorna (ok, mensagem_de_erro).
    Marca o email como verificado em caso de sucesso.
    """
    submitted_code = (submitted_code or '').strip()
    if not submitted_code:
        return False, 'Digite o código de 6 dígitos.'

    code_obj = user.verification_codes.filter(used=False).first()
    if not code_obj:
        return False, 'Nenhum código ativo. Clique em "Reenviar código".'

    if code_obj.is_expired():
        return False, 'Código expirado. Clique em "Reenviar código" para receber um novo.'

    if code_obj.attempts >= MAX_ATTEMPTS:
        return False, 'Muitas tentativas. Clique em "Reenviar código" para receber um novo.'

    if not secrets.compare_digest(code_obj.code, submitted_code):
        code_obj.attempts += 1
        code_obj.save(update_fields=['attempts'])
        remaining = MAX_ATTEMPTS - code_obj.attempts
        if remaining <= 0:
            return False, 'Muitas tentativas. Clique em "Reenviar código" para receber um novo.'
        return False, f'Código incorreto. Você ainda tem {remaining} tentativa(s).'

    code_obj.used = True
    code_obj.save(update_fields=['used'])
    user.email_verified = True
    user.save(update_fields=['email_verified'])
    logger.info(f'Email verificado com sucesso: {user.email}')
    return True, ''
