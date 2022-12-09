from .test_base import ConstantMixin
from rest_framework.test import APITestCase
from leads.models_lead import LeadAttribute


class TestLeadAttribute(APITestCase, ConstantMixin):

    ######################
    # ---- GET ---- #
    ######################

    def test_get_lead_attribute_without_auth(self):
        lead_attr_resp = self.client.get(self.LEAD_ATTR_URL)
        self.assertEqual(lead_attr_resp.status_code, 403)

    def test_get_list_with_auth(self):
        self.register_user()
        self.create_account()
        lead_attr_resp = self.client.get(self.LEAD_ATTR_URL)
        self.assertEqual(lead_attr_resp.status_code, 200)
        self.assertEqual(lead_attr_resp.json(), [])

    ######################
    # ---- POST ---- #
    ######################

    def test_post_incorrect_config(self):
        self.register_user()
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
        account = self.create_account()
        resp = self.create_leadattr(
            account_id=account['id'],
            lead_type=LeadAttribute.LEAD_CHOICES.main,
            name='Email',
            attribute_type=LeadAttribute.ATTRIBUTE_CHOICES.email,
        ).json()
        self.assertEqual(resp['name'], 'Email')
