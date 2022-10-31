from leads.models_user import UserOTP
from .test_base import ConstantMixin
from rest_framework.test import APITestCase


class TestLeadAttribute(APITestCase, ConstantMixin):

    def test_get_lead_attribute_without_auth(self):
        lead_attr_resp = self.client.get(self.LEAD_ATTR_URL)
        self.assertEqual(lead_attr_resp.status_code, 403)

    def test_get_list_with_auth(self):
        # sign up
        registration_resp = self.client.post(self.REGISTER_URL, self.USER_DATA)
        self.assertEqual(registration_resp.status_code, 200)

        # User Otp
        user_otp = UserOTP.objects.all().first()
        user_otp.is_verified = True
        user_otp.save()

        # login
        login_resp = self.client.post(self.LOGIN_URL, self.USER_DATA)
        token = login_resp.json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=token)

        # Accessing the url
        # this is return 403 insted of 200
        lead_attr_resp = self.client.get(self.LEAD_ATTR_URL)
        self.assertEqual(lead_attr_resp.status_code, 200)

        # POST, PUT and DELETE
