from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Max
from .models import Conversation, Message
from accounts.models import User
from jobs.models import Application


@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(
        participants=request.user
    ).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')
    
    conversation_data = []
    for conv in conversations:
        other_user = conv.get_other_participant(request.user)
        last_message = conv.get_last_message()
        unread = conv.unread_count(request.user)
        
        conversation_data.append({
            'conversation': conv,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread,
        })
    
    return render(request, 'messaging/conversation_list.html', {
        'conversations': conversation_data,
    })


@login_required
def conversation_detail(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    if other_user == request.user:
        messages.error(request, 'Voce nao pode conversar consigo mesmo.')
        return redirect('messaging:list')
    
    if not can_message(request.user, other_user):
        messages.error(request, 'Voce so pode conversar com usuarios relacionados as suas candidaturas.')
        return redirect('messaging:list')
    
    conversation = get_or_create_conversation(request.user, other_user)
    
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    chat_messages = conversation.messages.select_related('sender').order_by('created_at')

    # 'chat_messages' (e não 'messages') para não colidir com o framework
    # de mensagens do Django usado nos toasts do base.html
    return render(request, 'messaging/conversation_detail.html', {
        'conversation': conversation,
        'other_user': other_user,
        'chat_messages': chat_messages,
    })


@login_required
@require_POST
def send_message(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    if other_user == request.user:
        return JsonResponse({'error': 'Voce nao pode enviar mensagem para si mesmo.'}, status=400)
    
    if not can_message(request.user, other_user):
        return JsonResponse({'error': 'Voce nao tem permissao para enviar mensagem para este usuario.'}, status=403)
    
    text = request.POST.get('text', '').strip()
    if not text:
        return JsonResponse({'error': 'Mensagem vazia.'}, status=400)
    
    conversation = get_or_create_conversation(request.user, other_user)
    
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        text=text
    )

    conversation.save()

    notify_new_message(request.user, other_user)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'text': message.text,
                'sender': request.user.username,
                'created_at': message.created_at.strftime('%H:%M'),
            }
        })
    
    return redirect('messaging:detail', user_id=user_id)


def notify_new_message(sender, recipient):
    """Notifica o destinatário sobre nova mensagem, sem duplicar enquanto houver uma não lida."""
    from django.urls import reverse
    from accounts.models import Notification

    link = reverse('messaging:detail', args=[sender.id])
    already_pending = Notification.objects.filter(
        user=recipient,
        notification_type='new_message',
        link=link,
        is_read=False
    ).exists()

    if not already_pending:
        sender_name = sender.get_full_name() or sender.username
        if sender.is_company() and hasattr(sender, 'company_profile'):
            sender_name = sender.company_profile.company_name
        Notification.notify_user(
            user=recipient,
            notification_type='new_message',
            title='Nova mensagem',
            message=f'{sender_name} enviou uma mensagem para você.',
            link=link
        )


def can_message(user1, user2):
    if user1.is_admin_user() or user2.is_admin_user():
        return True
    
    if user1.is_candidate() and user2.is_company():
        return Application.objects.filter(
            candidate=user1,
            job__company=user2
        ).exists()
    
    if user1.is_company() and user2.is_candidate():
        return Application.objects.filter(
            candidate=user2,
            job__company=user1
        ).exists()
    
    return False


def get_or_create_conversation(user1, user2):
    conversation = Conversation.objects.filter(
        participants=user1
    ).filter(
        participants=user2
    ).first()
    
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(user1, user2)
        
        application = Application.objects.filter(
            Q(candidate=user1, job__company=user2) |
            Q(candidate=user2, job__company=user1)
        ).first()
        
        if application:
            conversation.application = application
            conversation.save()
    
    return conversation


@login_required
def start_conversation(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    if request.user == application.candidate:
        other_user = application.job.company
    elif request.user == application.job.company:
        other_user = application.candidate
    else:
        messages.error(request, 'Voce nao tem permissao para iniciar esta conversa.')
        return redirect('dashboard:index')
    
    return redirect('messaging:detail', user_id=other_user.id)


@login_required
def unread_count(request):
    count = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).count()
    
    return JsonResponse({'unread_count': count})


@login_required
def sync_messages(request, user_id):
    """Retorna mensagens novas (id > after) para atualização incremental do chat."""
    other_user = get_object_or_404(User, id=user_id)

    if other_user == request.user or not can_message(request.user, other_user):
        return JsonResponse({'error': 'Sem permissao.'}, status=403)

    conversation = get_or_create_conversation(request.user, other_user)

    try:
        after = int(request.GET.get('after', 0))
    except (TypeError, ValueError):
        after = 0

    new_msgs = conversation.messages.filter(id__gt=after).select_related('sender').order_by('created_at')
    new_msgs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    return JsonResponse({
        'messages': [
            {
                'id': m.id,
                'text': m.text,
                'mine': m.sender == request.user,
                'created_at': m.created_at.strftime('%H:%M'),
            }
            for m in new_msgs
        ]
    })
