import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from trainers.tests.factories import TrainerProfileFactory, TrainingPlanFactory, TrainingApplicationFactory, UserFactory

@pytest.mark.django_db
def test_get_trainers():
    client = APIClient()
    TrainerProfileFactory.create_batch(5)

    response = client.get(reverse("trainer-list"))

    assert response.status_code == 200
    assert len(response.data) == 5

@pytest.mark.django_db
def test_get_trainer_detail():
    client = APIClient()
    trainer = TrainerProfileFactory()

    response = client.get(reverse("trainer-detail", args=[trainer.pk]))

    assert response.status_code == 200
    assert response.data["user"] is not None

@pytest.mark.django_db
def test_apply_training():
    client = APIClient()
    user = UserFactory()
    plan = TrainingPlanFactory()

    client.force_authenticate(user=user)
    response = client.post(reverse("apply", args=[plan.pk]), {"plan_id": str(plan.id)})

    assert response.status_code == 201
    assert response.data["status"] == "pending"

@pytest.mark.django_db
def test_trainer_approves_application():
    client = APIClient()
    trainer = UserFactory()
    plan = TrainingPlanFactory(trainer__user=trainer)
    application = TrainingApplicationFactory(plan=plan, trainer=plan.trainer)

    client.force_authenticate(user=trainer)
    response = client.patch(reverse("application-approve", args=[application.pk]), {"status": "approved"})

    assert response.status_code == 200
    assert response.data["status"] == "approved"
