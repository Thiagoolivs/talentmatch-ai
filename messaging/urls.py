from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.conversation_list, name='list'),
    path('<int:user_id>/', views.conversation_detail, name='detail'),
    path('send/<int:user_id>/', views.send_message, name='send'),
    path('start/<int:application_id>/', views.start_conversation, name='start'),
    path('unread/', views.unread_count, name='unread'),
]
