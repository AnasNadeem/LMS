from leads.models_user import Account, UserOTP
from .test_base import ConstantMixin
from rest_framework.test import APITestCase


class TestAccount(APITestCase, ConstantMixin):

    ######################
    # ---- GET ---- #
    ######################

    def test_get_list_without_auth(self):
        account_resp = self.client.get(self.ACCOUNT_LIST_URL)
        self.assertEqual(account_resp.status_code, 403)

    def test_get_list_with_auth(self):
        # Register
        self.client.post(self.REGISTER_URL, self.USER_DATA)

        # UserOTP
        user_otp = UserOTP.objects.all().first()
        user_otp.is_verified = True
        user_otp.save()

        # Login
        login_resp = self.client.post(self.LOGIN_URL, self.USER_DATA)
        token = login_resp.json()['token']
        self.client.credentials(HTTP_AUTHORIZATION=token)

        resp = self.client.get(self.ACCOUNT_LIST_URL)
        self.assertEqual(resp.status_code, 200)

    ######################
    # ---- POST ---- #
    ######################

    def test_post_without_auth(self):
        account_resp = self.client.post(self.ACCOUNT_LIST_URL)
        self.assertEqual(account_resp.status_code, 403)

    def test_post_with_auth(self):
        # Register
        self.client.post(self.REGISTER_URL, self.USER_DATA)

        # UserOTP
        user_otp = UserOTP.objects.all().first()
        user_otp.is_verified = True
        user_otp.save()

        # Login
        login_resp = self.client.post(self.LOGIN_URL, self.USER_DATA)
        token = login_resp.json()['token']
        self.client.credentials(HTTP_AUTHORIZATION=token)

        # Incorrect config
        account_data = {'name': 'abc',
                        'business_desc': {
                            'xyz': 'Its about xyz'  # invalid category
                        }
                        }
        resp = self.client.post(self.ACCOUNT_LIST_URL, account_data)
        self.assertEqual(resp.status_code, 400)

        # Correct config
        account_data = {"name": "abc",
                        "business_desc": {
                            "it": "Its about IT"
                        }
                        }
        resp = self.client.post(self.ACCOUNT_LIST_URL, account_data, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Account.objects.all().count(), 1)

        account_resp = self.client.get(self.ACCOUNT_LIST_URL)
        self.assertEqual(len(account_resp.json()), 1)
