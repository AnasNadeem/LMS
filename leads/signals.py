from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from leads.models_user import Member


@receiver(post_save, sender=Member)
def memberCreated(sender, instance, created, **kwargs):
    if created:
        subject = " Invitation "
        message = f"hi {instance.user.email} invitation message"
        email_from = settings.EMAIL_HOST_USER
        recipient_mail = [instance.user.email]
        send_mail(subject, message, email_from, recipient_mail, fail_silently=False)


# @receiver(post_save, sender=LeadAttribute)
# def add_field_to_existing_lead_data(sender, instance, created, **kwargs):
#     if not created:
#         return
