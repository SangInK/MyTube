from django.urls import path
from . import views

urlpatterns = [
    path("", views.google_oauth.as_view(), name="oatuh"),
    path("redirect/", views.google_redirect.as_view(), name="redirect"),
    path("check/", views.user_check.as_view(), name="check"),
    path("logout/", views.user_logout.as_view(), name="logout"),
    path("revoke/", views.user_revoke.as_view(), name="revoke"),
    path("ul/", views.user_list.as_view(), name="list"),
]
