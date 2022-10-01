from django.urls import reverse

from rest_framework.test import APITestCase
from leads.models_user import User


class TestUser(APITestCase):
    REGISTER_URL = reverse('register')
    LOGIN_URL = reverse('login')

    def test_register_incorrect_config(self):
        # Register with no data
        data = {}
        resp = self.client.post(self.REGISTER_URL, data)
        self.assertEqual(len(resp.json()), 2)
        self.assertEqual(resp.status_code, 400)

        # Register with incorrect mail
        data = {'email': 'test', 'password': 'Test'}
        resp = self.client.post(self.REGISTER_URL, data)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.status_code, 400)
        self.assertTrue('email' in resp.json())

        # Register with short password
        data = {'email': 'test@gmail.com', 'password': 't'}
        resp = self.client.post(self.REGISTER_URL, data)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.status_code, 400)
        self.assertTrue('password' in resp.json())

        # Register with already registered email
        data = {'email': 'test@gmail.com', 'password': 'Test@123'}
        User.objects.create_user(**data)
        resp = self.client.post(self.REGISTER_URL, data)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.status_code, 400)
        self.assertTrue('User already exist' in resp.json()['error'][0])

    def test_register_correct_config(self):
        # Register with correct data
        data = {'email': 'test@gmail.com', 'password': 'Test@123'}
        resp = self.client.post(self.REGISTER_URL, data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(User.objects.all().count(), 1)