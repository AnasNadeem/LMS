from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models
from django.utils import timezone

import phonenumbers
from autoslug import AutoSlugField
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField


class TimeBaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(max_length=150, unique=True, validators=[username_validator])
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField()
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    # def email_user(self, subject, message, from_email=None, **kwargs):
    #     """Send an email to this user."""
    #     send_mail(subject, message, from_email, [self.email], **kwargs)


class Account(TimeBaseModel):
    name = models.CharField(max_length=150)
    business_desc = models.JSONField(default=dict, null=True, blank=True)
    # users = models.ManyToManyField(User, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AccountUser(TimeBaseModel):
    USER_ROLE = Choices(
        ('admin', 'Is Admin'),
        ('staff', 'Is Staff'),
    )

    JOINED_STATUS = Choices(
        ('pending', 'Pending'),
        ('joined', 'Joined'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=USER_ROLE, default=USER_ROLE.staff)
    status = models.CharField(max_length=50, choices=JOINED_STATUS, default=JOINED_STATUS.pending)

    def __str__(self):
        return f"{self.user.email} for {self.account.name}"


class LeadAttribute(TimeBaseModel):
    LEAD_CHOICES = Choices(
        ('main', 'Main Lead'),
        ('track', 'Track Lead'),
        ('post', 'Post Lead'),
    )

    ATTRIBUTE_CHOICES = Choices(
        ('choices', 'Choices'),
        ('email', 'Email'),
        ('integer', 'Integer'),
        ('phone_number', 'Phone Number'),
        ('string', 'String'),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    lead_type = models.CharField(max_length=10, choices=LEAD_CHOICES)
    name = models.CharField(max_length=250)
    slug = AutoSlugField(populate_from='name', unique_with=('account', 'lead_type'))
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


class LeadUserMap(TimeBaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    leads = models.ManyToManyField(Lead, blank=True)

    def __str__(self):
        return self.user.get_full_name
