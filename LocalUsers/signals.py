from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import SwordphishUser


def create_swordphishuser(sender, instance, created, **kwargs):
    # pylint: disable=W0613
    if created and sender == User:
        instance.username = instance.email
        SwordphishUser.objects.create(user=instance)
        instance.save()


def save_swordphishuser(sender, instance, **kwargs):
    # pylint: disable=W0613
    if sender == User:
        instance.swordphishuser.save()


post_save.connect(create_swordphishuser, sender=User)
post_save.connect(save_swordphishuser, sender=User)
