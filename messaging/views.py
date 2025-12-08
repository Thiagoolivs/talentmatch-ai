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
    
    return render(request, 'messaging/conversation_detail.html', {
        'conversation': conversation,
        'other_user': other_user,
        'messages': chat_messages,
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
