import json
from django.http import JsonResponse
from rest_framework import generics, permissions, status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import TrainerProfile, TrainingPlan, TrainingApplication
from .serializers import TrainerProfileSerializer, TrainingPlanSerializer
import stripe
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY


# トレーナー一覧
class TrainerListView(generics.ListAPIView):
    queryset = TrainerProfile.objects.all()
    serializer_class = TrainerProfileSerializer
    permission_classes = [permissions.AllowAny]


# トレーナー詳細
class TrainerDetailView(generics.RetrieveAPIView):
    queryset = TrainerProfile.objects.all()
    serializer_class = TrainerProfileSerializer
    permission_classes = [permissions.AllowAny]


# 受付状態の変更
class UpdateTrainingPlanView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, id):
        plan = get_object_or_404(TrainingPlan, id=id, trainer__user=request.user)
        plan.is_available = request.data.get("is_available", plan.is_available)
        plan.save()
        return Response({"id": plan.id, "is_available": plan.is_available})


# 仮予約API
class TrainingApplicationCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        plan = get_object_or_404(TrainingPlan, id=request.data.get("plan_id"))
        if not plan.is_available:
            return Response({"error": "このプランは受付停止中です"}, status=400)

        application = TrainingApplication.objects.create(
            user=request.user,
            trainer=plan.trainer,
            plan=plan,
            status="pending",
            expires_at=timezone.now() + timezone.timedelta(days=2)
        )

        return Response({"id": application.id, "status": "pending"}, status=status.HTTP_201_CREATED)


# 予約確定API（トレーナーが決定する）
class TrainingApplicationApproveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, id):
        application = get_object_or_404(TrainingApplication, id=id, trainer__user=request.user)

        if application.status != "pending":
            return Response({"error": "この申し込みはすでに処理済みです"}, status=400)

        application.status = "approved"
        application.expires_at = timezone.now() + timezone.timedelta(days=2)
        application.save()

        return Response({"id": application.id, "status": "approved"})


# チックアウトURLを作成する
class CreateCheckoutSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        application = get_object_or_404(TrainingApplication, id=id, user=request.user, status="approved")

        if application.plan.plan_type == "one_time":
            mode = "payment"
            line_item = {
                "price_data": {  # 動的に価格を設定
                    "currency": "jpy",
                    "product_data": {
                        "name": application.plan.title,
                    },
                    "unit_amount": application.plan.price * 100,
                },
                "quantity": 1,
            }
        else:
            mode = "subscription"
            line_item = {
                "price": application.plan.stripe_price_id,  # 事前に登録した価格IDを使用
                "quantity": 1,
            }

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[line_item],
            mode=mode,
            success_url=f"{settings.FRONTEND_URL}/trainers/success/?application_id={application.id}",
            cancel_url=f"{settings.FRONTEND_URL}/trainers/cancel/"
        )

        return Response({"checkout_url": session.url})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get("Stripe-Signature")

    if settings.DEBUG:
        payload_str = payload.decode("utf-8")  # **bytes → str に変換**
        event = json.loads(payload_str)  # **JSONパース**
    else:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            return JsonResponse({"error": str(e)}, status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        application_id = metadata.get("application_id")
        # application_id = session["metadata"]["application_id"]

        if application_id:
            application = TrainingApplication.objects.filter(id=application_id).first()
            if application:
                if application.plan.plan_type == "one_time":
                    application.status = "confirmed"
                else:
                    application.status = "active"
                    application.stripe_subscription_id = session["subscription"]
                application.save()

    if event["type"] == "invoice.payment_failed":
        sub_id = event["data"]["object"]["subscription"]
        application = TrainingApplication.objects.filter(stripe_subscription_id=sub_id).first()
        if application:
            application.status = "payment_failed"
            application.save()

    return JsonResponse({"status": "success"})

