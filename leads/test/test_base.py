from django.test import TestCase

from rest_framework.test import APIClient


class ConstantMixin(object):
    DEFAULT_EMAIL = "test@gmail.com"
    DEFAULT_EMAIL2 = "test2@gmail.com"
    METHOD = "http://"
    DOMAIN_URL = "localhost:8000"
    METHOD = "http://"
    DOMAIN_URL = "localhost:8000"
    SUBDOMAIN_URL = "anas.localhost:8000"
    BASE_URL = METHOD + DOMAIN_URL
    SUBDOMAIN_BASE_URL = METHOD + SUBDOMAIN_URL

    # UserViewset URLs
    REGISTER_URL = BASE_URL + "/api/user"
    LOGIN_URL = BASE_URL + "/api/user/login"
    USER_LIST_URL = BASE_URL + "/api/user"
    USER_DATA = {"email": DEFAULT_EMAIL, "password": "Test@123"}
    USER2_DATA = {"email": DEFAULT_EMAIL2, "password": "Test@1234"}
    PASSWORD_CHANGE_URL = BASE_URL + "/api/user/password_change"

    # AccountViewset URLs
    BASE_ACCOUNT_URL = "/api/account"
    ACCOUNT_URL = BASE_URL + BASE_ACCOUNT_URL
    ACCOUNT_SUBDOMIN_URL = SUBDOMAIN_BASE_URL + BASE_ACCOUNT_URL

    # LeadAttributeViewSet URLs
    BASE_LEAD_ATTR_URL = "/api/leadattribute"
    LEAD_ATTR_URL = BASE_URL + BASE_LEAD_ATTR_URL

    # members
    BASE_MEMBER_URL = "/api/member"
    MEMBER_ATTR_URL = BASE_URL + BASE_MEMBER_URL
    ACCOUNT_SUBDOMAIN_URL = SUBDOMAIN_BASE_URL + BASE_ACCOUNT_URL


class BaseApiClient(APIClient):

    def __init__(self, *args, **kwargs):
        super(BaseApiClient, self).__init__(*args, **kwargs)
        self.site_domain = "localhost:8000"
        self.account_url = "{}.{}".format("anas", self.site_domain)

    def setup_account_url(self, subdomain):
        self.account_url = "{}.{}".format(subdomain, self.site_domain)

    def setup_host(self, url, kwargs):
        if self.account_url in url:
            kwargs["HTTP_HOST"] = self.account_url

    def get(self, url, *args, **kwargs):
        self.setup_host(url, kwargs)
        return super(BaseApiClient, self).get(url, *args, **kwargs)

    def put(self, url, *args, **kwargs):
        self.setup_host(url, kwargs)
        return super(BaseApiClient, self).put(url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        self.setup_host(url, kwargs)
        return super(BaseApiClient, self).post(url, *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        self.setup_host(url, kwargs)
        return super(BaseApiClient, self).delete(url, *args, **kwargs)

    def patch(self, url, *args, **kwargs):
        self.setup_host(url, kwargs)
        return super(BaseApiClient, self).patch(url, *args, **kwargs)


class BaseTestCase(TestCase):
    client_class = BaseApiClient

    def setUp(self):
        super(BaseTestCase, self).setUp()
