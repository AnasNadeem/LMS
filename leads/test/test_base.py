
class ConstantMixin(object):
    DEFAULT_EMAIL = 'test@gmail.com'
    DEFAULT_EMAIL2 = "test2@gmail.com"
    METHOD = 'http://'
    DOMAIN_URL = 'localhost:8000'
    BASE_URL = METHOD + DOMAIN_URL

    # UserViewset URLs
    REGISTER_URL = BASE_URL + '/api/user'
    LOGIN_URL = BASE_URL + '/api/user/login'
    USER_LIST_URL = BASE_URL + '/api/user'
    USER_DATA = {'email': DEFAULT_EMAIL, 'password': 'Test@123'}
    USER2_DATA = {'email': DEFAULT_EMAIL2, 'password': 'Test@1234'}

    # AccountViewset URLs
    BASE_ACCOUNT_URL = '/api/account'
    ACCOUNT_URL = BASE_URL + BASE_ACCOUNT_URL
