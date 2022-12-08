from leads.models_user import UserOTP


class ConstantMixin(object):
    DEFAULT_EMAIL = "test@gmail.com"
    DEFAULT_EMAIL2 = "test2@gmail.com"

    # UserViewset URLs
    REGISTER_URL = "/api/user"
    LOGIN_URL = "/api/user/login"
    USER_LIST_URL = "/api/user"
    USER_DATA = {"email": DEFAULT_EMAIL, "password": "Test@123"}
    USER2_DATA = {"email": DEFAULT_EMAIL2, "password": "Test@1234"}
    PASSWORD_CHANGE_URL = "/api/user/password_change"

    # AccountViewset URLs
    ACCOUNT_URL = "/api/account"

    # LeadAttributeViewSet URLs
    LEAD_ATTR_URL = "/api/leadattribute"

    # members
    MEMBER_ATTR_URL = "/api/member"

    def register_user(self, email=DEFAULT_EMAIL):
        user_data = {"email": email, "password": "Test@123"}
        # Register
        self.client.post(self.REGISTER_URL, user_data)

        # UserOTP
        user_otp = UserOTP.objects.filter(is_verified=False).first()
        user_otp.is_verified = True
        user_otp.save()

        # Login
        login_resp = self.client.post(self.LOGIN_URL, user_data)
        token = login_resp.json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=token)
