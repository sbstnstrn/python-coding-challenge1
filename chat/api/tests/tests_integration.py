from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models import User, Chat, Message

class MessageChatIntegrationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test')
        self.admin = User.objects.create_superuser(username='admin', password='test')
        self.chat = Chat.objects.create(user=self.user)
        self.message_user = Message.objects.create(user=self.user, chat=self.chat, content="Hello!")
        self.message_admin = Message.objects.create(user=self.admin, chat=self.chat, content="Hi!")


    def test_chat_archive(self):
        self.client.login(username='admin', password='test')
        url = reverse('chat-action', args=[self.chat.pk])
        data = {
            "archived": True,
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.chat.refresh_from_db()
        self.assertTrue(self.chat.archived)
        self.message_user.refresh_from_db()
        self.assertTrue(self.message_user.archived)
        self.message_admin.refresh_from_db()
        self.assertTrue(self.message_admin.archived)

    def test_message_create_with_chat(self):
        self.client.login(username='testuser', password='test')
        url = reverse('message-create')
        data = {
            "user": self.user.pk,
            "chat": self.chat.pk,
            "content": "New message",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 3)
        self.assertEqual(Message.objects.last().content, "New message")

    def test_chat_delete_with_messages(self):
        self.client.login(username='admin', password='test')
        url = reverse('chat-action', args=[self.chat.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Chat.objects.count(), 0)
        self.assertEqual(Message.objects.count(), 0)

