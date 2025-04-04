from django.urls import path
from api.views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/me/', UserRetrieveAPIView.as_view(), name='user-me'),
    path('users/create/', UserCreateAPIView.as_view(), name='user-create'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyAPIView.as_view(), name='user-action'),
    
    path('chats/', ChatListAPIView.as_view(), name='chat-list'),
    path('chats/create/', ChatCreateAPIView.as_view(), name='chat-create'),
    path('chats/<int:pk>/', ChatRetrieveUpdateDestroyAPIView.as_view(), name='chat-action'),
    
    path('messages/', MessageListAPIView.as_view(), name='message-list'),
    path('messages/create/', MessageCreateAPIView.as_view(), name='message-create'),
    path('messages/<int:pk>/', MessageRetrieveUpdateDestroyAPIView.as_view(), name='message-action'),
]