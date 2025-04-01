from django.urls import path
from . import views

urlpatterns = [
     path('users/', views.user_list, name='user_list'),
    path('room/<int:other_id>/', views.chat_room, name='chat_room'),
    path('room/<str:room_name>/', views.generic_chat_room, name='chat_room'),

]
