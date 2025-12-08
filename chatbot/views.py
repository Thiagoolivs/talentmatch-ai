import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ChatSession, ChatMessage
from .ai_engine import get_ai_response


@login_required
def chat_page(request):
    session, created = ChatSession.objects.get_or_create(
        user=request.user,
        is_active=True,
        defaults={}
    )
    
    messages = session.messages.all()[:50]
    
    return render(request, 'chatbot/chat.html', {
        'session': session,
        'messages': messages
    })


@login_required
@require_POST
def send_message(request):
    """Endpoint para enviar mensagem com suporte a CSRF."""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Mensagem vazia'}, status=400)
        
        session, created = ChatSession.objects.get_or_create(
            user=request.user,
            is_active=True
        )
        
        ChatMessage.objects.create(
            session=session,
            role='user',
            content=user_message
        )
        
        ai_response = get_ai_response(request.user, user_message, session)
        
        ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=ai_response
        )
        
        session.save()
        
        return JsonResponse({
            'response': ai_response,
            'success': True
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados invalidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Erro interno. Tente novamente.'}, status=500)


@login_required
@require_POST
def new_session(request):
    """Cria nova sessao de chat."""
    ChatSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
    
    ChatSession.objects.create(user=request.user, is_active=True)
    
    return JsonResponse({'success': True, 'message': 'Nova sessao iniciada'})


@login_required
def chat_history(request):
    sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')[:10]
    
    sessions_with_messages = []
    for session in sessions:
        first_message = session.messages.filter(role='user').first()
        sessions_with_messages.append({
            'session': session,
            'first_message': first_message.content[:50] if first_message else 'Sem mensagens',
            'message_count': session.messages.count()
        })
    
    return render(request, 'chatbot/history.html', {
        'sessions': sessions_with_messages
    })


@login_required
def view_session(request, session_id):
    """Visualiza uma sessao especifica do historico."""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    messages = session.messages.all()
    
    return render(request, 'chatbot/chat.html', {
        'session': session,
        'messages': messages,
        'view_only': not session.is_active
    })
