"""Context processors para dados globais de templates (notificações e mensagens)."""


def notifications(request):
    if not request.user.is_authenticated:
        return {}

    from accounts.models import Notification
    from messaging.models import Message

    user_notifications = Notification.objects.filter(user=request.user)

    unread_messages_count = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).count()

    return {
        'unread_notifications_count': user_notifications.filter(is_read=False).count(),
        'recent_notifications': user_notifications[:8],
        'unread_messages_count': unread_messages_count,
    }
