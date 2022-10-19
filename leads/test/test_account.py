from rest_framework.test import APITestCase
from leads.models_user import User, Account

class TestAccountModel(APITestCase):
    def setUp(self):
        account = Account.objects.create(name="name")
        self.account = account

    def test_account_str(self):
        self.assertEqual(self.account.name, 'name')
        self.assertEqual(str(self.account), 'name')


class TestAccountView(APITestCase):
    def setUp(self):
        BASE_URL = 'http://localhost:8000'
        ACCOUNT_URL = BASE_URL + '/api/account'

    def test_create_account(self):
        pass
