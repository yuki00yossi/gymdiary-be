import boto3
from django.conf import settings

def generate_presigned_url(file_name, expiration=3600):
    """ S3の署名付きURLを発行する（有効期限: 1時間）"""
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
