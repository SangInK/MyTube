from google_oauth.models import GoogleUser
from google_oauth.serializers import GoogleUserSerializer


class GoogleUserService:

    data = None  # 역직렬화가 완료된 데이터
    queryset = None  # Django queryset 객체

    def __init__(self, **kwargs):
        """
        kwargs의 값을 사용하여 저장된 google 유저 조회
        """

        if "access_token" in kwargs:
            self.set_google_user(access_token=kwargs["access_token"])

        elif "id" in kwargs:
            self.set_google_user(id=kwargs["id"])

        elif "user_id" in kwargs:
            self.set_google_user(user_id=kwargs["user_id"])

    def set_google_user(self, **kwargs):

        try:
            if "access_token" in kwargs:
                queryset = GoogleUser.objects.get(access_token=kwargs["access_token"])

            elif "id" in kwargs:
                queryset = GoogleUser.objects.get(id=kwargs["id"])

            elif "user_id" in kwargs:
                queryset = GoogleUser.objects.get(user_id=kwargs["user_id"])

            if queryset is not None:
                serializer = GoogleUserSerializer(queryset)
                data = serializer.data

        except Exception as e:
            data = None
            queryset = None

        self.data = data
        self.queryset = queryset

    def get_google_user(self):
        data = {
            "user_name": self.data["user_name"],
            "thumb_url": self.data["thumb_url"],
        }

        return data

    def is_valid(self):
        valid = False

        if self.data is not None:
            valid = True

        return valid

    def delete_user(self):
        self.queryset.delete()

    def update_user(self, **kwargs):
        serializer = GoogleUserSerializer(
            instance=self.queryset,
            data=kwargs,
            partial=True,
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        self.set_google_user(user_id=serializer.data["user_id"])

    def create_user(self, **kwargs):
        self.set_google_user(user_id=kwargs["user_id"])

        if self.is_valid():
            self.update_user(
                access_token=kwargs["access_token"],
                refresh_token=kwargs["refresh_token"],
            )
        else:
            serializer = GoogleUserSerializer(data=kwargs)

            if serializer.is_valid(raise_exception=True):
                serializer.save()

            self.data = serializer.data
            self.queryset = GoogleUser.objects.get(user_id=kwargs["user_id"])
