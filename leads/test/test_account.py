from leads.models_user import Account
from .test_base import ConstantMixin
from rest_framework.test import APITestCase


class TestAccount(APITestCase, ConstantMixin):

    ######################
    # ---- GET ---- #
    ######################

    def test_get_list_without_auth(self):
        account_resp = self.client.get(self.ACCOUNT_URL)
        self.assertEqual(account_resp.status_code, 403)

    def test_get_list_with_auth(self):
        self.register_user()
        self.login_user()
        resp = self.client.get(self.ACCOUNT_URL)
        self.assertEqual(resp.status_code, 200)

    ######################
    # ---- POST ---- #
    ######################

    def test_post_without_auth(self):
        account_resp = self.client.post(self.ACCOUNT_URL)
        self.assertEqual(account_resp.status_code, 403)

    def test_post_with_auth(self):
        self.register_user()
        self.login_user()

        # Incorrect config
        account_data = {
            "name": "anas",
            "business_desc": {"xyz": "Its about xyz"},  # invalid category
        }
        resp = self.client.post(self.ACCOUNT_URL, account_data)
        self.assertEqual(resp.status_code, 400)

        # Correct config
        account_data = {"name": "anas", "business_desc": {"it": "Its about IT"}}
        resp = self.client.post(self.ACCOUNT_URL, account_data, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Account.objects.all().count(), 1)

        account_resp = self.client.get(self.ACCOUNT_URL)
        self.assertEqual(len(account_resp.json()), 1)

    def test_auth_user_create_account(self):
        self.register_user()
        self.login_user()

        # POST - User A
        account_data = {"name": "anas", "business_desc": {"it": "its about IT"}}

        account_resp = self.client.post(self.ACCOUNT_URL, account_data, format="json")
        self.assertEqual(account_resp.status_code, 201)
        self.assertEqual(Account.objects.all().count(), 1)

        # GET/<pk> - By User A i.e., Admin
        account_resp = self.client.get(
            f"{self.ACCOUNT_URL}/{account_resp.json()['id']}",
            account_data,
            format="json",
        )
        self.assertEqual(account_resp.status_code, 200)

        # PUT - By User A i.e., Admin
        account_data['name'] = 'test'
        account_resp_json = account_resp.json()
        put_account_url = f"{self.ACCOUNT_URL}/{account_resp_json['id']}"
        updated_account_resp = self.client.put(put_account_url, data=account_data)
        self.assertEqual(updated_account_resp.status_code, 200)
        self.assertEqual(updated_account_resp.json()['name'], 'test')

        self.register_user(self.DEFAULT_EMAIL2)
        self.login_user(self.DEFAULT_EMAIL2)

        account_data = {
            "name": "abc update",
            "business_desc": {
                "it": "its about IT update"
            }
        }
        resp = self.client.put(put_account_url, data=account_data)
        self.assertEqual(resp.status_code, 403)
