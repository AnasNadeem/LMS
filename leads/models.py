from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone

from autoslug import AutoSlugField
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
    phone_number = PhoneNumberField(null=False, blank=False, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
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
    users = models.ManyToManyField(User, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class LeadAttribute(TimeBaseModel):
    LEAD_CHOICES = (
        ('main', 'Main Lead'),
        ('track', 'Track Lead'),
        ('post', 'Post Lead'),
    )

    ATTRIBUTE_CHOICES = (
        ('string', 'String'),
        ('integer', 'Integer'),
        ('phone_number', 'Phone Number'),
        ('choices', 'Choices'),
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
    data = models.JSONField()


class LeadUserMap(TimeBaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    leads = models.ManyToManyField(Lead, blank=True)

    def __str__(self):
        return self.user.get_full_name
