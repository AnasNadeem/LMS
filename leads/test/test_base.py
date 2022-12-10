from leads.models_user import UserOTP, Member


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
    ACCOUNT_DATA = {"name": "anas", "business_desc": {"it": "its about IT"}}

    # LeadAttributeViewSet URLs
    LEADATTR_URL = "/api/leadattribute"

    # MemberViewset URLs
    MEMBER_ATTR_URL = "/api/member"

    # LeadViewSet URLs
    LEAD_URL = "/api/lead"

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

    def login_user(self, email=DEFAULT_EMAIL):
        user_data = {"email": email, "password": "Test@123"}
        login_resp = self.client.post(self.LOGIN_URL, user_data)
        token = login_resp.json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=token)

    def create_account(self):
        resp = self.client.post(self.ACCOUNT_URL, self.ACCOUNT_DATA, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Member.objects.all().count(), 1)
        return resp.json()

    def create_leadattr(self, account_id, lead_type, name, attribute_type, value={}, verify=True):
        leadattr_data = {
            'account': account_id,
            'lead_type': lead_type,
            'name': name,
            'attribute_type': attribute_type,
            'value': value,
        }
        resp = self.client.post(self.LEADATTR_URL, leadattr_data, format="json")
        if verify:
            self.assertEqual(resp.status_code, 201)
        return resp

    def create_lead(self, account_id, main_data={}, track_data={}, post_data={}, verify=True):
        data = {
            "main": main_data,
            "track": track_data,
            "post": post_data
        }
        lead_data = {
            'account': account_id,
            'data': data
        }
        resp = self.client.post(self.LEAD_URL, lead_data, format="json")
        if verify:
            self.assertEqual(resp.status_code, 201)
        return resp
