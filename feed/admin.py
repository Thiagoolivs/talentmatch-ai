from django.contrib import admin

from .models import Post, PostComment, PostLike


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'content_preview', 'created_at')
    search_fields = ('author__username', 'content')
    list_filter = ('created_at',)

    def content_preview(self, obj):
        return obj.content[:60]
    content_preview.short_description = 'Conteudo'


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'content', 'created_at')
    search_fields = ('user__username', 'content')


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
