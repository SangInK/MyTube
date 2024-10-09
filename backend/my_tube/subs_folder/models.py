from django.db import models

# verbose_name 입력을 위한 Django의 국제화 기능
from django.utils.translation import gettext as _

from google_oauth.models import GoogleUser


class Folder(models.Model):
    google_user = models.ForeignKey(GoogleUser, on_delete=models.CASCADE)
    folder_name = models.CharField(_("folder_name"), max_length=100)


class Subscription(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)

    subs_id = models.CharField(_("subs_id"), max_length=50)
    title = models.CharField(_("title"), max_length=500)
    description = models.CharField(_("description"), max_length=1000, blank=True)
    thumbnails = models.CharField(_("thumbnails"), max_length=200)
