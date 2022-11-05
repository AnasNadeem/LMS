from leads.models_user import Member
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=Member)
def memberCreated(sender, instance, created, **kwargs):
    if created:
        print("send mail")
        print("email", instance.user.email)
        subject = " Invitation "
        message = f"hi {instance.user.email} invitation message"
        email_from = settings.EMAIL_HOST_USER
        recipient_mail = [instance.user.email]
        send_mail(subject, message, email_from, recipient_mail, fail_silently=False)
# post_save.connect(memberCreated, sender=Member)
