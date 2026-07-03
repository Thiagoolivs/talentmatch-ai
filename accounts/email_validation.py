"""
Validação de entregabilidade de email via API externa.

Usa a AbstractAPI Email Validation (https://www.abstractapi.com/api/email-verification-validation-api)
quando a variável de ambiente EMAIL_VALIDATION_API_KEY está configurada.
Sem a chave, aplica apenas o bloqueio local de domínios descartáveis.

A validação é fail-open: indisponibilidade da API nunca bloqueia um cadastro.
"""
import logging
import os

import requests
from django.core.cache import cache
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

ABSTRACT_API_URL = 'https://emailvalidation.abstractapi.com/v1/'
CACHE_TTL_SECONDS = 60 * 60 * 24
REQUEST_TIMEOUT_SECONDS = 6

MSG_UNDELIVERABLE = 'Este email parece não existir. Verifique se digitou corretamente.'
MSG_DISPOSABLE = 'Emails temporários/descartáveis não são aceitos. Use um email permanente.'

# Fallback local: domínios de email descartável mais comuns.
DISPOSABLE_DOMAINS = {
    '10minutemail.com', 'burnermail.io', 'discard.email', 'dispostable.com',
    'emailondeck.com', 'fakeinbox.com', 'getnada.com', 'guerrillamail.com',
    'guerrillamail.info', 'guerrillamail.net', 'inboxkitten.com', 'maildrop.cc',
    'mailinator.com', 'mailnesia.com', 'mintemail.com', 'mohmal.com',
    'mytemp.email', 'sharklasers.com', 'spamgourmet.com', 'temp-mail.org',
    'tempinbox.com', 'tempmail.com', 'tempmail.dev', 'tempr.email',
    'throwaway.email', 'trashmail.com', 'yopmail.com',
}


def validate_email_deliverability(email):
    """
    Valida se o email existe e não é descartável.

    Levanta ValidationError quando o email é reprovado.
    Retorna silenciosamente quando aprovado ou quando a verificação
    não pode ser concluída (sem chave de API, erro de rede, etc.).
    """
    email = (email or '').strip().lower()
    if not email or '@' not in email:
        return

    domain = email.rsplit('@', 1)[1]
    if domain in DISPOSABLE_DOMAINS:
        raise ValidationError(MSG_DISPOSABLE)

    api_key = os.environ.get('EMAIL_VALIDATION_API_KEY', '').strip()
    if not api_key:
        return

    cache_key = f'email_validation:{email}'
    verdict = cache.get(cache_key)

    if verdict is None:
        verdict = _query_api(api_key, email)
        if verdict is None:
            return
        cache.set(cache_key, verdict, CACHE_TTL_SECONDS)

    if verdict == 'undeliverable':
        raise ValidationError(MSG_UNDELIVERABLE)
    if verdict == 'disposable':
        raise ValidationError(MSG_DISPOSABLE)


def _query_api(api_key, email):
    """Consulta a AbstractAPI. Retorna 'ok', 'undeliverable', 'disposable' ou None (indisponível)."""
    try:
        response = requests.get(
            ABSTRACT_API_URL,
            params={'api_key': api_key, 'email': email},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()

        valid_format = data.get('is_valid_format', {}).get('value', True)
        deliverability = data.get('deliverability', 'UNKNOWN')
        disposable = data.get('is_disposable_email', {}).get('value', False)

        if not valid_format or deliverability == 'UNDELIVERABLE':
            return 'undeliverable'
        if disposable:
            return 'disposable'
        return 'ok'
    except Exception as e:
        logger.warning(f'Validação de email via API indisponível para {email}: {e}')
        return None
