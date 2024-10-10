from django.db.models import Q

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from utils.auth.CredentialsService import CredentialsService

from .models import Folder, Subscription
from .serializers import FolderSerializer, SubscriptionSerializer

# google 구독 채널 조회 시 한 번에 조회할 채널의 수
MAX_RESULT = 25


def _get_credentials(request):
    """
    youtube 구독 채널을 조회하기 위해 google oauth2 인증 정보 조회하여 반환
    """
    credentials = CredentialsService(request.session["credentials"])
    request.session["credentials"] = credentials.credentials_to_dict()

    return credentials


def _get_subscriptions(request, nextToken=""):
    """
    구독중인 youtube 채널 조회.
    google api를 통해 가져온 youtube 채널과 폴더에 저장된 채널 정보 = Subscription의 데이터를 합쳐서 표시

    Args:
        nextToken (string): api를 통해 youtube 구독 채널 조회 시 한 번에 모든 채널을 조회할 수 없으므로
        pagination 처리. 해당 페이징 처리를 위해 다음 페이지의 token 값이 있을 경우 다음 페이지를 조회
    """

    credentials = _get_credentials(request)

    youtube = credentials.get_youtube()

    subscriptions = (
        youtube.subscriptions()
        .list(part="id,snippet", maxResults=MAX_RESULT, mine=True, pageToken=nextToken)
        .execute()
    )

    subs = {"pageInfo": subscriptions.get("pageInfo", {})}
    subs["pageInfo"]["nextPageToken"] = subscriptions.get("nextPageToken", "")

    my_subs = Subscription.objects.filter(
        folder__in=Folder.objects.filter(
            google_user_id=credentials.google_user.data["id"]
        ).values_list("id", flat=True)
    )
    serializer = SubscriptionSerializer(my_subs, many=True)

    subs["items"] = serializer.data if nextToken == "" else []

    for item in [
        item["snippet"]
        for item in subscriptions["items"]
        if item["snippet"]["resourceId"]["channelId"]
        not in [item["subs_id"] for item in serializer.data]
    ]:
        subs_temp = {
            "subs_id": item["resourceId"]["channelId"],
            "title": item["title"],
            "description": item["description"],
            "thumbnails": item["thumbnails"]["default"]["url"],
        }

        subs["items"].append(subs_temp)

    return subs


class folder(APIView):
    def delete(self, request, pk):
        try:
            folder = Folder.objects.get(id=pk)
            folder.delete()

            return Response({"isOk": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"isOk": False}, status=status.HTTP_400_BAD_REQUEST)


class folders(APIView):
    def get(self, request):
        if "credentials" in request.session:
            credentials = _get_credentials(request)
            credentials.set_google_user(credentials.credentials.token)

            folder = Folder.objects.filter(
                google_user=credentials.google_user.data["id"]
            )
            serializer = FolderSerializer(folder, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        if "credentials" in request.session:
            credentials = _get_credentials(request)
            credentials.set_google_user(credentials.credentials.token)

            request.data["google_user"] = credentials.google_user.data["id"]
            serializer = FolderSerializer(data=request.data)

            if serializer.is_valid(raise_exception=True):
                serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class subscriptions(APIView):
    def get(self, request, pk, nextToken):
        subs = _get_subscriptions(
            request, "" if nextToken == "firstSearch" else nextToken
        )

        return Response(subs, status=status.HTTP_200_OK)

    def post(self, request, pk, nextToken):
        # 이미 입력된 구독채널이 있으면 삭제
        # 채널의 폴더 간 이동 기능 없으므로 주석처리
        # data = [data for data in request.data if "folder" in data]

        # if len(data) > 0:
        #     filter = Q()

        #     for item in data:
        #         filter |= Q(subs_id=item["subs_id"])

        #     subs = Subscription.objects.filter(filter)
        #     subs.delete()

        folder = Folder.objects.get(id=pk)
        folder_serializer = FolderSerializer(folder)

        data = request.data
        for item in data:
            item["folder"] = folder_serializer.data

        serializer = SubscriptionSerializer(data=data, many=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(
            {"isOk": True, "subs": serializer.data}, status=status.HTTP_200_OK
        )

    def delete(self, request, pk, nextToken):
        try:
            filter = Q(folder=pk)
            filter_channel_id = Q()

            for subs in request.data:
                filter_channel_id |= Q(subs_id=subs["subs_id"])

            filter &= filter_channel_id

            subs = Subscription.objects.filter(filter)
            subs.delete()

            return Response({"isOk": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
