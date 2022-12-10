from .test_base import ConstantMixin
from rest_framework.test import APITestCase
from leads.models_lead import LeadAttribute


class TestLeadAttribute(APITestCase, ConstantMixin):

    ######################
    # ---- GET ---- #
    ######################

    def test_get_leadattribute_without_auth(self):
        leadattr_resp = self.client.get(self.LEADATTR_URL)
        self.assertEqual(leadattr_resp.status_code, 403)

    def test_get_list_with_auth(self):
        self.register_user()
        self.login_user()
        self.create_account()
        leadattr_resp = self.client.get(self.LEADATTR_URL)
        self.assertEqual(leadattr_resp.status_code, 200)
        self.assertEqual(leadattr_resp.json(), [])

    ######################
    # ---- POST ---- #
    ######################

    def test_post_incorrect_config(self):
        self.register_user()
        self.login_user()
        account = self.create_account()
        resp = self.create_leadattr(
            account_id=account['id'],
            lead_type='blah',
            name='Email',
            attribute_type=LeadAttribute.ATTRIBUTE_CHOICES.email,
            verify=False
        )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue('lead_type' in resp.json())

    def test_post_correct_config(self):
        self.register_user()
        self.login_user()
        account = self.create_account()
        resp = self.create_leadattr(
            account_id=account['id'],
            lead_type=LeadAttribute.LEAD_CHOICES.main,
            name='Email',
            attribute_type=LeadAttribute.ATTRIBUTE_CHOICES.email,
        ).json()
        self.assertEqual(resp['name'], 'Email')

    ######################
    # ---- PUT ---- #
    ######################

    def test_put_leadattribute_from_diff_user(self):
        self.register_user()
        self.login_user()
        account = self.create_account()

        resp = self.create_leadattr(
            account_id=account['id'],
            lead_type=LeadAttribute.LEAD_CHOICES.main,
            name='Email',
            attribute_type=LeadAttribute.ATTRIBUTE_CHOICES.email,
        ).json()
        self.assertEqual(resp['name'], 'Email')

        self.register_user(self.DEFAULT_EMAIL2)
        self.login_user(self.DEFAULT_EMAIL2)
        resp['name'] = 'Name'
        resp['attribute_type'] = LeadAttribute.ATTRIBUTE_CHOICES.string
        put_leadattr_url = f"{self.LEADATTR_URL}/{resp['id']}"
        updated_resp = self.client.put(put_leadattr_url, data=resp)
        self.assertEqual(updated_resp.status_code, 403)

        self.login_user(self.DEFAULT_EMAIL)
        leadattr_resp = self.client.get(put_leadattr_url)
        self.assertEqual(leadattr_resp.json()['name'], 'Email')
        self.assertEqual(leadattr_resp.json()['attribute_type'], LeadAttribute.ATTRIBUTE_CHOICES.email)

    def test_put_leadattribute(self):
        self.register_user()
        self.login_user()
        account = self.create_account()

        resp = self.create_leadattr(
            account_id=account['id'],
            lead_type=LeadAttribute.LEAD_CHOICES.main,
            name='Email',
            attribute_type=LeadAttribute.ATTRIBUTE_CHOICES.email,
        ).json()
        self.assertEqual(resp['name'], 'Email')

        resp['name'] = 'Name'
        resp['attribute_type'] = LeadAttribute.ATTRIBUTE_CHOICES.string
        put_leadattr_url = f"{self.LEADATTR_URL}/{resp['id']}"
        updated_resp = self.client.put(put_leadattr_url, data=resp)
        self.assertEqual(updated_resp.status_code, 200)
        self.assertEqual(updated_resp.json()['name'], 'Name')
        self.assertEqual(updated_resp.json()['attribute_type'], LeadAttribute.ATTRIBUTE_CHOICES.string)

    ######################
    # ---- DELETE ---- #
    ######################

    def test_delete_leadattribute(self):
        self.register_user()
        self.login_user()
        account = self.create_account()

        resp = self.create_leadattr(
            account_id=account['id'],
            lead_type=LeadAttribute.LEAD_CHOICES.main,
            name='Email',
            attribute_type=LeadAttribute.ATTRIBUTE_CHOICES.email,
        ).json()
        self.assertEqual(resp['name'], 'Email')

        delete_leadattr_url = f"{self.LEADATTR_URL}/{resp['id']}"
        updated_resp = self.client.delete(delete_leadattr_url)
        self.assertEqual(updated_resp.status_code, 204)
        self.assertEqual(LeadAttribute.objects.all().count(), 0)
