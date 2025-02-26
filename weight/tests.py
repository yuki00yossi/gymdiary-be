import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from weight.models import WeightRecord

User = get_user_model()

@pytest.fixture
def api_client():
    """ テスト用のAPIクライアント """
    return APIClient()

@pytest.fixture
def create_user():
    """ テスト用のユーザー作成 """
    def _create_user(username, name, password):
        return User.objects.create_user(username=username, name=name, password=password)
    return _create_user

@pytest.fixture
def create_weight_record():
    """ 体重記録を作成するヘルパー関数 """
    def _create_weight_record(user, weight, fat, record_date):
        return WeightRecord.objects.create(
            user=user, weight=weight, fat=fat, record_date=record_date)
    return _create_weight_record

# ✅ 正常系テスト
@pytest.mark.django_db
def test_create_weight_record(api_client, create_user):
    """ ✅ 体重記録を新規作成 """
    user = create_user("test_user", "test name", "password123")
    api_client.force_login(user)

    url = "/api/weight/"
    data = {"weight": 70.5, "fat": 20.5, "record_date": "2025-01-01"}

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert float(response.data["weight"]) == 70.5
    assert WeightRecord.objects.count() == 1

@pytest.mark.django_db
def test_get_weight_records(api_client, create_user, create_weight_record):
    """ ✅ 体重記録の取得（一覧）"""
    user = create_user("test_user", "testuser", "password123")
    api_client.force_login(user)

    create_weight_record(user, 70.5, 20.3, now())
    create_weight_record(user, 71.0, 20.5, now())

    url = "/api/weight/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert float(response.data[0]["weight"]) == 71.0  # 最新の記録が先に来る

# ❌ 異常系テスト
@pytest.mark.django_db
def test_create_weight_record_unauthorized(api_client):
    """ ❌ 未ログイン状態での体重記録作成（エラー）"""
    url = "/api/weight/"
    data = {"weight": 70.5, "fat": 20.5, "record_date": "2025-01-01"}

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_get_weight_records_unauthorized(api_client):
    """ ❌ 未ログイン状態での体重記録取得（エラー）"""
    url = "/api/weight/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
