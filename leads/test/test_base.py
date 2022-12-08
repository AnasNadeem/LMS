
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
