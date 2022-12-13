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

    OPS = [
        # String
        'contains',  # Contains the phrase
        'icontains',  # Same as contains, but case-insensitive
        'endswith',  # Ends with
        'iendswith',  # Same as endswidth, but case-insensitive
        'exact',  # An exact match
        'iexact',  # Same as exact, but case-insensitive
        'startswith',  # Starts with
        'istartswith',  # Same as startswith, but case-insensitive
        # List
        'in',  # Matches one of the values
        'isnull',  # Matches NULL values
        # Date, DateTime
        'date',  # Matches a date
        'day',  # Matches a date (day of month, 1-31) (for dates)
        'gt',  # Greater than
        'gte',  # Greater than, or equal to
        'hour',  # Matches an hour (for datetimes)
        'lt',  # Less than
        'lte',  # Less than, or equal to
        'minute',  # Matches a minute (for datetimes)
        'month',  # Matches a month (for dates)
        'second',  # Matches a second (for datetimes)
        'quarter',  # Matches a quarter of the year (1-4) (for dates)
        'time',  # Matches a time (for datetimes)
        'week',  # Matches a week number (1-53) (for dates)
        'week_day',  # Matches a day of week (1-7) 1 is sunday
        'iso_week_day',  # Matches a ISO 8601 day of week (1-7) 1 is monday
        'year',  # Matches a year (for dates)
        'iso_year',  # Matches an ISO 8601 year (for dates)
        # Different
        'range',  # Match between
        'regex',  # Matches a regular expression
        'iregex',  # Same as regex, but case-insensitive
    ]

    ATTR_OP_COMBO = {
        'boolean': [
            'contains',
            'icontains',
            'exact',
            'iexact',
        ],
        'choices': [
            'contains',
            'icontains',
            'endswith',
            'iendswith',
            'exact',
            'iexact',
            'startswith',
            'istartswith',
            'in',
        ],
        'email': [
            'contains',
            'icontains',
            'endswith',
            'iendswith',
            'exact',
            'iexact',
            'startswith',
            'istartswith',
        ],
        'integer': [
            'gt',
            'gte',
            'lt',
            'lte',
            'range',
        ],
        'phone_number': [],
        'string': [
            'contains',
            'icontains',
            'endswith',
            'iendswith',
            'exact',
            'iexact',
            'startswith',
            'istartswith',
        ],
    }

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

    def validate_op(self, op):
        if not op:
            raise ValidationError({"op": "Empty Op"})

        if op not in self.OPS:
            raise ValidationError({"op": f"Invalid op: '{op}'"})

        if op not in self.ATTR_OP_COMBO[self.attribute_type]:
            raise ValidationError({"op": f"Invalid op combo: Attribute: '{self.attribute_type}' cannot be used with Op: '{op}'"})


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
            self.clean_leadattr_data(lead_data, lead_attributes)

    def clean_leadattr_data(self, lead_data, lead_attributes):
        for lead_attr, lead_value in lead_data.items():
            lead_attribute = lead_attributes.filter(slug=lead_attr).first()
            if not lead_attribute:
                raise ValidationError({"lead_attribute": f"Invalid lead attribute: '{lead_attr}''"})
            # Check if the lead_value contains op
            op, lead_value = (lead_value[0], lead_value[1]) if (isinstance(lead_value, list)) else (None, lead_value)
            if op:
                lead_attribute.validate_op(op)
            validate_func = getattr(lead_attribute, lead_attribute.LEADATTR_WITH_VALUE_VALIDATION.get(lead_attribute.attribute_type))
            validate_func(lead_value)


class LeadUserMap(TimeBaseModel):
    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    leads = models.ManyToManyField(Lead, blank=True)

    def __str__(self):
        return f"{self.member.account.name} {self.member.user.get_full_name} {self.member.role}"
