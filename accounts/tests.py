import pytest
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser, UserRole


# テスト用のクライアントを作成
@pytest.fixture
def api_client():
    return APIClient()


# テスト用のユーザー作成
@pytest.fixture
def create_user():
    def _create_user(username, name, password, role):
        user = CustomUser.objects.create_user(username=username, name=name, password=password)
        UserRole.objects.create(user=user, role=role)
        return user
    return _create_user


@pytest.mark.django_db
def test_register_member(api_client):
    """ ✅ 正常系: 一般会員の登録 """
    url = "/api/account/register/"
    data = {
        "username": "member_user",
        "name": "一般会員",
        "password": "password123",
        "role": "member"
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["username"] == "member_user"


@pytest.mark.django_db
def test_register_trainer(api_client):
    """ ✅ 正常系: トレーナーの登録 """
    url = "/api/account/register/"
    data = {
        "username": "trainer_user",
        "name": "トレーナー",
        "password": "password123",
        "role": "trainer"
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["username"] == "trainer_user"


@pytest.mark.django_db
def test_register_existing_user(api_client, create_user):
    """ ❌ 異常系: 既に存在するユーザー名で登録 """
    create_user("existing_user", "既存ユーザー", "password123", "member")
    url = "/api/account/register/"
    data = {
        "username": "existing_user",
        "name": "新規会員",
        "password": "password123",
        "role": "member"
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_success(api_client, create_user):
    """ ✅ 正常系: ログイン成功 """
    create_user("test_user", "テストユーザー", "password123", "member")
    url = "/api/account/login/"
    data = {
        "username": "test_user",
        "password": "password123"
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "ログイン成功"


@pytest.mark.django_db
def test_login_invalid_password(api_client, create_user):
    """ ❌ 異常系: パスワードが間違っている """
    create_user("test_user", "テストユーザー", "password123", "member")
    url = "/api/account/login/"
    data = {
        "username": "test_user",
        "password": "wrongpassword"
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_unknown_user(api_client):
    """ ❌ 異常系: 存在しないユーザー """
    url = "/api/account/login/"
    data = {
        "username": "unknown_user",
        "password": "password123"
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_logout(api_client, create_user):
    """ ✅ 正常系: ログアウト """
    user = create_user("test_user", "テストユーザー", "password123", "member")
    api_client.force_login(user)  # セッションログイン
    url = "/api/account/logout/"
    response = api_client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "ログアウトしました"


@pytest.mark.django_db
def test_me(api_client, create_user):
    """ ✅ 正常系: ログインユーザー情報取得 """
    user = create_user("test_user", "テストユーザー", "password123", "member")
    api_client.force_login(user)
    url = "/api/account/me/"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == "test_user"


@pytest.mark.django_db
def test_me_unauthenticated(api_client):
    """ ❌ 異常系: 未ログインユーザーの情報取得 """
    url = "/api/account/me/"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
