from rest_framework.test import APITestCase
from leads.models_user import User, Account
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse


class TestAccountModel(APITestCase):
    def setUp(self):
        account = Account.objects.create(name="name")
        self.account = account

    def test_account_str(self):
        self.assertEqual(self.account.name, 'name')
        self.assertEqual(str(self.account), 'name')

# the below test are same test but with different approach 
class TestAccountView(APITestCase):
    print('start test')
    def setUp(self):
        #create authenticated user 
        self.base_url = 'http://localhost:8000'
        self.register_url = self.base_url + '/api/user'
        self.login_url = self.base_url + '/api/user/login'
        self.account_url = self.base_url + '/api/account'
        self.user = User.objects.create_user("email" "test@test.com","password" "testpassword")
        client = APIClient

    def test_list_account_view(self):
        print("list account view test starts from here")
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.client.login(user=self.user)
        response = self.client.get(self.account_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        

        
        
        

        
        