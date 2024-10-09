from django.urls import path
from . import views

urlpatterns = [
    path("<int:pk>/<str:nextToken>/", views.subscriptions.as_view()),
    # path("sub/", views.subscription.as_view()),
    # path("folder/<int:pk>", views.folder.as_view()),
    path("folders/", views.folders.as_view()),
]
