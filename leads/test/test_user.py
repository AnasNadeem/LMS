from leads.models_user import User, UserOTP
from .test_base import ConstantMixin
from rest_framework.test import APITestCase


class TestUser(APITestCase, ConstantMixin):

    ######################
    # ---- REGISTER ---- #
    ######################

    def test_register_incorrect_config(self):
        # Register with no data
        data = {}
        resp = self.client.post(self.REGISTER_URL, data)
        self.assertEqual(len(resp.json()), 2)
        self.assertEqual(resp.status_code, 400)

        # Register with incorrect mail
        data = {"email": "test", "password": "Test"}
        resp = self.client.post(self.REGISTER_URL, data)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.status_code, 400)
        self.assertTrue("email" in resp.json())

        # Register with short password
        data = {"email": "test@gmail.com", "password": "t"}
        resp = self.client.post(self.REGISTER_URL, data)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.status_code, 400)
        self.assertTrue("password" in resp.json())

        # Register with already registered email
        data = {"email": "test@gmail.com", "password": "Test@123"}
        User.objects.create_user(**data)
        resp = self.client.post(self.REGISTER_URL, data)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.status_code, 400)
        self.assertTrue("User already exist" in resp.json()["error"][0])

    def test_register_correct_config(self):
        # Register with correct data
        data = {"email": "test@gmail.com", "password": "Test@123"}
        resp = self.client.post(self.REGISTER_URL, data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(User.objects.all().count(), 1)

    ######################
    # ---- LOGIN ---- #
    ######################

    def test_login_incorrect_config(self):
        # Login with not registered mail
        data = {"email": "test@gmail.com", "password": "Test"}
        resp = self.client.post(self.LOGIN_URL, data)
        self.assertEqual(resp.status_code, 400)

    def test_login_correct_config(self):
        # Login with correct data
        data = {"email": "test@gmail.com", "password": "Test@123"}
        self.client.post(self.REGISTER_URL, data)
        resp = self.client.post(self.LOGIN_URL, data)
        self.assertEqual(resp.status_code, 200)

    ######################
    # ---- USER LIST ---- #
    ######################

    def test_get_user_list_without_auth(self):
        # Request without authentication
        resp = self.client.get(self.USER_LIST_URL)
        self.assertEqual(resp.status_code, 403)

    def test_get_user_list_with_auth(self):
        # Register
        self.client.post(self.REGISTER_URL, self.USER_DATA)

        # UserOTP
        user_otp = UserOTP.objects.all().first()
        user_otp.is_verified = True
        user_otp.save()

        # Login
        login_resp = self.client.post(self.LOGIN_URL, self.USER_DATA)
        token = login_resp.json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=token)

        resp = self.client.get(self.USER_LIST_URL)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
