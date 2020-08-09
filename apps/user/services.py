from apps.user.models import Avatar


def adjust_user_main_avatars(avatar: Avatar):
    if avatar.main is False:
        print('false', avatar)
        return

    user = avatar.user
    other_avatars = user.avatars.exclude(pk=avatar.pk)

    pks = [a.pk for a in other_avatars]
    Avatar.objects.filter(pk__in=pks, user_id=user.pk).update(main=False)
