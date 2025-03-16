import factory
from django.conf import settings
from trainers.models import TrainerProfile, TrainingPlan, TrainingApplication
import uuid

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    username = factory.Faker("user_name")
    name = factory.Faker("name")

class TrainerProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TrainerProfile

    user = factory.SubFactory(UserFactory)
    bio = factory.Faker("text")
    experience = factory.Faker("random_int", min=1, max=10)
    certifications = factory.Faker("sentence")

class TrainingPlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TrainingPlan

    trainer = factory.SubFactory(TrainerProfileFactory)
    title = factory.Faker("word")
    description = factory.Faker("text")
    price = factory.Faker("random_int", min=1000, max=10000)
    duration = factory.Faker("random_int", min=30, max=120)
    is_available = True
    plan_type = "one_time"

class TrainingApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TrainingApplication

    user = factory.SubFactory(UserFactory)
    trainer = factory.SubFactory(TrainerProfileFactory)
    plan = factory.SubFactory(TrainingPlanFactory)
    status = "pending"
