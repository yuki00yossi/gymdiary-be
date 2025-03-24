from django.conf import settings


def google_analytics(request):
    """
    DEBUG=Falseの場合に、GoogleアナリティクスのトラッキングIDを返す
    """
    ga_tracking_id = getattr(settings, 'GOOGLE_ANALYTICS_TRACKING_ID', False)
    print('ga_tracking_id: ', ga_tracking_id)
    print(settings.DEBUG)
    if not settings.DEBUG and ga_tracking_id:
        print({
            'GOOGLE_ANALYTICS_TRACKING_ID': ga_tracking_id,
        })
        return {
            'GOOGLE_ANALYTICS_TRACKING_ID': ga_tracking_id,
        }
    print('not settings.DEBUG and ga_tracking_id')
    return {}
