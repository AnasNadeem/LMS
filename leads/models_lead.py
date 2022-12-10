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
    seq_no = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.lead_type}"

    LEADATTR_WITH_VALUE_VALIDATION = {
        'boolean': 'validate_bool',
        'choices': 'validate_choices',
        'email': 'validate_email',
        'integer': 'validate_integer',
        'phone_number': 'validate_phone_number',
        'string': 'validate_string',
    }

    def validate_bool(self, lead_value):
        if not isinstance(lead_value, bool):
            raise ValidationError({self.slug: f"Invalid boolean: '{lead_value}' for field: '{self.name}'"})

    def validate_choices(self, lead_value):
        if not isinstance(self.value, list):
            raise ValidationError({self.slug: f"Invalid choices '{lead_value}' for field '{self.name}'"})

        if not len(self.value):
            raise ValidationError({self.slug: f"Invalid choices value: '{lead_value}' for field: '{self.name}'"})

    def validate_email(self, lead_value):
        try:
            validate_email(lead_value)
        except Exception as e:
            e.message = f"Invalid email: '{lead_value}' for field: {self.name}."
            raise ValidationError({self.slug: e.message})

    def validate_integer(self, lead_value):
        if not isinstance(lead_value, int):
            raise ValidationError({self.slug: f"Invalid integer: '{lead_value}' for field: '{self.name}'"})

    def validate_phone_number(self, lead_value):
        phone_num = phonenumbers.parse(lead_value)
        if not phonenumbers.is_valid_number(phone_num):
            raise ValidationError({self.slug: f"Invalid phone number: '{lead_value}' for field: '{self.name}'"})

    def validate_string(self, lead_value):
        if not isinstance(lead_value, str):
            raise ValidationError({self.slug: f"Invalid string: '{lead_value}' for field: '{self.name}'"})


class Lead(TimeBaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    data = models.JSONField(default=dict(main={}, track={}, post={}), null=True, blank=True)

    def save(self, **kwargs):
        self.clean()
        return super().save(**kwargs)

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
                raise ValidationError({"lead_attribute": f"Invalid lead attribute: '{lead_attr}' for lead type: '{lead_type}'"})
            validate_func = getattr(lead_attribute, LeadAttribute.LEADATTR_WITH_VALUE_VALIDATION.get(lead_attribute.attribute_type))
            validate_func(lead_value)


class LeadUserMap(TimeBaseModel):
    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    leads = models.ManyToManyField(Lead, blank=True)

    def __str__(self):
        return f"{self.member.account.name} {self.member.user.get_full_name} {self.member.role}"
