"""
Tasks to run in parallell
"""
from project.celery import app
from apps.user import services
from apps.user.models import Avatar


@app.task(bind=True,
          queue='avatar',
          options={'queue': 'avatar'},
          rate_limit='10/m',  # Max. 10 tasks per minute
          default_retry_delay=2 * 60,  # retry in 2m
          ignore_result=True)
def adjust_user_main_avatars(self, avatar_id: str):
    try:
        avatar = Avatar.objects.get(pk=avatar_id)
        services.adjust_user_main_avatars(avatar=avatar)
        return avatar
    except Exception as exc:
        raise self.retry(exc=exc)
