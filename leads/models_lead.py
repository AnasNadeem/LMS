import phonenumbers
from autoslug import AutoSlugField
from rest_framework.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models
from model_utils import Choices
from leads.models_base import TimeBaseModel
from leads.models_user import Account, Member
from autoslug.settings import slugify as default_slugify


def custom_slugify(value):
    return default_slugify(value).replace('-', '_')


class LeadAttribute(TimeBaseModel):
    LEAD_CHOICES = Choices(
        ('main', 'Main Lead'),
        ('track', 'Track Lead'),
        ('post', 'Post Lead'),
    )

    ATTRIBUTE_CHOICES = Choices(
        ('boolean', 'Boolean'),
        ('choices', 'Choices'),
        ('email', 'Email'),
        ('integer', 'Integer'),
        ('phone_number', 'Phone Number'),
        ('string', 'String'),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    lead_type = models.CharField(max_length=10, choices=LEAD_CHOICES)
    name = models.CharField(max_length=250)
    slug = AutoSlugField(custom_slugify, populate_from='name', unique_with=('account', 'lead_type'))
    attribute_type = models.CharField(max_length=50, choices=ATTRIBUTE_CHOICES)
    value = models.JSONField(default=dict, null=True, blank=True)
    seq_no = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} {self.lead_type}"


class Lead(TimeBaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    data = models.JSONField(default=dict(main={}, track={}, post={}), null=True, blank=True)

    def clean(self):
        super().clean()
        data = self.data
        if len(data.keys()) != 3:
            raise ValidationError("Invalid json data for 'data' field.")

        lead_choices = [LeadAttribute.LEAD_CHOICES.main,
                        LeadAttribute.LEAD_CHOICES.track,
                        LeadAttribute.LEAD_CHOICES.post]
        for data_lead_choice in data.keys():
            if data_lead_choice not in lead_choices:
                raise ValidationError(f"'{data_lead_choice}' is not a valid lead choice.")

        all_lead_attributes = self.account.leadattribute_set.all()
        for lead_type, lead_data in data.items():
            lead_attributes = all_lead_attributes.filter(lead_type=lead_type)
            self.clean_lead_data(lead_type, lead_data, lead_attributes)

    def clean_lead_data(self, lead_type, lead_data, lead_attributes):
        for lead_attr, lead_value in lead_data.items():
            lead_attribute = lead_attributes.filter(slug=lead_attr).first()
            if not lead_attribute:
                raise ValidationError(f"Invalid lead attribute '{lead_attr}' for lead type '{lead_type}'.")

            # Email Validation
            if lead_attribute.lead_type == LeadAttribute.ATTRIBUTE_CHOICES.email:
                try:
                    validate_email(lead_value)
                except Exception as e:
                    e.message = f"Invalid email '{lead_value}' for field {lead_attribute.name}."
                    raise ValidationError(e.message)

            # String Validation
            if lead_attribute.lead_type == LeadAttribute.ATTRIBUTE_CHOICES.string:
                if not isinstance(lead_value, str):
                    raise ValidationError(f"Invalid string '{lead_value}' for field {lead_attribute.name}.")

            # Integer Validation
            if lead_attribute.lead_type == LeadAttribute.ATTRIBUTE_CHOICES.integer:
                if not isinstance(lead_value, int):
                    raise ValidationError(f"Invalid integer '{lead_value}' for field {lead_attribute.name}.")

            # Phone Number Validation
            if lead_attribute.lead_type == LeadAttribute.ATTRIBUTE_CHOICES.phone_number:
                phone_num = phonenumbers.parse(lead_value)
                if not phonenumbers.is_valid_number(phone_num):
                    raise ValidationError(f"Invalid phone number '{lead_value}' for field {lead_attribute.name}")

            # Choices Validation
            if lead_attribute.lead_type == LeadAttribute.ATTRIBUTE_CHOICES.choices:
                if not isinstance(lead_attribute.value, list):
                    raise ValidationError(f"Invalid choices '{lead_value}' for field {lead_attribute.name}.")

                if not len(lead_attribute.value):
                    raise ValidationError(f"Invalid choices value '{lead_value}' for field {lead_attribute.name}")

            if lead_attribute.lead_type == LeadAttribute.ATTRIBUTE_CHOICES.boolean:
                if not isinstance(lead_value, bool):
                    raise ValidationError(f"Invalid boolean '{lead_value}' for field {lead_attribute.name}.")


class LeadUserMap(TimeBaseModel):
    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    leads = models.ManyToManyField(Lead, blank=True)

    def __str__(self):
        return f"{self.member.account.name} {self.member.user.get_full_name} {self.member.role}"
