from enum import Enum

from django.conf import settings
from django.http import HttpResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from utils.auth.UserService import UserService
from utils.auth.GoogleUserService import GoogleUserService
from utils.auth.FlowService import FlowService
from utils.auth.CredentialsService import CredentialsService


from google_oauth.models import User
from google_oauth.serializers import UserSerializer


# 회원여부, 로그인 여부 확인을 위한 enmu
class LOGIN_STATE(Enum):
    nosign = 0
    login = 1
    logout = 2


class user_check(APIView):
    def get(self, request):
        response = Response()
        response_data = {
            "loginState": LOGIN_STATE.nosign.value,
            "user": None,
        }

        # COOKIE에 user_token이 있을 경우 해당 토큰에 해당하는 유저 조회 후 처리
        if "user_token" in request.COOKIES:
            user = UserService(user_token=request.COOKIES["user_token"])

            if user.is_valid():
                if user.check_expires():
                    # user의 login_state == 로그인 상태 여부 가 false == 로그아웃일 경우
                    if not user.data["user_state"]:
                        response_data["loginState"] = LOGIN_STATE.logout.value

                    else:
                        google_user = GoogleUserService(id=user.data["google_user"])

                        if "credentials" in request.session:
                            credentials = CredentialsService(
                                request.session["credentials"]
                            )

                            request.session["credentials"] = (
                                credentials.credentials_to_dict()
                            )
                        else:
                            flow = FlowService()

                            credentials = CredentialsService(
                                {
                                    "token": google_user.data["access_token"],
                                    "refresh_token": google_user.data["refresh_token"],
                                    "client_id": flow.config["web"]["client_id"],
                                    "client_secret": flow.config["web"][
                                        "client_secret"
                                    ],
                                    "token_uri": flow.config["web"]["token_uri"],
                                    "scopes": flow.SCOPES,
                                }
                            )

                            request.session["credentials"] = (
                                credentials.credentials_to_dict()
                            )

                        response_data["loginState"] = LOGIN_STATE.login.value
                        response_data["user"] = google_user.get_google_user()

                else:
                    user.delete_user()
                    response = _delete_cookie(response)

            else:
                response = _delete_cookie(response)

        response.data = response_data
        response.status_code = status.HTTP_200_OK

        return response


class google_oauth(APIView):
    def post(self, request):
        response = Response()

        try:
            if "user_token" in request.COOKIES:
                # TODO 이미 인증이 완료된 사용자라면 DB에서 해당 사용자의 정보를 조회 후 반환
                pass
            else:
                # Google Flow 객체 생성
                flow = FlowService()
                flow.set_flow({"client_config": flow.config, "scopes": flow.SCOPES})

                # Google Flow 객체를 사용하여 인증 화면 url 생성
                authorization_url, state = flow.get_authorization_url()

                request.session["google_oauth2_state"] = state

                return Response({"authorization_url": authorization_url})

        except Exception as e:
            response.data = None
            response.status_code = status.HTTP_400_BAD_REQUEST

            return response


class google_redirect(APIView):
    def _validate_date(self, request):
        """
        Google 인증 창을 통해 전달받은 내용의 유효성 검증
        """

        data = request.GET

        code = data.get("code")
        error = data.get("error")
        state = data.get("state")

        if error is not None:
            raise Exception(error)

        if code is None or state is None:
            raise Exception("Code and state are required.")

        session_state = request.session["google_oauth2_state"]

        if session_state is None:
            raise Exception("CSRF check failed.")

        del request.session["google_oauth2_state"]

        if state != session_state:
            raise Exception("CSRF check failed.")

        return code, state

    def get(self, request):
        response = HttpResponse()
        is_ok = False

        try:
            code, state = self._validate_date(request)

            # Google Flow 객체 생성
            flow = FlowService()
            flow.set_flow(
                {"client_config": flow.config, "scopes": flow.SCOPES, "state": state}
            )

            # Google Flow 객체를 사용하여 Token 생성 및 인증서 조회
            flow.set_token(code=code)
            flow_credentials = flow.get_credentials()

            credentials = CredentialsService(flow_credentials)
            credentials.set_google_user(credentials.credentials.token)

            youtube = credentials.get_youtube()

            channels = (
                youtube.channels()
                .list(part="snippet,contentDetails,statistics", mine=True)
                .execute()
            )

            google_user = GoogleUserService()
            google_user.create_user(
                user_id=channels["items"][0]["id"],
                user_name=channels["items"][0]["snippet"]["title"],
                thumb_url=channels["items"][0]["snippet"]["thumbnails"]["default"][
                    "url"
                ],
                access_token=credentials.credentials.token,
                refresh_token=credentials.credentials.refresh_token,
            )

            user = UserService(google_user_id=google_user.data["id"])
            user.create_user(google_user_id=google_user.data["id"])

            response.status_code = status.HTTP_200_OK

            request.session["credentials"] = credentials.credentials_to_dict()

            response.set_cookie(
                "user_token",
                user.data["user_token"],
                max_age=259200,
                samesite="none",
                secure=True,
            )

        except Exception as e:
            print(f"error: {e.args[0]}")

        # response.content = f"""
        # <script>
        #     location.href = '{settings.CLIENT_ORIGIN}?isOk={is_ok}'
        # </script>
        # """

        # 개발을 위해 임시로 만들어둔 엔드포인트 처리
        response.content = f"""
        <script>
            location.href = 'https://liberal-chigger-blindly.ngrok-free.app/auth/ul'
        </script>
        """

        return response


class user_logout(APIView):
    def post(self, request):
        user = UserService(user_token=request.COOKIES["user_token"])
        user.update_user(user_state=False)

        return Response({"user": None}, status=status.HTTP_200_OK)


class user_revoke(APIView):
    def post(self, request):
        credentials = CredentialsService(request.session["credentials"])
        revoke = credentials.rovoke_credentials()

        if getattr(revoke, "status_code") == status.HTTP_200_OK:
            del request.session["credentials"]
            credentials.google_user.delete_user()

            response = Response()
            response = _delete_cookie(response)

            response.status_code = status.HTTP_200_OK

            return response
        else:
            return Response(revoke.text, status=status.HTTP_400_BAD_REQUEST)


def _delete_cookie(response):
    response.delete_cookie("user_token")
    response.set_cookie("user_token", value="", expires=0, secure=True, samesite="none")

    response.data = {"user": None}

    return response


class user_list(APIView):
    def get(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)

        return Response(serializer.data, status.HTTP_200_OK)
