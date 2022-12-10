from .test_base import ConstantMixin
from rest_framework.test import APITestCase
from leads.models_lead import LeadAttribute, Lead


class TestLead(APITestCase, ConstantMixin):

    ######################
    # ---- GET ---- #
    ######################

    def test_get_lead_without_auth(self):
        lead_resp = self.client.get(self.LEAD_URL)
        self.assertEqual(lead_resp.status_code, 403)

    def test_get_list_with_auth(self):
        self.register_user()
        self.create_account()
        lead_resp = self.client.get(self.LEAD_URL)
        self.assertEqual(lead_resp.status_code, 200)
        self.assertEqual(lead_resp.json(), [])
        self.assertEqual(Lead.objects.all().count(), 0)

    ######################
    # ---- POST ---- #
    ######################

    def test_post_lead(self):
        self.register_user()
        account = self.create_account()

        # LeadAttrbite - email
        email_attr = self.create_leadattr(
            account_id=account['id'],
            lead_type=LeadAttribute.LEAD_CHOICES.main,
            name='Email',
            attribute_type=LeadAttribute.ATTRIBUTE_CHOICES.email,
        ).json()

        # LeadAttrbite - name
        string_attr = self.create_leadattr(
            account_id=account['id'],
            lead_type=LeadAttribute.LEAD_CHOICES.main,
            name='Name',
            attribute_type=LeadAttribute.ATTRIBUTE_CHOICES.string,
        ).json()

        # LeadAttrbite - integer
        integer_attr = self.create_leadattr(
            account_id=account['id'],
            lead_type=LeadAttribute.LEAD_CHOICES.main,
            name='Number',
            attribute_type=LeadAttribute.ATTRIBUTE_CHOICES.integer,
        ).json()

        # LeadAttrbite - boolean
        bool_attr = self.create_leadattr(
            account_id=account['id'],
            lead_type=LeadAttribute.LEAD_CHOICES.track,
            name='Paid',
            attribute_type=LeadAttribute.ATTRIBUTE_CHOICES.boolean,
        ).json()

        # With Incorrect config
        # 1. Incorrect lead_type
        track_data = {
            email_attr['slug']: 'test@gmail.com',
            string_attr['slug']: 'test',
            integer_attr['slug']: 23,
        }
        lead_resp = self.create_lead(account['id'], track_data=track_data, verify=False)
        self.assertEqual(lead_resp.status_code, 400)
        self.assertEqual(Lead.objects.all().count(), 0)

        # 2. Incorrect leadattribute slug
        main_data = {
            'hello': 'test@gmail.com',  # incorrect
            string_attr['slug']: 'test',
            integer_attr['slug']: 23,
        }
        lead_resp = self.create_lead(account['id'], main_data=main_data, verify=False)
        self.assertEqual(lead_resp.status_code, 400)
        self.assertEqual(Lead.objects.all().count(), 0)
        self.assertTrue('lead_attribute' in lead_resp.json())

        # 3. Incorrect data of attribute_type email
        main_data = {
            email_attr['slug']: 'test',  # incorrect
            string_attr['slug']: 'test',
            integer_attr['slug']: 23,
        }
        lead_resp = self.create_lead(account['id'], main_data=main_data, verify=False)
        self.assertEqual(lead_resp.status_code, 400)
        self.assertEqual(Lead.objects.all().count(), 0)
        self.assertTrue(email_attr['slug'] in lead_resp.json())

        # 4. Incorrect data of attribute_type string
        main_data = {
            email_attr['slug']: 'test@gmail.com',
            string_attr['slug']: 23,  # incorrect
            integer_attr['slug']: 23,
        }
        lead_resp = self.create_lead(account['id'], main_data=main_data, verify=False)
        self.assertEqual(lead_resp.status_code, 400)
        self.assertEqual(Lead.objects.all().count(), 0)
        self.assertTrue(string_attr['slug'] in lead_resp.json())

        # 4. Incorrect data of attribute_type integer
        main_data = {
            email_attr['slug']: 'test@gmail.com',
            string_attr['slug']: 'test',
            integer_attr['slug']: 'test',  # incorrect
        }
        lead_resp = self.create_lead(account['id'], main_data=main_data, verify=False)
        self.assertEqual(lead_resp.status_code, 400)
        self.assertEqual(Lead.objects.all().count(), 0)
        self.assertTrue(integer_attr['slug'] in lead_resp.json())

        # 5. Incorrect data of attribute_type boolean
        main_data = {
            email_attr['slug']: 'test@gmail.com',
            string_attr['slug']: 'test',
            integer_attr['slug']: 23,
        }
        track_data = {
            bool_attr['slug']: 'hello',  # incorrect
        }
        lead_resp = self.create_lead(account['id'], main_data=main_data, track_data=track_data, verify=False)
        self.assertEqual(lead_resp.status_code, 400)
        self.assertEqual(Lead.objects.all().count(), 0)
        self.assertTrue(bool_attr['slug'] in lead_resp.json())

        # 5. Correct data
        main_data = {
            email_attr['slug']: 'test@gmail.com',
            string_attr['slug']: 'test',
            integer_attr['slug']: 23,
        }
        track_data = {
            bool_attr['slug']: False
        }
        lead_resp = self.create_lead(account['id'], main_data=main_data, track_data=track_data, verify=False)
        self.assertEqual(lead_resp.status_code, 201)
        self.assertEqual(Lead.objects.all().count(), 1)

    # ######################
    # # ---- PUT ---- #
    # ######################

    # def test_put_leadattribute_from_diff_user(self):
    #     self.register_user()
    #     account = self.create_account()

    #     resp = self.create_leadattr(
    #         account_id=account['id'],
    #         lead_type=LeadAttribute.LEAD_CHOICES.main,
    #         name='Email',
    #         attribute_type=LeadAttribute.ATTRIBUTE_CHOICES.email,
    #     ).json()
    #     self.assertEqual(resp['name'], 'Email')

    #     resp['name'] = 'Name'
    #     resp['attribute_type'] = LeadAttribute.ATTRIBUTE_CHOICES.string
    #     put_leadattr_url = f"{self.LEADATTR_URL}/{resp['id']}"
    #     updated_resp = self.client.put(put_leadattr_url, data=resp)
    #     self.assertEqual(updated_resp.status_code, 403)

    #     leadattr_resp = self.client.get(put_leadattr_url)
    #     self.assertEqual(leadattr_resp.json()['name'], 'Email')
    #     self.assertEqual(leadattr_resp.json()['attribute_type'], LeadAttribute.ATTRIBUTE_CHOICES.email)

    # def test_put_leadattribute(self):
    #     self.register_user()
    #     account = self.create_account()

    #     resp = self.create_leadattr(
    #         account_id=account['id'],
    #         lead_type=LeadAttribute.LEAD_CHOICES.main,
    #         name='Email',
    #         attribute_type=LeadAttribute.ATTRIBUTE_CHOICES.email,
    #     ).json()
    #     self.assertEqual(resp['name'], 'Email')

    #     resp['name'] = 'Name'
    #     resp['attribute_type'] = LeadAttribute.ATTRIBUTE_CHOICES.string
    #     put_leadattr_url = f"{self.LEADATTR_URL}/{resp['id']}"
    #     updated_resp = self.client.put(put_leadattr_url, data=resp)
    #     self.assertEqual(updated_resp.status_code, 200)
    #     self.assertEqual(updated_resp.json()['name'], 'Name')
    #     self.assertEqual(updated_resp.json()['attribute_type'], LeadAttribute.ATTRIBUTE_CHOICES.string)

    # ######################
    # # ---- DELETE ---- #
    # ######################

    # def test_delete_leadattribute(self):
    #     self.register_user()
    #     account = self.create_account()

    #     email_attr = self.create_leadattr(
    #         account_id=account['id'],
    #         lead_type=LeadAttribute.LEAD_CHOICES.main,
    #         name='Email',
    #         attribute_type=LeadAttribute.ATTRIBUTE_CHOICES.email,
    #     ).json()

    #     string_attr = self.create_leadattr(
    #         account_id=account['id'],
    #         lead_type=LeadAttribute.LEAD_CHOICES.main,
    #         name='Name',
    #         attribute_type=LeadAttribute.ATTRIBUTE_CHOICES.string,
    #     ).json()
