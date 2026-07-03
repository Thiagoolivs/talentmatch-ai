from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.models import Notification

from .models import Post, PostComment, PostLike


def _company_can_post(user):
    if not user.is_authenticated or not user.is_company():
        return False
    profile = getattr(user, 'company_profile', None)
    return bool(profile and profile.is_verified())


@login_required
def feed(request):
    posts = (
        Post.objects
        .select_related('author__company_profile')
        .prefetch_related('comments__user__company_profile')
        .annotate(
            num_likes=Count('likes', distinct=True),
            num_comments=Count('comments', distinct=True),
            liked_by_me=Exists(PostLike.objects.filter(post=OuterRef('pk'), user=request.user)),
        )
        .order_by('-created_at')
    )

    paginator = Paginator(posts, 10)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'feed/feed.html', {
        'posts': page,
        'can_post': _company_can_post(request.user),
    })


@login_required
@require_POST
def create_post(request):
    if not _company_can_post(request.user):
        messages.error(request, 'Apenas empresas aprovadas podem publicar no feed.')
        return redirect('feed:index')

    content = request.POST.get('content', '').strip()
    image = request.FILES.get('image')

    if not content:
        messages.error(request, 'Escreva algo para publicar.')
        return redirect('feed:index')
    if len(content) > 3000:
        messages.error(request, 'A publicação deve ter no máximo 3000 caracteres.')
        return redirect('feed:index')
    if image and image.size > 5 * 1024 * 1024:
        messages.error(request, 'A imagem deve ter no máximo 5MB.')
        return redirect('feed:index')

    Post.objects.create(author=request.user, content=content, image=image)
    messages.success(request, 'Publicação criada!')
    return redirect('feed:index')


@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = PostLike.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    return JsonResponse({
        'liked': created,
        'count': post.likes.count(),
    })


@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    content = request.POST.get('content', '').strip()

    if not content:
        messages.error(request, 'Escreva um comentário.')
    elif len(content) > 1000:
        messages.error(request, 'O comentário deve ter no máximo 1000 caracteres.')
    else:
        PostComment.objects.create(post=post, user=request.user, content=content)
        if post.author != request.user:
            author_name = request.user.get_full_name() or request.user.username
            Notification.notify_user(
                user=post.author,
                notification_type='system',
                title='Novo comentário na sua publicação',
                message=f'{author_name} comentou: "{content[:80]}"',
                link=reverse('feed:index') + f'#post-{post.id}',
            )

    return redirect(reverse('feed:index') + f'#post-{post.id}')


@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user and not (request.user.is_staff or request.user.is_admin_user()):
        messages.error(request, 'Você não tem permissão para excluir esta publicação.')
        return redirect('feed:index')
    post.delete()
    messages.success(request, 'Publicação excluída.')
    return redirect('feed:index')


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(PostComment, id=comment_id)
    allowed = (
        comment.user == request.user
        or comment.post.author == request.user
        or request.user.is_staff
        or request.user.is_admin_user()
    )
    if not allowed:
        messages.error(request, 'Você não tem permissão para excluir este comentário.')
        return redirect('feed:index')
    post_id = comment.post_id
    comment.delete()
    return redirect(reverse('feed:index') + f'#post-{post_id}')
