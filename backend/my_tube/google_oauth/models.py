from django.db import models

# verbose_name 입력을 위한 Django의 국제화 기능
from django.utils.translation import gettext as _


class GoogleUser(models.Model):
    user_id = models.CharField(_("user_id"), max_length=50)
    user_name = models.CharField(_("user_name"), max_length=50)
    thumb_url = models.CharField(_("thumb_url"), max_length=200)

    access_token = models.CharField(_("token"), max_length=300)
    refresh_token = models.CharField(_("refresh_token"), max_length=300)


class User(models.Model):
    google_user = models.OneToOneField(GoogleUser, on_delete=models.CASCADE)

    user_token = models.UUIDField(_("user_token"))
    user_state = models.BooleanField()
    expires_at = models.DateTimeField()
