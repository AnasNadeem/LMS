from .test_base import ConstantMixin
from rest_framework.test import APITestCase


class TestLeadAttribute(APITestCase, ConstantMixin):

    def test_get_lead_attribute_without_auth(self):
        lead_attr_resp = self.client.get(self.LEAD_ATTR_URL)
        self.assertEqual(lead_attr_resp.status_code, 403)

    def test_get_list_with_auth(self):
        self.register_user()

        # GET
        # lead_attr_resp = self.client.get(self.LEAD_ATTR_URL)
        # self.assertEqual(lead_attr_resp.status_code, 200)
        # POST
        # PUT
        # DELETE
