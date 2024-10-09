from uuid import uuid4
from datetime import datetime, timedelta

from google_oauth.models import User
from google_oauth.serializers import UserSerializer


class UserService:
    def __init__(self, **kwargs):
        if "user_token" in kwargs:
            self.set_user(user_token=kwargs["user_token"])
        elif "google_user_id" in kwargs:
            self.set_user(google_user_id=kwargs["google_user_id"])

    def set_user(self, **kwargs):
        data = None
        queryset = None

        try:
            if "user_token" in kwargs:
                queryset = User.objects.get(user_token=kwargs["user_token"])
            elif "google_user_id" in kwargs:
                queryset = User.objects.get(google_user_id=kwargs["google_user_id"])

            if queryset is not None:
                serializer = UserSerializer(queryset)
                data = serializer.data

        except Exception as e:
            data = None
            queryset = None

        self.data = data
        self.queryset = queryset

    def is_valid(self):
        valid = False

        if self.data is not None:
            valid = True

        return valid

    def check_expires(self):
        valid = False

        if (
            datetime.strptime(
                self.data["expires_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
            ).replace(tzinfo=None)
            >= datetime.now()
        ):
            valid = True

        return valid

    def delete_user(self):
        self.queryset.delete()

    def update_user(self, **kwargs):
        serializer = UserSerializer(instance=self.queryset, data=kwargs, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        self.set_user(google_user_id=serializer.data["google_user"])

    def create_user(self, google_user_id):

        if self.is_valid():
            self.update_user(
                user_token=str(uuid4()),
                user_state=True,
                expires_at=datetime.now() + timedelta(days=1),
            )
        else:
            user = {
                "google_user": google_user_id,
                "user_token": str(uuid4()),
                "user_state": True,
                "expires_at": datetime.now() + timedelta(days=1),
            }

            serializer = UserSerializer(data=user)

            if serializer.is_valid(raise_exception=True):
                serializer.save()

            self.data = serializer.data
            self.queryset = User.objects.get(google_user=google_user_id)
