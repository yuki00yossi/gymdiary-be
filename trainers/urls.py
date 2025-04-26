from django.urls import path
from . import views

urlpatterns = [
    path('trainer-profile/', views.TrainerProfileView.as_view(), name='trainer-profile'),
    path("interview/", views.InterviewScheduleView.as_view(), name="trainer.interview"),
    # path("<uuid:pk>/", TrainerDetailView.as_view(), name="trainer-detail"),
    # path("plans/<uuid:id>/", UpdateTrainingPlanView.as_view(), name="plan-update"),

    # # 申し込み関連
    # path("<uuid:id>/apply/", TrainingApplicationCreateView.as_view(), name="apply"),
    # path("applications/<uuid:id>/approve/", TrainingApplicationApproveView.as_view(), name="application-approve"),

    # # 支払い関連
    # path("applications/<uuid:id>/pay/", CreateCheckoutSessionView.as_view(), name="pay"),
    # path("stripe/webhook/", stripe_webhook, name="stripe-webhook"),
]
