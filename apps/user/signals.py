from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.user import services, models


@receiver(post_save, sender=models.User)
def create_account_validation_pin(instance: models.User,
                                  raw: bool,
                                  created: bool, **_):
    if raw is True:
        return

    if created is False:
        return

    instance.create_or_renew_validation_pin()


@receiver(post_save, sender=models.Avatar)
def adjust_user_main_avatar(instance: models.Avatar, raw: bool, **_):
    if raw is True:
        return

    if instance.main is False:
        return

    services.adjust_user_main_avatars(avatar=instance)
