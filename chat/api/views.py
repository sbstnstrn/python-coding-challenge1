from django.shortcuts import render
from api.models import User, Chat, Message
from api.serializers import UserSerializer, ChatSerializer, ChatCreateSerializer, MessageSerializer, MessageCreateSerializer
from rest_framework import filters, generics, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        if request.user.is_superuser or request.user.is_staff:
            return True
        return False
    
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all().order_by('pk')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(pk=self.request.user.pk)
        return qs

class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all().order_by('pk')
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        serializer.save(is_staff=False, is_superuser=False)

class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all().order_by('pk')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class ChatListAPIView(generics.ListAPIView):
    queryset = Chat.objects.all().order_by('pk')
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

class ChatCreateAPIView(generics.CreateAPIView):
    queryset = Chat.objects.all().order_by('pk')
    serializer_class = ChatCreateSerializer
    permission_classes = [IsAuthenticated]

class ChatRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chat.objects.all().order_by('pk')
    serializer_class = ChatSerializer
    permission_classes = [IsAdminUser]

class ChatRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Chat.objects.all().order_by('pk')
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]    

class MessageListAPIView(generics.ListAPIView):
    queryset = Message.objects.all().order_by('pk')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

class MessageCreateAPIView(generics.CreateAPIView):
    queryset = Chat.objects.all().order_by('pk')
    serializer_class = MessageCreateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        chat_id = self.request.data.get('chat')
        chat = get_object_or_404(Chat, id=chat_id)

        if chat.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You can only post messages in chats you created.")
        serializer.save(user=self.request.user, chat=chat)
    
class MessageRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all().order_by('pk')
    serializer_class = MessageSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsOwner()]
        return super().get_permissions()

