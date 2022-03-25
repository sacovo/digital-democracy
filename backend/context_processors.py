from django.conf import settings


def disable_comments(request):
    return {"DISABLE_COMMENTS": settings.DISABLE_COMMENTS}
