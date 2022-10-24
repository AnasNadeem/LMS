
class ConstantMixin(object):
    DEFAULT_EMAIL = 'test@gmail.com'
    BASE_URL = 'http://localhost:8000'
    REGISTER_URL = BASE_URL + '/api/user'
    LOGIN_URL = BASE_URL + '/api/user/login'
    USER_LIST_URL = BASE_URL + '/api/user'
    USER_DATA = {'email': DEFAULT_EMAIL, 'password': 'Test@123'}