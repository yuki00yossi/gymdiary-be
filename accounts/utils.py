import os
import boto3
import string
import secrets
from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from datetime import datetime


def generate_presigned_url(file_name, expiration=3600):
    """ S3の署名付きURLを発行する（有効期限: 1時間）"""
    if settings.DEBUG:
        return "http://localhost:8000/media/" + file_name
    else:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": "media/images/" + file_name},
            ExpiresIn=expiration  # 署名の有効期限（秒）
        )
    return url


def generate_token(length=6):
    """ 大文字アルファベットと、数字ランダム文字列を生成する """
    words = string.ascii_uppercase + string.digits
    token = ''.join(secrets.choice(words) for i in range(length))
    return token


def create_meet_event(start_date, start_time, title='', calendar_id='your_calendar_id@group.calendar.google.com'):
    """
    Google CalendarにMeet付きイベントを作成する関数
    start_date: "2025-04-13"
    start_time: "14:30"
    """

    # 🔑 サービスアカウントのJSONファイルパス
    SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, 'accounts','auth', 'google_cloud_api_credentials.json')
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    delegated_credentials = credentials.with_subject("yoshioka@studio-babe.jp")

    # Google Calendar APIクライアント
    service = build('calendar', 'v3', credentials=delegated_credentials)

    # 予約時間の設定
    # start_dt = jst.localize(datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M"))
    start_dt = datetime.strptime(start_date + ' ' + start_time, "%Y-%m-%d %H:%M")
    end_dt = start_dt + timedelta(minutes=30)

    event = {
        'summary': 'Gym Diary トレーナー面談' if not title else title,
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Tokyo'},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Tokyo'},
        'conferenceData': {
            'createRequest': {
                'requestId': f'gymdiary-{start_date}-{start_time}',
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        }
    }

    created_event = service.events().insert(
        calendarId=calendar_id,
        body=event,
        conferenceDataVersion=1
    ).execute()

    return created_event.get('hangoutLink')  # ← MeetのURLを返す！
