from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from rest_framework.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField
from leads.models_base import TimeBaseModel
from leads.models_manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True, blank=False)
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'

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
    BUSINESS_CATEGORY = Choices(
        ('it', 'IT'),
        ('other', 'Other'),
    )
    name = models.CharField(max_length=150)
    business_desc = models.JSONField(default=dict, null=True, blank=True)
    # users = models.ManyToManyField(User, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        business_desc = self.business_desc
        for category, desc in business_desc.items():
            if category not in self.BUSINESS_CATEGORY:
                raise ValidationError('Not a valid category')
            if not isinstance(desc, str):
                raise ValidationError('Invalid business description')


class Member(TimeBaseModel):
    USER_ROLE = Choices(
        ('admin', 'Is Admin'),
        ('staff', 'Is Staff'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=USER_ROLE, default=USER_ROLE.staff)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'account',)

    def __str__(self):
        return f"{self.user.email} account: {self.account.name}"


class UserOTP(TimeBaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email
