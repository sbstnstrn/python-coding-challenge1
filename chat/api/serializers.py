from api.models import User, Chat, Message
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'is_staff', 'is_superuser', 'chats', 'messages')
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
            "is_staff": {"default": False},
            "is_superuser": {"default": False},
        }           

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ('id', 'user', 'messages', 'archived', 'created_at', 'updated_at')

    def validate_user(self, value):
        raise ValidationError("You cannot modify the user field.")
    
class ChatCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Chat
        fields = ('user',)

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('user', 'chat', 'content', 'archived', 'created_at', 'updated_at')

class MessageCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all())

    class Meta:
        model = Message
        fields = ('user', 'chat', 'content')
