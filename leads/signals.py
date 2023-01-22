from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from leads.models_user import Member
from leads.models_lead import LeadAttribute, Lead


@receiver(post_save, sender=Member)
def memberCreated(sender, instance, created, **kwargs):
    if created:
        subject = " Invitation "
        message = f"hi {instance.user.email} invitation message"
        email_from = settings.EMAIL_HOST_USER
        recipient_mail = [instance.user.email]
        send_mail(subject, message, email_from, recipient_mail, fail_silently=False)


@receiver(post_save, sender=LeadAttribute)
def add_field_to_existing_lead_data(sender, instance, created, **kwargs):
    if not created:
        return
    for lead in Lead.objects.filter(account=instance.account):
        lead.data[f"{instance.lead_type}"][f"{instance.slug}"] = None
        lead.save()

    # Lead.objects.filter(account=instance.account).update(**{f"data__{instance.lead_type}__{instance.slug}": None})
    # for lead in instance.account.lead_set.all():
    #     update_field = {f"data__{instance.lead_type}__{instance.slug}": None}
    #     lead.update(**update_field)


@receiver(post_delete, sender=LeadAttribute)
def delete_field_to_existing_lead_data(sender, instance, **kwargs):
    for lead in Lead.objects.filter(account=instance.account):
        del lead.data[f"{instance.lead_type}"][f"{instance.slug}"]
        lead.save()
