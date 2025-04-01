from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models import User, Chat, Message

class MessageListAPIView(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test')
        self.admin = User.objects.create_superuser(username='admin', password='test')
        self.url = reverse('message-list')

    def test_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for message in response.data['results']:
            self.assertEqual(message['user'], self.user.id)
     
    def test_authenticated_as_admin(self):
        self.client.login(username='admin', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), self.user.messages.count())

class MessageCreateAPIView(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test')
        self.admin = User.objects.create_superuser(username='admin', password='test')
        self.chat = Chat.objects.create(user=self.user)
        self.url = reverse('message-create')

    def test_not_authenticated(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated(self):
        self.client.login(username='testuser', password='test')
        data = {
            "user": self.user.pk,
            "chat": 1,
            "content": "Hello!",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], "Hello!")
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.last().user, self.user)
        self.assertEqual(Message.objects.last().chat, self.chat)
        self.assertEqual(Message.objects.last().content, "Hello!")

class MessageRetrieveUpdateDestroyAPIViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test')
        self.admin = User.objects.create_superuser(username='admin', password='test')
        self.chat = Chat.objects.create(user=self.user)
        self.message = Message.objects.create(user=self.user, chat=self.chat, content="Hello!")
        self.url = reverse('message-detail', args=[self.message.pk])

    def test_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], "Hello!")
    
    def test_authenticated_modify(self):
        self.client.login(username='testuser', password='test')
        data = {
            "content": "Updated content",
        }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.message.refresh_from_db()
        self.assertEqual(self.message.content, "Updated content")

    def test_authenticated_delete(self):
        self.client.login(username='testuser', password='test')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Message.objects.count(), 0)

    def test_authenticated_as_admin(self):
        self.client.login(username='admin', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], "Hello!")

    def test_authenticated_as_admin_modify(self):
        self.client.login(username='admin', password='test')
        data = {
            "content": "Admin updated content",
        }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_as_admin_delete(self):
        self.client.login(username='admin', password='test')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Message.objects.count(), 1)