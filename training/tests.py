import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from training.models import TrainingSession, Workout, WorkoutSet
from django.utils.timezone import now

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
def create_training_session():
    """ トレーニング記録を作成するヘルパー関数 """
    def _create_training_session(user, date):
        return TrainingSession.objects.create(user=user, date=date)
    return _create_training_session


@pytest.fixture
def create_workout():
    """ ワークアウトを作成するヘルパー関数 """
    def _create_workout(session, menu, type, unit):
        return Workout.objects.create(session=session, menu=menu, type=type, unit=unit)
    return _create_workout


@pytest.fixture
def create_workout_set():
    """ セットを作成するヘルパー関数 """
    def _create_workout_set(workout, weight, reps, memo):
        return WorkoutSet.objects.create(workout=workout, weight=weight, reps=reps, memo=memo)
    return _create_workout_set


# ✅ 正常系テスト
@pytest.mark.django_db
def test_create_training_session(api_client, create_user):
    """ ✅ トレーニング記録を新規作成 """
    user = create_user("test_user", "Test User", "password123")
    api_client.force_login(user)

    url = "/api/training/"
    data = {
        "date": "2025-02-26",
        "workouts": [
            {
                "menu": "ベンチプレス",
                "type": "weight",
                "unit": "kg",
                "memo": "フォームを意識",
                "sets": [
                    {"weight": 80, "reps": 10, "memo": "フォームを意識"},
                    {"weight": 75, "reps": 12, "memo": "最後の2回がきつかった"}
                ]
            }
        ]
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["date"] == "2025-02-26"
    assert TrainingSession.objects.count() == 1
    assert Workout.objects.count() == 1
    assert WorkoutSet.objects.count() == 2


@pytest.mark.django_db
def test_get_training_sessions(api_client, create_user, create_training_session, create_workout, create_workout_set):
    """ ✅ トレーニング記録の取得（一覧）"""
    user = create_user("test_user", "Test User", "password123")
    api_client.force_login(user)

    session = create_training_session(user, "2025-02-26")
    workout = create_workout(session, "ベンチプレス", "weight", "kg")
    create_workout_set(workout, 80, 10, "フォームを意識")
    create_workout_set(workout, 75, 12, "最後の2回がきつかった")

    url = "/api/training/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["date"] == "2025-02-26"
    assert response.data[0]["workouts"][0]["menu"] == "ベンチプレス"


@pytest.mark.django_db
def test_delete_training_session(api_client, create_user, create_training_session):
    """ ✅ トレーニング記録の削除 """
    user = create_user("test_user", "Test User", "password123")
    api_client.force_login(user)

    session = create_training_session(user, "2025-02-26")

    url = f"/api/training/{session.id}/"
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert TrainingSession.objects.count() == 0


# ❌ 異常系テスト
@pytest.mark.django_db
def test_create_training_session_unauthorized(api_client):
    """ ❌ 未ログイン状態でのトレーニング記録作成（エラー）"""
    url = "/api/training/"
    data = {
        "date": "2025-02-26",
        "workouts": [
            {
                "menu": "ベンチプレス",
                "type": "weight",
                "unit": "kg",
                "memo": "フォームを意識",
                "sets": [{"weight": 80, "reps": 10, "memo": "フォームを意識"}]
            }
        ]
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_other_user_training_session(api_client, create_user, create_training_session):
    """ ❌ 他のユーザーのトレーニング記録を取得（エラー）"""
    user1 = create_user("user1", "User One", "password123")
    user2 = create_user("user2", "User Two", "password123")  # 別のユーザー
    api_client.force_login(user2)

    session = create_training_session(user1, "2025-02-26")  # user1のデータ

    url = f"/api/training/{session.id}/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_other_user_training_session(api_client, create_user, create_training_session):
    """ ❌ 他のユーザーのトレーニング記録を削除（エラー）"""
    user1 = create_user("user1", "User One", "password123")
    user2 = create_user("user2", "User Two", "password123")  # 別のユーザー
    api_client.force_login(user2)

    session = create_training_session(user1, "2025-02-26")  # user1のデータ

    url = f"/api/training/{session.id}/"
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert TrainingSession.objects.filter(id=session.id).exists()  # データは削除されていない
