from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models import User

class UserListAPIViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test')
        self.admin = User.objects.create_superuser(username='admin', password='test')
        self.url = reverse('user-list')

    def test_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_authenticated_as_admin(self):
        self.client.login(username='admin', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

class UserRetrieveAPIViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test')
        self.admin = User.objects.create_superuser(username='admin', password='test')
        self.url = reverse('user-me')

    def test_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_authenticated_as_admin(self):
        self.client.login(username='admin', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'admin')

class UserUpdateAPIViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test')
        self.admin = User.objects.create_superuser(username='admin', password='test')
        self.url = reverse('user-create')

    def test_create_user(self):
        data = {
            "username": "newuser",
            "password": "test",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_create_user_no_password(self):
        data = {
            "username": "newuser",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)

    def test_create_user_no_username(self):
        data = {
            "password": "test",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)

    def test_create_user_username_already_exists(self):
        data = {
            "username": "testuser",
            "password": "test",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)

    def test_create_staff_user(self):
        data = {
            "username": "staffuser",
            "password": "test",
            "is_staff": True,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        user = User.objects.get(username='staffuser')
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        data = {
            "username": "superuser",
            "password": "test",
            "is_superuser": True,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        user = User.objects.get(username='superuser')
        self.assertFalse(user.is_superuser)
    
class UserRetrieveUpdateDestroyAPIViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test')
        self.admin = User.objects.create_superuser(username='admin', password='test')
        self.url = reverse('user-action', args=[self.user.pk])

    def test_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_as_admin(self):
        self.client.login(username='admin', password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_authenticated_as_admin_update(self):
        self.client.login(username='admin', password='test')
        data = {
            "is_staff": True,
        }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_authenticated_as_admin_delete(self):
        self.client.login(username='admin', password='test')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_authenticated_as_admin_delete_non_existent_user(self):
        self.client.login(username='admin', password='test')
        response = self.client.delete(reverse('user-action', args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_as_admin_update_non_existent_user(self):
        self.client.login(username='admin', password='test')
        data = {
            "is_staff": True,
        }
        response = self.client.patch(reverse('user-action', args=[999]), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        user = User.objects.get(pk=self.user.pk)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)