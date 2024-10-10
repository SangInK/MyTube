# MyTube
 1. Google 인증을 사용하여 인증 후 해당 유저의 구독중인 youtube 채널 목록 표시.
 2. 구독중인 채널을 폴더 별로 관리할 수 있도록 폴더 추가 및 삭제, 구독 채널 이동 기능 구현.



# API Endpoints
## 1. Google OAuth API
### 1.1. Google OAuth

- **URL**: `/auth/`
- **Method**: `POST`
- **Description**: Google 인증 화면 URL을 생성하여 반환합니다. 사용자가 인증을 완료하면 Google의 리디렉션 URL로 이동합니다.
- **Response**:
    - **Status Code**: `200 OK`
    - **Response Body**:
      ```json
      {
          "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
      }
      ```

---

### 1.2. Google Redirect

- **URL**: `/auth/redirect/`
- **Method**: `GET`
- **Description**: Google 인증 후 리디렉션된 URL에서 호출됩니다. 인증 코드를 사용하여 사용자를 인증합니다.

- **Query Parameters**:
    - `code`: Google에서 제공하는 인증 코드
    - `state`: CSRF 보호를 위한 상태 값

- **Response**:
    - **Status Code**: `200 OK`

- **Redirects**: 성공적으로 인증된 후 사용자에게 다른 URL로 리디렉션됩니다.

---

### 1.3. Check User Login State

- **URL**: `/auth/check/`
- **Method**: `GET`
- **Description**: 현재 사용자의 로그인 상태를 확인합니다.

- **Response**:
    - **Status Code**: `200 OK`
    - **Response Body**:
      ```json
      {
          "loginState": 0,  // 0: not signed in, 1: logged in, 2: logged out
          "user": {          // User object if logged in
              // User data here if logged in
          }
      }
      ```

---

### 1.4. User Logout

- **URL**: `/auth/logout/`
- **Method**: `POST`
- **Description**: 현재 사용자를 로그아웃합니다.

- **Response**:
    - **Status Code**: `200 OK`
    - **Response Body**:
      ```json
      {
          "user": null
      }
      ```

---

### 1.5. Revoke User Credentials

- **URL**: `/auth/revoke/`
- **Method**: `POST`
- **Description**: Google API에서 사용자의 인증 정보를 취소합니다.

- **Response**:
    - **Status Code**: `200 OK` or `400 Bad Request`
---

### 1.6. User List (개발중 입력된 유저 리스트를 확인하기 위한 임시 엔드포인트)

- **URL**: `/auth/ul/`
- **Method**: `GET`
- **Description**: 모든 사용자 정보를 반환합니다.

- **Response**:
    - **Status Code**: `200 OK`
    - **Response Body**:
      ```json
      [
          {
              "id": 1,
              "username": "string",
              "email": "string"
          },
          // More user objects
      ]
      ```

---

## 2. Subscription and Folder API

### 2.1. Get Folders

- **URL**: `/folders/`
- **Method**: `GET`
- **Description**: Google 인증된 사용자가 생성한 폴더 목록을 반환합니다.
- **Response**:
    - **Status Code**: `200 OK`
    - **Response Body**:
      ```json
      [
          {
              "id": 1,
              "name": "string",
              "google_user": "string"
          },
          // More folder objects
      ]
      ```

---

### 2.2. Create Folder

- **URL**: `/folders/`
- **Method**: `POST`
- **Description**: 새로운 폴더를 생성합니다.
- **Request Body**:
    - **google_user**: Google 사용자 ID
    - **name**: 폴더 이름
- **Response**:
    - **Status Code**: `201 Created`
    - **Response Body**:
      ```json
      {
          "id": 1,
          "name": "string",
          "google_user": "string"
      }
      ```

---

### 2.3. Delete Folder

- **URL**: `/folder/<int:pk>/`
- **Method**: `DELETE`
- **Description**: 지정된 폴더를 삭제합니다.
- **Response**:
    - **Status Code**: `200 OK`
    - **Response Body**:
      ```json
      {
          "isOk": true
      }
      ```

---

### 2.4. Get Subscriptions

- **URL**: `/<int:pk>/<str:nextToken>/`
- **Method**: `GET`
- **Description**: 유저의 구독중인 YouTube 채널을 조회합니다. `nextToken` 값이 있을 경우, 다음 페이지의 채널을 조회합니다.
- **Response**:
    - **Status Code**: `200 OK`
    - **Response Body**:
      ```json
      {
          "pageInfo": {
              "totalResults": 100,
              "nextPageToken": "string"
          },
          "items": [
              {
                  "subs_id": "channel_id",
                  "title": "string",
                  "description": "string",
                  "thumbnails": "thumbnail_url"
              },
              // More subscription objects
          ]
      }
      ```

---

### 2.5. Add Subscriptions to Folder

- **URL**: `/<int:pk>/<str:nextToken>/`
- **Method**: `POST`
- **Description**: 폴더에 구독 채널을 추가합니다.
- **Request Body**:
    - **folder**: 폴더 정보
    - **items**: 구독 채널 정보
- **Response**:
    - **Status Code**: `200 OK`
    - **Response Body**:
      ```json
      {
          "isOk": true,
          "subs": [
              {
                  "subs_id": "channel_id",
                  "title": "string",
                  "description": "string",
                  "thumbnails": "thumbnail_url"
              },
              // More subscription objects
          ]
      }
      ```

---

### 2.6. Delete Subscriptions from Folder

- **URL**: `/<int:pk>/<str:nextToken>/`
- **Method**: `DELETE`
- **Description**: 폴더에서 지정된 구독 채널을 삭제합니다.
- **Response**:
    - **Status Code**: `200 OK`
    - **Response Body**:
      ```json
      {
          "isOk": true
      }
      ```


## Error Responses

- **400 Bad Request**: 잘못된 요청 데이터
- **403 Forbidden**: 권한이 없음
- **404 Not Found**: 요청한 리소스를 찾을 수 없음
- **500 Internal Server Error**: 서버 오류
