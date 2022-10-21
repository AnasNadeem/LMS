from rest_framework.test import APITestCase
from leads.models_user import User, Account
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

class TestAccountModel(APITestCase):
    def setUp(self):
        account = Account.objects.create(name="name")
        self.account = account

    def test_account_str(self):
        self.assertEqual(self.account.name, 'name')
        self.assertEqual(str(self.account), 'name')

# the below test are same test but with different approach 
class TestAccountView(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        BASE_URL = 'http://localhost:8000'
        ACCOUNT_URL = BASE_URL + '/api/account'
        self.account_url = ACCOUNT_URL,
        self.user = User.objects.create_user( email="test@mail.com", password="p12345678")

    def test_create_account(self):

        user = self.user
        self.client.force_login(user)
        data = {
        "name":"name",
        "subdomain":"name"
        }
        response = self.client.post('/api/account', data)
        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_see_account(self):
        user= User.objects.create_user("a@a.com", "somepass")
        self.client.force_login(user=user)
        response = self.client.get("/api/account")
        self.assertEqual(response.status_code, 200)

class TryingAuthentication(APITestCase):
    def setUp(self):
        self.login_url = '/api/user'
        self.user_data = {
        "email":"a@a.com",
        "password":"pass"

        }
        self.client.post(self.login_url, self.user_data)
        auth_url = '/api/user/login'
        self.access_token = self.client.post(auth_url, {
        "email":self.user_data.get("email"),
        "password": self.user_data.get("password")
        }).data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_account_page(self):
        response = self.client.get('/api/account')
        self.assertEqual(response.status_code, 200)
