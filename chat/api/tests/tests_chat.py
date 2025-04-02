from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models import Chat, User

class ChatListAPIViewTests(APITestCase): 
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test')
        self.chat = Chat.objects.create(user=self.user)
        self.url = reverse('chat-list')
        
    def test_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['user'], self.user.pk)

class ChatCreateAPIViewTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='test')
        self.user = User.objects.create_user(username='testuser', password='test')
        self.url = reverse('chat-create')

    def test_not_authenticated(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated(self):
        self.client.login(username='testuser', password='test')
        user = User.objects.get(username='testuser')
        data = {
            "user": user.pk,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Chat.objects.count(), 1)
        self.assertEqual(Chat.objects.last().user, user)
    
    def test_authenticated_as_admin(self):
        self.client.login(username='admin', password='test')
        user = User.objects.get(username='admin')
        data = {
            "user": user.pk,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Chat.objects.count(), 1)
        self.assertEqual(Chat.objects.last().user, user)

class ChatRetrieveUpdateDestroyAPIView(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='test')
        self.user = User.objects.create_user(username='testuser', password='test')
        self.user2 = User.objects.create_user(username='testuser2', password='test')
        self.chat = Chat.objects.create(user=self.user)
        self.url = reverse('chat-action', args=[self.chat.pk])

    def test_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_non_owner(self):
        self.client.login(username='testuser2', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_as_owner(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.pk)

    def test_authenticated_as_admin(self):
        self.client.login(username='admin', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.pk)

    def test_not_authenticated_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Chat.objects.count(), 1)
    
    def test_authenticated_delete(self):
        self.client.login(username='testuser', password='test')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Chat.objects.count(), 1)

    def test_authenticated_as_admin_delete(self):
        self.client.login(username='admin', password='test')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Chat.objects.count(), 0)

    def test_authenticated_as_admin_delete_non_existent_chat(self):
        self.client.login(username='admin', password='test')
        response = self.client.delete(reverse('chat-action', args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Chat.objects.count(), 1)

    def test_authenticated_as_admin_update_chat(self):
        self.client.login(username='admin', password='test')
        data = {
            "archived": True,
        }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        chat = Chat.objects.get(pk=self.chat.pk)
        self.assertTrue(chat.archived)

    def test_authenticated_as_admin_update_non_existent_chat(self):
        self.client.login(username='admin', password='test')
        data = {
            "archived": True,
        }
        response = self.client.patch(reverse('chat-action', args=[999]), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_as_admin_update_chat_with_invalid_data(self):
        self.client.login(username='admin', password='test')
        data = {
            "archived": "invalid_value",
        }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_as_admin_update_chat_read_only_field(self):
        self.client.login(username='admin', password='test')
        data = {
            "user": self.user2.pk,
        }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        chat = Chat.objects.get(pk=self.chat.pk)
        self.assertEqual(chat.user, self.user)