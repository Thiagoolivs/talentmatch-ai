from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_page, name='chat'),
    path('send/', views.send_message, name='send'),
    path('new/', views.new_session, name='new_session'),
    path('history/', views.chat_history, name='history'),
    path('session/<int:session_id>/', views.view_session, name='view_session'),
]
