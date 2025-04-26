from django.conf import settings
import pytz
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from dateutil.parser import parse

from accounts.utils import create_meet_event
from .models import TrainerProfile, InterviewSchedule
from .serializers import TrainerProfileSerializer
from django.core.mail import send_mail
from django.template.loader import render_to_string

class TrainerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.trainer_profile
        except TrainerProfile.DoesNotExist:
            return Response({'detail': '未登録'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TrainerProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user  # ユーザーIDをセット
        print(data)  # デバッグ用
        try:
            profile = request.user.trainer_profile
            serializer = TrainerProfileSerializer(profile, data=data)
        except TrainerProfile.DoesNotExist:
            serializer = TrainerProfileSerializer(data=data)

        if serializer.is_valid():
            serializer.save(user=request.user)  # ユーザーIDをセット
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InterviewScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        date = request.data.get('date')
        utc_dt = parse(date)
        jst = pytz.timezone('Asia/Tokyo')
        date = utc_dt.astimezone(jst).date().isoformat()
        time = request.data.get('time')

        if not date or not time:
            return Response({'detail': 'dateとtimeは必須です'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        # 同日時に他トレーナーの予約が存在するかチェック
        exists = InterviewSchedule.objects.filter(
            date=date,
            time=time,
        ).exclude(user=user).exists()

        if exists:
            return Response(
                {'detail': 'この日時はすでに予約されています。他の時間をお選びください。'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 自分の予約は update_or_create でOK
        schedule, _ = InterviewSchedule.objects.update_or_create(
            user=user,
            defaults={'date': date, 'time': time}
        )

        # Google Calendarにイベントを作成
        title = "トレーナー初回面談(" + request.user.name + "さん | " + str(request.user.id) + ")" # タイトルにユーザー名を追加
        meets_url = create_meet_event(start_date=date, start_time=time, title=title, calendar_id=settings.GOOGLE_CALENDAR_ID)  # Google Calendarにイベントを作成

        # Google MeetsのURLをメール送信
        subject = 'トレーナー面談のご予約が完了しました'
        message = render_to_string('email/account/interview_schedule.txt', {
            'user': user,
            'date': date,
            'time': time,
            'meets_url': meets_url,
        })
        html_message = render_to_string('email/account/interview_schedule.html', {
            'user': user,
            'date': date,
            'time': time,
            'meets_url': meets_url,
        })
        send_mail(subject,
                  message=message,
                  html_message=html_message,
                  from_email='info@gymdiary.tokyo',
                  recipient_list=[user.email])

        return Response({
            'message': '面談予約が完了しました',
            'date': schedule.date,
            'time': schedule.time
        }, status=status.HTTP_201_CREATED)
