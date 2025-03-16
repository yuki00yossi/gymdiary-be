import pytest
from trainers.models import TrainerProfile, TrainingPlan, TrainingApplication
from trainers.tests.factories import TrainerProfileFactory, TrainingPlanFactory, TrainingApplicationFactory

@pytest.mark.django_db
def test_create_trainer():
    trainer = TrainerProfileFactory()
    assert trainer.user is not None
    assert isinstance(trainer, TrainerProfile)

@pytest.mark.django_db
def test_create_training_plan():
    plan = TrainingPlanFactory()
    assert plan.trainer is not None
    assert plan.is_available == True

@pytest.mark.django_db
def test_create_training_application():
    application = TrainingApplicationFactory()
    assert application.status == "pending"
    assert application.user is not None
